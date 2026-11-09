import pytest

from lfu_cache import LFUCache


def test_get_put_basic():
    c = LFUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    assert c.get("a") == 1
    assert c.get("missing") is None
    assert c.get("missing", 0) == 0


def test_evicts_least_frequently_used():
    c = LFUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.get("a")          # a freq=2, b freq=1
    c.put("c", 3)       # evicts b (lowest freq)
    assert "b" not in c
    assert c.get("a") == 1
    assert c.get("c") == 3


def test_update_increments_freq_without_growing():
    c = LFUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.put("a", 10)      # still capacity 2, a now higher freq
    assert len(c) == 2
    assert c.get("a") == 10


def test_delete_and_stats():
    c = LFUCache(3)
    c.put(1, "x")
    assert c.delete(1) is True
    assert c.delete(1) is False
    c.get(1)
    c.put(2, "y")
    c.get(2)
    assert (c.hits, c.misses) == (1, 1)


def test_tie_break_by_recency():
    # When frequencies are equal, the least-recently-used among them is evicted.
    c = LFUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    # both freq 1; a was inserted first so is less recent
    c.put("c", 3)       # should evict a
    assert "a" not in c
    assert "b" in c and "c" in c


def test_invalid_capacity():
    with pytest.raises(ValueError):
        LFUCache(0)
