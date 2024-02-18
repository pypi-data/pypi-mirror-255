"""
"""

from multiprocessing.synchronize import RLock as MultiprocessingRLock


def remove_tqdm_multiprocessing_lock():
    from tqdm import tqdm
    tqdm_lock = tqdm.get_lock()
    assert tqdm_lock.__class__.__name__ == 'TqdmDefaultWriteLock'
    tqdm_lock.locks = [
        lock for lock in tqdm_lock.locks
        if not isinstance(lock, MultiprocessingRLock)
    ]
