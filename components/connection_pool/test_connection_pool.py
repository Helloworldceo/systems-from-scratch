import pytest

from connection_pool import ConnectionPool, PoolTimeout


class FakeConn:
    def __init__(self, n):
        self.n = n
        self.closed = False

    def close(self):
        self.closed = True


def make_factory():
    counter = 0

    def factory():
        nonlocal counter
        counter += 1
        return FakeConn(counter)

    return factory


def test_acquire_and_release_reuses():
    pool = ConnectionPool(make_factory(), max_size=2)
    c1 = pool.acquire()
    pool.release(c1)
    c2 = pool.acquire()
    assert c1 is c2
    assert pool.total == 1
    assert pool.idle == 0
    pool.release(c2)
    assert pool.idle == 1


def test_creates_up_to_max_then_times_out():
    pool = ConnectionPool(make_factory(), max_size=2)
    a = pool.acquire()
    b = pool.acquire()
    assert pool.total == 2
    with pytest.raises(PoolTimeout):
        pool.acquire(timeout=0)
    pool.release(a)
    c = pool.acquire(timeout=0)
    assert c is a
    pool.release(b)
    pool.release(c)


def test_context_manager():
    pool = ConnectionPool(make_factory(), max_size=1)
    with pool.connection() as conn:
        assert isinstance(conn, FakeConn)
        assert len(pool) == 1
    assert len(pool) == 0
    assert pool.idle == 1


def test_invalid_args():
    with pytest.raises(ValueError):
        ConnectionPool(make_factory(), 0)
    with pytest.raises(TypeError):
        ConnectionPool("not-callable", 1)


def test_release_without_acquire():
    pool = ConnectionPool(make_factory(), max_size=1)
    with pytest.raises(RuntimeError):
        pool.release(FakeConn(0))


def test_close_discards_idle():
    pool = ConnectionPool(make_factory(), max_size=2)
    c = pool.acquire()
    pool.release(c)
    assert pool.idle == 1
    pool.close()
    assert pool.idle == 0
    assert pool.total == 0
