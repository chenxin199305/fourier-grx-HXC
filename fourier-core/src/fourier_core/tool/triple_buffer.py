"""
Triple-buffer framework for high-real-time usage in Python
Supports both multi-thread (in-process) and multi-process (shared memory) scenarios.

Features
- Triple buffer: front / middle / back indices to ensure writer never overwrites a buffer readers may be using.
- For multi-process usage, uses multiprocessing.shared_memory to store NumPy arrays in shared memory.
- Uses a small sequence counter (seqlock-style) to allow readers to detect in-progress swaps and retry.
- Minimal locking: the critical section only wraps the sequence counter and pointer swap.
- API: writer_back_buffer(), publish(), get_snapshot(copy=True), close()

Notes & tradeoffs
- Readers may retry if a publish is in progress; retries are typically very short.
- Writer must write into the provided back buffers in-place (no reallocation).
- All buffers are preallocated to avoid runtime allocation and GC pauses.

Example usage:
- For in-process (threads) use TripleBuffer.allocate(spec)
- For inter-process use TripleBufferSharedMemory.allocate(spec, name_prefix)

"""

from __future__ import annotations

import ctypes
import math
import threading
import time

import numpy as np
import multiprocessing as mp

from typing import Dict, Tuple
from multiprocessing import Process, Value, Lock
from multiprocessing.shared_memory import SharedMemory


# ---------------------------
# Helper utilities
# ---------------------------

def _nbytes_for_shape(shape: Tuple[int, ...], dtype: np.dtype) -> int:
    return int(np.prod(shape)) * np.dtype(dtype).itemsize


# ---------------------------
# In-process triple buffer
# ---------------------------
class TripleBuffer:
    """Simple triple-buffer for multi-thread use. All buffers are numpy arrays in-process.

    - buffers: list of 3 dicts mapping name->ndarray
    - _front_index: which buffer is published (0..2)
    - _swap_lock: threading.Lock to protect swap
    - _seq: small integer used for seqlock-like detection in readers
    """

    def __init__(self, buffers: Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray], Dict[str, np.ndarray]]):
        keys = set(buffers[0].keys())
        if not (keys == set(buffers[1].keys()) == set(buffers[2].keys())):
            raise ValueError("All three buffers must share the same keys")
        # validate shapes/dtypes
        for k in keys:
            a, b, c = buffers[0][k], buffers[1][k], buffers[2][k]
            if a.shape != b.shape or a.dtype != b.dtype or a.shape != c.shape or a.dtype != c.dtype:
                raise ValueError("All buffers for key %s must have same shape and dtype" % k)

        self._buffers = list(buffers)
        self._front_index = 0
        self._swap_lock = threading.Lock()
        # sequence counter for readers to detect swaps (int)
        self._seq = 0

    @classmethod
    def allocate(cls, spec: Dict[str, Tuple[Tuple[int, ...], np.dtype]]):
        b0 = {k: np.zeros(shape, dtype=dtype) for k, (shape, dtype) in spec.items()}
        b1 = {k: np.zeros(shape, dtype=dtype) for k, (shape, dtype) in spec.items()}
        b2 = {k: np.zeros(shape, dtype=dtype) for k, (shape, dtype) in spec.items()}
        return cls((b0, b1, b2))

    # ------------------------
    # Writer-side API
    # ------------------------
    def _back_index(self) -> int:
        # choose the buffer not equal to front and not equal to middle (we'll compute middle as any other)
        # simpler: pick (front + 2) % 3 as back - ensures rotation
        return (self._front_index + 2) % 3

    def get_back_buffer(self) -> Dict[str, np.ndarray]:
        return self._buffers[self._back_index()]

    def publish(self) -> None:
        """Make back become front using a tiny critical section protected by _swap_lock.
        We use a sequence counter to let readers detect an in-progress swap.
        """
        with self._swap_lock:
            # mark odd
            self._seq += 1
            self._front_index = self._back_index()
            # mark even
            self._seq += 1

    # ------------------------
    # Reader-side API
    # ------------------------
    def get_front_buffer(self, copy: bool = True, retries: int = 3) -> Dict[str, np.ndarray]:
        """Get consistent snapshot from current front buffer. If a swap occurs while reading, retry.

        copy=True returns copies (safe). copy=False returns references (read-only recommended).
        """
        for _ in range(retries):
            seq1 = self._seq
            idx = self._front_index
            front = self._buffers[idx]
            if copy:
                data = {k: v.copy() for k, v in front.items()}
            else:
                data = front
            seq2 = self._seq
            if seq1 == seq2 and (seq1 % 2 == 0):
                return data
            # else retry
        # last attempt: return copies to be safe
        return {k: v.copy() for k, v in self._buffers[self._front_index].items()}


