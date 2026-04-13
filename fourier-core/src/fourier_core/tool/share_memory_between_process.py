#!/usr/bin/env python3
"""
Shared-memory double-buffer FSA demo.

- Uses multiprocessing.shared_memory for two buffers per FSA.
- Uses multiprocessing.Value for front_index and per-buffer sequence counters.
- Writer: update(back) -> seq_back += 1 -> publish() (swap front_index under lock)
- Reader: read front_index, read seq_before, read data, read seq_after -> accept if equal.
"""

from __future__ import annotations
import time
import os
import math
import numpy as np
from multiprocessing import Process, Value, Lock, set_start_method
from multiprocessing import shared_memory
from typing import Tuple

# -----------------------
# Constants / Layout
# -----------------------
# FSA model fields: pos, vel, cur, tor, status, error
FSA_FIELD_COUNT = 6
DTYPE = np.float64
BYTES_PER_FIELD = np.dtype(DTYPE).itemsize
BUFFER_BYTES = FSA_FIELD_COUNT * BYTES_PER_FIELD


# -----------------------
# Shared helper classes
# -----------------------
class _SharedBufferView:
    """Wrap a SharedMemory block as a numpy vector of floats for FSA fields."""

    def __init__(self, shm: shared_memory.SharedMemory):
        self.shm = shm
        # Use ndarray view directly on the buffer
        self.arr = np.ndarray((FSA_FIELD_COUNT,), dtype=DTYPE, buffer=self.shm.buf)

    def write(self, values: Tuple[float, ...]):
        # Write in-place; values length must match FSA_FIELD_COUNT
        self.arr[:] = values

    def read_copy(self) -> Tuple[float, ...]:
        # Return a numpy copy converted to tuple to avoid exposure of buffer
        return tuple(self.arr.copy())

    def close(self):
        try:
            self.shm.close()
        except Exception:
            pass

    def unlink(self):
        try:
            self.shm.unlink()
        except Exception:
            pass


# -----------------------
# Shared Double-Buffer FSA
# -----------------------
class SharedDoubleBufferFSA:
    """
    Manage two SharedMemory buffers and per-buffer seq counters.

    allocate(name_prefix) -> returns (instance, meta)
      - instance: usable in parent process
      - meta: dict of shm names for children to attach

    attach(meta, front_index, seq0, seq1, swap_lock) -> returns instance attached in child
    """

    def __init__(self,
                 shm0: shared_memory.SharedMemory,
                 shm1: shared_memory.SharedMemory,
                 front_index: Value,
                 seq0: Value,
                 seq1: Value,
                 swap_lock: Lock,
                 name_prefix: str = ""):
        self._shm0 = shm0
        self._shm1 = shm1
        self._buf0 = _SharedBufferView(self._shm0)
        self._buf1 = _SharedBufferView(self._shm1)

        # front_index: Value('i')  -> 0 or 1, indicates which buffer is currently the front
        self.front_index = front_index

        # seq Values for each buffer, used to detect full-frame writes
        self.seq = (seq0, seq1)

        # lock used to swap front_index atomically
        self.swap_lock = swap_lock

        self.name_prefix = name_prefix

    # --------------------------
    # Factory: allocate resources (parent)
    # --------------------------
    @classmethod
    def allocate(cls, name_prefix: str):
        # create uniquely named shared memory blocks
        uniq = f"{int(time.time() * 1e6) % 1000000}_{os.getpid()}"
        name0 = f"{name_prefix}_buf0_{uniq}"
        name1 = f"{name_prefix}_buf1_{uniq}"

        shm0 = shared_memory.SharedMemory(create=True, size=BUFFER_BYTES, name=name0)
        shm1 = shared_memory.SharedMemory(create=True, size=BUFFER_BYTES, name=name1)

        # zero initialize
        np.ndarray((FSA_FIELD_COUNT,), dtype=DTYPE, buffer=shm0.buf).fill(0)
        np.ndarray((FSA_FIELD_COUNT,), dtype=DTYPE, buffer=shm1.buf).fill(0)

        # front_index and seq counters (multiprocessing.Value are process-shared)
        front_index = Value('i', 0, lock=False)  # 0 or 1
        seq0 = Value('l', 0, lock=False)  # should be incremented by writer when write completes
        seq1 = Value('l', 0, lock=False)

        swap_lock = Lock()

        inst = cls(shm0, shm1, front_index, seq0, seq1, swap_lock, name_prefix=name_prefix)

        # meta contains names so other processes can attach
        meta = {
            'shm_name0': name0,
            'shm_name1': name1,
        }

        return inst, meta, front_index, (seq0, seq1), swap_lock

    # --------------------------
    # Attach (child process)
    # --------------------------
    @classmethod
    def attach(cls, meta, front_index: Value, seqs: Tuple[Value, Value], swap_lock: Lock, name_prefix: str = ""):
        shm0 = shared_memory.SharedMemory(name=meta['shm_name0'])
        shm1 = shared_memory.SharedMemory(name=meta['shm_name1'])
        seq0, seq1 = seqs
        return cls(shm0, shm1, front_index, seq0, seq1, swap_lock, name_prefix=name_prefix)

    # --------------------------
    # Internal helpers
    # --------------------------
    def _get_buf_by_index(self, idx: int) -> _SharedBufferView:
        return self._buf0 if idx == 0 else self._buf1

    # --------------------------
    # Writer API (single writer assumed)
    # --------------------------
    def update_back(self, position=None, velocity=None, current=None, torque=None, status=None, error=None):
        """
        Write data into back buffer (no swap). After this, caller SHOULD call publish().
        If you want to update partially, it's OK but you must ensure you call publish() after finishing.
        """
        back_idx = 1 - int(self.front_index.value)
        buf = self._get_buf_by_index(back_idx)

        # prepare values: order [pos, vel, cur, tor, status, error]
        # Use 0.0 for None fields to keep deterministic layout (or you can keep old values - choose policy)
        # We'll read old values then overwrite only updated fields to preserve other fields if not provided.
        cur_values = list(buf.arr.copy())

        if position is not None:
            cur_values[0] = float(position)
        if velocity is not None:
            cur_values[1] = float(velocity)
        if current is not None:
            cur_values[2] = float(current)
        if torque is not None:
            cur_values[3] = float(torque)
        if status is not None:
            cur_values[4] = float(status)
        if error is not None:
            cur_values[5] = float(error)

        # write into back buffer
        buf.write(tuple(cur_values))

        # mark back buffer as completed by incrementing seq (writer-only)
        # increment by 1 (monotonic)
        self.seq[back_idx].value = int(self.seq[back_idx].value) + 1

    def publish(self):
        """
        Atomically make back buffer the front buffer.
        Writer should call publish() after update_back().
        """
        with self.swap_lock:
            back_idx = 1 - int(self.front_index.value)
            # swap front_index to back
            self.front_index.value = back_idx

    # --------------------------
    # Reader API
    # --------------------------
    def get_all(self, retries: int = 3):
        """
        Read a consistent snapshot of the current front buffer.
        Uses seq compare before/after to ensure consistency. Retries up to `retries`.
        Returns tuple: (pos, vel, cur, tor, status, error) or raises RuntimeError if unstable.
        """
        for _ in range(retries):
            idx = int(self.front_index.value)  # read which buffer is front
            seq_before = int(self.seq[idx].value)
            # read data copy
            buf = self._get_buf_by_index(idx)
            data = buf.read_copy()
            seq_after = int(self.seq[idx].value)
            if seq_before == seq_after:
                # data consistent
                # Convert status & error to int if they were stored as floats
                pos, vel, cur, tor, status_f, error_f = data
                try:
                    status = int(status_f)
                    error = int(error_f)
                except Exception:
                    status = int(status_f)
                    error = int(error_f)
                return (float(pos), float(vel), float(cur), float(tor), status, error)
            # else retry
        # final attempt: return last read but warn
        raise RuntimeError("Failed to read consistent FSA frame after retries")

    # --------------------------
    # Cleanup
    # --------------------------
    def close(self):
        try:
            self._buf0.close()
        except Exception:
            pass
        try:
            self._buf1.close()
        except Exception:
            pass

    def unlink(self):
        try:
            self._buf0.unlink()
        except Exception:
            pass
        try:
            self._buf1.unlink()
        except Exception:
            pass


