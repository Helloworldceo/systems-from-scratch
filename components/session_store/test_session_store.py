import pytest

from session_store import SessionStore


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t

    def advance(self, s):
        self.t += s


def test_create_and_get():
    store = SessionStore(default_ttl=60, clock=FakeClock())
    sid = store.create({"user": "alice"})
    assert store.get(sid) == {"user": "alice"}
    assert store.get("missing") is None
    assert store.get("missing", 0) == 0
    assert sid in store


def test_expires_after_ttl():
    clk = FakeClock()
    store = SessionStore(default_ttl=10, clock=clk)
    sid = store.create("data")
    clk.advance(9.9)
    assert store.get(sid) == "data"
    clk.advance(0.2)
    assert store.get(sid) is None
    assert sid not in store
    assert len(store) == 0


def test_custom_ttl_and_renew():
    clk = FakeClock()
    store = SessionStore(default_ttl=5, clock=clk)
    sid = store.create("v", ttl=20)
    clk.advance(15)
    assert store.get(sid) == "v"
    assert store.renew(sid, ttl=30)
    clk.advance(25)
    assert store.get(sid) == "v"
    clk.advance(10)
    assert store.get(sid) is None
    assert store.renew(sid) is False


def test_set_overwrite_and_delete():
    store = SessionStore(default_ttl=100, clock=FakeClock())
    store.set("k1", 1)
    store.set("k1", 2, ttl=50)
    assert store.get("k1") == 2
    assert store.delete("k1") is True
    assert store.delete("k1") is False
    assert store.get("k1") is None


def test_cleanup_removes_expired():
    clk = FakeClock()
    store = SessionStore(default_ttl=10, clock=clk)
    store.create("a")
    store.create("b", ttl=30)
    clk.advance(15)
    assert store.cleanup() == 1
    assert len(store) == 1
    clk.advance(20)
    assert store.cleanup() == 1
    assert len(store) == 0


def test_invalid_args():
    with pytest.raises(ValueError):
        SessionStore(default_ttl=0)
    store = SessionStore(default_ttl=10, clock=FakeClock())
    with pytest.raises(ValueError):
        store.create("v", ttl=-1)
    with pytest.raises(ValueError):
        store.set("k", "v", ttl=0)
    with pytest.raises(ValueError):
        store.renew("missing", ttl=-5)


def test_duplicate_key_raises():
    clk = FakeClock()
    store = SessionStore(default_ttl=10, clock=clk)
    store.create("first", key="fixed")
    with pytest.raises(ValueError, match="already exists"):
        store.create("second", key="fixed")
    # expired key can be reused
    clk.advance(11)
    store.create("again", key="fixed")  # should succeed
    assert store.get("fixed") == "again"
