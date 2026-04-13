"""
Double-buffered shared state for real-time control loops (1 kHz)

Design goals:
- Writer (control loop) can update state at 1 kHz with minimal blocking.
- Readers can get a consistent snapshot of the most recent completed state.
- Minimize locking: only a tiny critical section to flip the index.
- Support optionally returning copies (safe) or returning a read-only view (fast).

Usage:
- Create DoubleBuffer with factory function that allocates numpy arrays for each field.
- Writer calls .write_update(updater) where `updater(back_buffers)` writes into provided back buffer arrays.
- Writer calls .publish() to atomically make the back buffer the front buffer.
- Reader calls .get_snapshot(copy=True) to get a dict of numpy arrays. If copy=False it returns references to the currently front buffers (read-only recommended).

Notes on real-time:
- The only locked section is the publish() swap and a tiny index read in get_snapshot(); these are extremely short.
- Avoid heavy copies in the real-time writer path. Prefer writer writing directly to the back buffer then calling publish().
- If you want absolutely lock-free reads, you must ensure the platform memory model provides the necessary atomicity; here we rely on Python's atomic assignment for the index and a tiny lock to be robust.

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
# In-process double buffer
# ---------------------------
class DoubleBuffer:
    """Double-buffered container for multiple numpy arrays.

    Internals:
    - buffers: list of two dicts, each dict maps name -> numpy array
    - _front_index: int, 0 or 1, indicates which buffer is currently published/readable
    - _swap_lock: threading.Lock used only to guard the pointer swap

    Guarantees:
    - Writer writes to back buffer (1 - front). After finishing, writer calls publish() to atomically switch which buffer is front.
    - Readers calling get_snapshot(copy=False) will get references to the front buffer arrays. They must treat them as read-only
      (do not modify). If copy=True, a deep copy of each array is returned.

    Performance:
    - publish() holds the lock for only a few CPU instructions (index swap). This is suitable for 1 kHz loops on typical hardware.
    """

    def __init__(self, buffer0: Dict[str, np.ndarray], buffer1: Dict[str, np.ndarray]):
        # Validate shapes and dtypes
        if set(buffer0.keys()) != set(buffer1.keys()):
            raise ValueError("Both buffers must have the same keys")

        for k in buffer0.keys():
            a = buffer0[k]
            b = buffer1[k]
            if a.shape != b.shape or a.dtype != b.dtype:
                raise ValueError(f"Buffer field '{k}' must have same shape/dtype in both buffers")

        self._buffers = [buffer0, buffer1]
        self._front_index = 0
        self._swap_lock = threading.Lock()

        # A small lock to protect reads of _front_index if you want extra safety. Not strictly required when we only read it,
        # but using it removes ambiguous interleavings and keeps things explicit.
        self._index_lock = threading.Lock()

    @classmethod
    def allocate(cls, spec: Dict[str, Tuple[Tuple[int, ...], np.dtype]]):
        """Allocate two underlying numpy buffers according to spec.

        spec: dict mapping name -> (shape tuple, dtype)
        Example: {
            'imu_quat': ((4,), np.float32),
            'joint_position': ((12,), np.float32),
        }
        """
        b0 = {k: np.zeros(shape, dtype=dtype) for k, (shape, dtype) in spec.items()}
        b1 = {k: np.zeros(shape, dtype=dtype) for k, (shape, dtype) in spec.items()}
        return cls(b0, b1)

    # ------------------------
    # Writer-side API
    # ------------------------
    def _back_index(self) -> int:
        # back = 1 - front
        return 1 - self._front_index

    def get_back_buffer(self) -> Dict[str, np.ndarray]:
        """Return references to the back buffers for the writer to update.

        Writer MUST write entirely into these arrays (no resizing) and then call publish().
        """
        return self._buffers[self._back_index()]

    def publish(self) -> None:
        """Atomically make the back buffer the front buffer.

        This should be called by the writer AFTER finishing writing to back buffers.
        The lock here is extremely short-lived.
        """
        with self._swap_lock:
            # Swap front index
            self._front_index = self._back_index()

    # ------------------------
    # Reader-side API
    # ------------------------
    def get_front_buffer(self, copy: bool = True) -> Dict[str, np.ndarray]:
        """Get a consistent snapshot of the current published (front) buffer.

        If copy=True returns deep copies of arrays (safe). If copy=False returns references to the arrays (fast) - treat as read-only.
        """
        # Small critical section to capture current front index
        with self._index_lock:
            idx = self._front_index

        front = self._buffers[idx]

        if copy:
            return {k: v.copy() for k, v in front.items()}
        else:
            # Caller must NOT mutate these arrays
            return front


# ---------------------------
# Multi-process double buffer using shared_memory
# ---------------------------
class DoubleBufferSharedMemory:
    """
    Double-buffer where each field has 2 SharedMemory blocks (front/back).
    front_index: Value('i') either 0 or 1
    seq: Value('i') seqlock-style counter (even=stable, odd=in-swap)
    swap_lock: process-safe lock
    """

    def __init__(self, spec, shms, front_index, seq, swap_lock):
        self._spec = spec  # name -> (shape, dtype)
        self._shms = shms  # name -> (shm0, shm1)
        self._front_index = front_index  # Value('i')
        self._seq = seq  # Value('i')
        self._swap_lock = swap_lock  # Lock

        # Create numpy views for buffer 0 and 1
        self._buf_views = []  # list of 2 dicts
        for b in range(2):
            d = {}
            for name, (shape, dtype) in spec.items():
                shm = shms[name][b]
                arr = np.ndarray(shape, dtype=dtype, buffer=shm.buf)
                d[name] = arr
            self._buf_views.append(d)

    @classmethod
    def allocate(cls, spec: Dict[str, Tuple[Tuple[int, ...], np.dtype]], name_prefix: str):
        """Allocate two shared-memory blocks per field.
        Returns (instance, meta).
        meta contains shm names so other processes can attach.
        """
        shms = {}
        meta = {}
        for name, (shape, dtype) in spec.items():
            nbytes = _nbytes_for_shape(shape, dtype)
            blocks = []
            block_names = []
            for i in range(2):
                shm_name = f"{name_prefix}_{name}_{i}_{int(time.time() * 1e6) % 1000000}"
                shm = SharedMemory(create=True, size=nbytes, name=shm_name)
                # zero-init
                arr = np.ndarray(shape, dtype=dtype, buffer=shm.buf)
                arr.fill(0)
                blocks.append(shm)
                block_names.append(shm_name)
            shms[name] = tuple(blocks)
            meta[name] = tuple(block_names)

        # process-shared states
        front_index = Value('i', 0, lock=False)
        seq = Value('i', 0, lock=False)
        swap_lock = Lock()

        instance = cls(spec, shms, front_index, seq, swap_lock)

        # also return meta so other processes can attach by name
        return instance, {"shared_names": meta}

    @classmethod
    def attach(
            cls,
            spec: Dict[str, Tuple[Tuple[int, ...], np.dtype]],
            meta: Dict,
            front_index: Value,
            seq: Value,
            swap_lock: Lock,
    ):
        """Attach by names from meta['shared_names'].
        front_index, seq, and swap_lock must be shared (e.g., via multiprocessing.Manager or fork).
        """
        shms = {}
        for name, (shape, dtype) in spec.items():
            block_names = meta['shared_names'][name]
            blocks = tuple(SharedMemory(name=n) for n in block_names)
            shms[name] = blocks
        return cls(spec, shms, front_index, seq, swap_lock)

    # ------------------------
    # Writer-side API
    # ------------------------
    def _back_index(self) -> int:
        return 1 - int(self._front_index.value)

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
    def close(self):
        for blocks in self._shms.values():
            for shm in blocks:
                try:
                    shm.close()
                except Exception:
                    pass

    def unlink(self):
        for blocks in self._shms.values():
            for shm in blocks:
                try:
                    shm.unlink()
                except Exception:
                    pass


# -------------------------
# Example: using DoubleBuffer in a 1 kHz control loop
# -------------------------
def example_usage_db():
    # Define the fields and shapes you need
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

    db = DoubleBuffer.allocate(spec)

    stop_event = threading.Event()

    def writer_thread(db: DoubleBuffer):
        period = 0.001  # 1 ms -> 1 kHz
        next_time = time.perf_counter()
        back = db.get_back_buffer()

        while not stop_event.is_set():
            # wait until next period (simple busy-wait / sleep strategy)
            next_time += period
            now = time.perf_counter()
            sleep_time = next_time - now
            if sleep_time > 0:
                # use sleep for longer intervals
                time.sleep(sleep_time)

            # --- begin write to back buffer (writer real-time path) ---
            # Simulate sensor reads and fill back arrays. Do NOT allocate new arrays here.
            # Example writes (replace with real sensor reads):
            back['imu_quat'][0] += 0.001  # mutate existing array in-place
            back['imu_quat'][1:] = 0.0

            # joint positions simulated
            back['joint_position'] += 0.01

            # finished writing to back -> publish
            db.publish()
            # --- end write ---

    def reader_thread(db: DoubleBuffer):
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
            snap = db.get_front_buffer(copy=False)

            # Process snapshot (read-only)
            # For demonstration, we copy here to avoid race if you want to mutate
            imu_quat = snap['imu_quat'].copy()

            # do some non-real-time processing...

    wt = threading.Thread(target=writer_thread, args=(db,), daemon=True)
    rt = threading.Thread(target=reader_thread, args=(db,), daemon=True)
    wt.start()
    rt.start()

    try:
        time.sleep(0.5)
    finally:
        stop_event.set()
        wt.join()
        rt.join()


# -------------------------
# Example: using DoubleBufferSharedMemory in a 1 kHz control loop
# -------------------------
def writer_process(spec, meta, front_index, seq, swap_lock):
    print("[Writer] Attaching...")
    db = DoubleBufferSharedMemory.attach(
        spec=spec,
        meta=meta,
        front_index=front_index,
        seq=seq,
        swap_lock=swap_lock,
    )

    # Writer loop: simulate 1kHz control loop (write → publish)
    print("[Writer] Running...")
    for i in range(50):
        back = db.get_back_buffer()
        back["imu_quat"][:] = np.random.rand(4)
        back["joint_position"][:] = np.random.rand(12)

        db.publish()
        time.sleep(0.001)  # 1kHz

    print("[Writer] Done.")


def reader_process(spec, meta, front_index, seq, swap_lock):
    print("[Reader] Attaching...")
    db = DoubleBufferSharedMemory.attach(
        spec=spec,
        meta=meta,
        front_index=front_index,
        seq=seq,
        swap_lock=swap_lock,
    )

    print("[Reader] Reading snapshots...")
    for i in range(20):
        snap = db.get_front_buffer(copy=True)
        print(f"[Reader] Snapshot {i}: imu_quat={snap['imu_quat']}, "
              f"joint_pos[0]={snap['joint_position'][0]}")
        time.sleep(0.005)  # slower reader

    print("[Reader] Done.")


def example_usage_dbsm():
    mp.set_start_method("spawn")  # important for cross-platform compatibility

    # Define shared arrays (your robot data can be put here)
    spec = {
        "imu_quat": ((4,), np.float32),
        "joint_position": ((12,), np.float32),
    }

    # Allocate double buffer shared memory
    db, meta = DoubleBufferSharedMemory.allocate(spec, name_prefix="demo_db")

    # The controlling shared objects must be passed to child processes
    front_index = db._front_index
    seq = db._seq
    swap_lock = db._swap_lock

    # Spawn writer / reader processes
    writer = Process(target=writer_process, args=(spec, meta, front_index, seq, swap_lock))
    reader = Process(target=reader_process, args=(spec, meta, front_index, seq, swap_lock))

    writer.start()
    reader.start()

    writer.join()
    reader.join()

    print("[Main] Cleaning up shared memory.")
    db.close()
    db.unlink()

    print("[Main] Done.")


if __name__ == '__main__':
    example_usage_db()