# ---------------------------
# Multi-process triple buffer using shared_memory
# ---------------------------
class TripleBufferSharedMemory:
    """
    Triple buffer where each field has 3 SharedMemory blocks backing numpy arrays.

    Allocation strategy:
      For each name: allocate 3 SharedMemory segments (one per buffer).
      Maintain a Value('i') front_index and a Value('i') seq counter (both in multiprocessing) and a Lock for swap.

    API mirrors TripleBuffer.
    """

    def __init__(
            self,
            spec: Dict[str, Tuple[Tuple[int, ...], np.dtype]],
            shms: Dict[str, Tuple[SharedMemory, SharedMemory, SharedMemory]],
            front_index: Value,
            seq: Value,
            swap_lock: Lock,
    ):
        self._spec = spec
        self._shms = shms  # name -> (shm0, shm1, shm2)
        self._front_index = front_index
        self._seq = seq
        self._swap_lock = swap_lock

        # create numpy views for each buffer
        self._buf_views = []  # list of 3 dicts
        for b in range(3):
            d = {}
            for name, (shape, dtype) in spec.items():
                shm = shms[name][b]
                # create ndarray using buffer interface
                arr = np.ndarray(shape, dtype=dtype, buffer=shm.buf)
                d[name] = arr
            self._buf_views.append(d)

    @classmethod
    def allocate(cls, spec: Dict[str, Tuple[Tuple[int, ...], np.dtype]], name_prefix: str):
        """Allocate shared memory blocks for all fields and three buffers.

        name_prefix: used to uniquely name SharedMemory blocks (should be unique across process runs)
        Returns an instance and also returns a 'meta' dict with names so other processes can attach.
        """
        shms = {}
        meta = {}
        for name, (shape, dtype) in spec.items():
            nbytes = _nbytes_for_shape(shape, np.dtype(dtype))
            blocks = []
            block_names = []
            for i in range(3):
                shm_name = f"{name_prefix}_{name}_{i}_{int(time.time() * 1e6) % 1000000}"
                shm = SharedMemory(create=True, size=nbytes, name=shm_name)
                # zero-init
                buf = np.ndarray(shape, dtype=dtype, buffer=shm.buf)
                buf.fill(0)
                blocks.append(shm)
                block_names.append(shm_name)
            shms[name] = tuple(blocks)
            meta[name] = tuple(block_names)

        # front index and seq
        front_index = Value('i', 0, lock=False)
        seq = Value('i', 0, lock=False)
        swap_lock = Lock()

        instance = cls(spec, shms, front_index, seq, swap_lock)

        # also return meta so other processes can attach by name
        return instance, {'shared_names': meta}

    @classmethod
    def attach(
            cls,
            spec: Dict[str, Tuple[Tuple[int, ...], np.dtype]],
            meta: Dict,
            front_index: Value,
            seq: Value,
            swap_lock: Lock,
    ):
        """Attach to existing shared memory blocks using meta dict which should contain names per (name, i).

        Because multiprocessing.Value/Lock are not shareable by name across independent processes easily without a
        multiprocessing.Manager, we expect the caller to pass in front_index, seq, and swap_lock objects created via a
        multiprocessing.Manager or inherited through fork/Process.
        """
        shms = {}
        for name, (shape, dtype) in spec.items():
            names = meta['shared_names'][name]
            blocks = tuple(SharedMemory(name=n) for n in names)
            shms[name] = blocks
        return cls(spec, shms, front_index, seq, swap_lock)

    # ------------------------
    # Writer-side API
    # ------------------------
    def _back_index(self) -> int:
        return (self._front_index.value + 2) % 3

    def get_back_buffer(self) -> Dict[str, np.ndarray]:
        return self._buf_views[self._back_index()]

    def publish(self) -> None:
        """Atomically swap back->front with minimal lock.
        seq: odd -> swap -> even.
        """
        with self._swap_lock:
            self._seq.value += 1
            self._front_index.value = self._back_index()
            self._seq.value += 1

    # ------------------------
    # Reader-side API
    # ------------------------
    def get_front_buffer(self, copy: bool = True, retries: int = 5) -> Dict[str, np.ndarray]:
        for _ in range(retries):
            s1 = int(self._seq.value)
            idx = int(self._front_index.value)
            front = self._buf_views[idx]

            if copy:
                data = {k: v.copy() for k, v in front.items()}
            else:
                data = front

            s2 = int(self._seq.value)
            if s1 == s2 and (s1 % 2 == 0):
                return data
            # else retry
        # Last resort: return a copy of current front
        return {k: v.copy() for k, v in self._buf_views[int(self._front_index.value)].items()}

    # ------------------------
    # Cleanup
    # ------------------------
    def close(self) -> None:
        """Close all SharedMemory blocks. Caller should also unlink them when appropriate.
        """
        for name, blocks in self._shms.items():
            for shm in blocks:
                try:
                    shm.close()
                except Exception:
                    pass

    def unlink(self) -> None:
        for name, blocks in self._shms.items():
            for shm in blocks:
                try:
                    shm.unlink()
                except Exception:
                    pass


