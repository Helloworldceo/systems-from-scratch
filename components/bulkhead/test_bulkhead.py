import threading
import pytest

from bulkhead import Bulkhead, BulkheadFull


def test_basic_acquire_release():
    bh = Bulkhead(2)
    assert bh.try_acquire()
    assert bh.try_acquire()
    assert not bh.try_acquire()
    assert bh.in_flight == 2
    assert bh.available == 0
    bh.release()
    assert bh.try_acquire()
    assert bh.admitted == 3
    assert bh.rejected == 1


def test_context_manager_rejects_when_full():
    bh = Bulkhead(1)
    with bh:
        with pytest.raises(BulkheadFull):
            with bh:
                pass
    # After exit, slot is free again
    with bh:
        assert bh.in_flight == 1


def test_slot_context_with_timeout_zero():
    bh = Bulkhead(1)
    with bh.slot(timeout=0):
        with pytest.raises(BulkheadFull):
            with bh.slot(timeout=0):
                pass
    assert bh.rejected >= 1


def test_concurrent_limit_enforced():
    bh = Bulkhead(3)
    attempted = threading.Event()
    release_all = threading.Event()
    results = []
    lock = threading.Lock()
    count = [0]

    def worker():
        acquired = bh.try_acquire()
        with lock:
            results.append(acquired)
            count[0] += 1
            if count[0] == 5:
                attempted.set()
        if acquired:
            release_all.wait(timeout=2.0)
            bh.release()

    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads:
        t.start()
    assert attempted.wait(timeout=2.0)
    release_all.set()
    for t in threads:
        t.join(timeout=2.0)

    admitted = results.count(True)
    rejected = results.count(False)
    assert admitted <= 3
    assert admitted + rejected == 5
    assert bh.in_flight == 0


def test_invalid_max_concurrent():
    with pytest.raises(ValueError):
        Bulkhead(0)
    with pytest.raises(ValueError):
        Bulkhead(-1)


def test_release_without_acquire_raises():
    bh = Bulkhead(1)
    with pytest.raises(RuntimeError):
        bh.release()


def test_stats_and_available():
    bh = Bulkhead(max_concurrent=2, name="db")
    assert bh.available == 2
    assert bh.try_acquire()
    assert bh.available == 1
    assert bh.admitted == 1
    bh.release()
    assert bh.available == 2
    assert bh.name == "db"
