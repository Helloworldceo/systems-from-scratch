import pytest

from thread_pool import ThreadPool


def _add(a: int, b: int) -> int:
    return a + b


def _fail() -> None:
    raise ValueError("boom")


def _identity(x: int) -> int:
    return x


def test_submit_and_result():
    with ThreadPool(2) as pool:
        fut = pool.submit(_add, 2, 3)
        assert fut.result() == 5
        assert fut.done() is True
        assert fut.exception() is None


def test_multiple_workers():
    with ThreadPool(4) as pool:
        futs = [pool.submit(_add, i, i) for i in range(10)]
        results = [f.result() for f in futs]
        assert results == [i * 2 for i in range(10)]


def test_exception_propagates():
    with ThreadPool(1) as pool:
        fut = pool.submit(_fail)
        with pytest.raises(ValueError, match="boom"):
            fut.result()
        assert isinstance(fut.exception(), ValueError)


def test_map():
    with ThreadPool(2) as pool:
        results = pool.map(_add, [1, 2, 3], [10, 20, 30])
        assert results == [11, 22, 33]


def test_invalid_args():
    with pytest.raises(ValueError):
        ThreadPool(0)
    with pytest.raises(ValueError):
        ThreadPool(-1)
    with pytest.raises(ValueError):
        ThreadPool(1, max_queue_size=-1)


def test_shutdown_rejects_submit():
    pool = ThreadPool(1)
    pool.shutdown(wait=True)
    with pytest.raises(RuntimeError):
        pool.submit(_add, 1, 1)


def test_context_manager_and_order():
    with ThreadPool(3) as pool:
        results = pool.map(_identity, range(5))
        assert results == list(range(5))