# -------------------------
# Example: using TripleBufferState in a 1 kHz control loop
# -------------------------

def example_usage_tb():
    # Example spec
    spec = {
        'imu_quat': ((4,), np.float32),
        'imu_euler_angle': ((3,), np.float32),
        'imu_angular_velocity': ((3,), np.float32),
        'imu_acceleration': ((3,), np.float32),
        'joint_position': ((12,), np.float32),
        'joint_velocity': ((12,), np.float32),
        'joint_effort': ((12,), np.float32),
        'joint_current': ((12,), np.float32),
    }

    # In-process example
    tb = TripleBuffer.allocate(spec)

    stop_event = threading.Event()

    def writer_thread(tb: TripleBuffer):
        period = 0.001  # 1 ms -> 1 kHz
        next_time = time.perf_counter()
        back = tb.get_back_buffer()

        while not stop_event.is_set():
            # wait until next period (simple busy-wait / sleep strategy)
            next_time += period
            now = time.perf_counter()
            sleep_time = next_time - now
            if sleep_time > 0:
                # use sleep for longer intervals
                time.sleep(sleep_time)

            # --- begin write to back buffer (writer real-time path) ---
            back['imu_quat'][:] = np.random.rand(4)
            back['joint_position'][:] = np.random.rand(12)

            # finished writing to back -> publish
            tb.publish()
            # --- end write ---

    def reader_thread(tb: TripleBuffer):
        period = 0.001  # 1 ms -> 1 kHz
        next_time = time.perf_counter()
        
        while not stop_event.is_set():
            # wait until next period (simple busy-wait / sleep strategy)
            next_time += period
            now = time.perf_counter()
            sleep_time = next_time - now
            if sleep_time > 0:
                # use sleep for longer intervals
                time.sleep(sleep_time)

            # Get most recent snapshot. For low-latency, you can use copy=False but treat returned arrays as read-only.
            snap = tb.get_front_buffer(copy=True)

            # Process snapshot (read-only)
            # For demonstration, we copy here to avoid race if you want to mutate
            imu_quat = snap['imu_quat'].copy()

            # do some non-real-time processing...

    wt = threading.Thread(target=writer_thread, args=(tb,), daemon=True)
    rt = threading.Thread(target=reader_thread, args=(tb,), daemon=True)
    wt.start()
    rt.start()

    try:
        time.sleep(0.5)
    finally:
        stop_event.set()
        wt.join()
        rt.join()


# ---------------------------
# Small example (in-process + multi-process notes)
# ---------------------------
if __name__ == "__main__":
    example_usage_tb()