# -----------------------
# Demo writer and reader processes
# -----------------------
def writer_process(meta, front_index, seqs, swap_lock, name_prefix):
    # attach to shared resources in child
    fsa = SharedDoubleBufferFSA.attach(meta=meta, front_index=front_index, seqs=seqs, swap_lock=swap_lock, name_prefix=name_prefix)
    print("[writer] attached, pid:", os.getpid())
    # simulate writing frames
    for i in range(1, 11):
        p = i * 1.0
        v = i * 2.0
        c = i * 3.0
        t = i * 4.0
        status = i
        error = i % 2
        # write into back then publish
        fsa.update_back(position=p, velocity=v, current=c, torque=t, status=status, error=error)
        fsa.publish()
        # sleep a bit
        time.sleep(0.08)
    fsa.close()
    print("[writer] done")


def reader_process(meta, front_index, seqs, swap_lock, name_prefix):
    fsa = SharedDoubleBufferFSA.attach(meta=meta, front_index=front_index, seqs=seqs, swap_lock=swap_lock, name_prefix=name_prefix)
    print("[reader] attached, pid:", os.getpid())
    # try to read 12 frames
    for _ in range(12):
        try:
            pos, vel, cur, tor, status, error = fsa.get_all(retries=5)
            print(f"[reader] read pos={pos}, vel={vel}, cur={cur}, tor={tor}, status={status}, error={error}")
        except RuntimeError as e:
            print("[reader] unstable read:", e)
        time.sleep(0.05)
    fsa.close()
    print("[reader] done")


# -----------------------
# Run demo
# -----------------------
if __name__ == "__main__":
    # Use spawn on platforms where fork isn't default (Windows), also safe for portability
    try:
        set_start_method("spawn")
    except RuntimeError:
        # already set
        pass

    name_prefix = "demo_fsa"
    inst, meta, front_idx, seqs, swap_lock = SharedDoubleBufferFSA.allocate(name_prefix=name_prefix)

    print("Allocated shared buffers:", meta)
    print("Parent pid:", os.getpid())

    # spawn writer and reader processes, passing the same Value/Lock objects
    writer = Process(target=writer_process, args=(meta, front_idx, seqs, swap_lock, name_prefix))
    reader = Process(target=reader_process, args=(meta, front_idx, seqs, swap_lock, name_prefix))

    writer.start()
    reader.start()

    writer.join()
    reader.join()

    # cleanup in parent
    inst.close()
    inst.unlink()
    print("Parent done, cleaned up shared memory.")
