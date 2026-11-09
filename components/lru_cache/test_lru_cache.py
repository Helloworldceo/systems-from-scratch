import pytest

from lru_cache import LRUCache


def test_get_put_basic():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    assert c.get("a") == 1
    assert c.get("missing") is None
    assert c.get("missing", 0) == 0


def test_evicts_least_recently_used():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.get("a")          # a is now most recent
    c.put("c", 3)       # evicts b
    assert "b" not in c
    assert c.keys() == ["c", "a"]


def test_update_moves_to_front_without_growing():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.put("a", 10)
    assert len(c) == 2
    assert c.keys() == ["a", "b"]
    assert c.get("a") == 10


def test_delete_and_stats():
    c = LRUCache(3)
    c.put(1, "x")
    assert c.delete(1) is True
    assert c.delete(1) is False
    c.get(1)
    c.put(2, "y")
    c.get(2)
    assert (c.hits, c.misses) == (1, 1)


def test_invalid_capacity():
    with pytest.raises(ValueError):
        LRUCache(0)
