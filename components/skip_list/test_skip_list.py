import pytest

from skip_list import SkipList


def test_insert_and_search():
    sl = SkipList(seed=42)
    sl.insert(3, "c")
    sl.insert(1, "a")
    sl.insert(2, "b")
    assert sl.search(1) == "a"
    assert sl.search(2) == "b"
    assert sl.search(3) == "c"
    assert sl.search(4) is None
    assert len(sl) == 3


def test_keys_are_sorted():
    sl = SkipList(seed=1)
    for k in [5, 1, 3, 2, 4]:
        sl.insert(k, k * 10)
    assert sl.keys() == [1, 2, 3, 4, 5]
    assert sl.items() == [(1, 10), (2, 20), (3, 30), (4, 40), (5, 50)]


def test_update_existing_key():
    sl = SkipList(seed=7)
    sl.insert("a", 1)
    sl.insert("a", 2)
    assert sl.search("a") == 2
    assert len(sl) == 1
    assert "a" in sl


def test_delete():
    sl = SkipList(seed=99)
    sl.insert(10, "x")
    sl.insert(20, "y")
    sl.insert(30, "z")
    assert sl.delete(20) is True
    assert sl.delete(20) is False
    assert sl.search(20) is None
    assert len(sl) == 2
    assert sl.keys() == [10, 30]
    assert sl.delete(10) is True
    assert sl.delete(30) is True
    assert len(sl) == 0
    assert sl.keys() == []


def test_empty_and_contains():
    sl = SkipList()
    assert len(sl) == 0
    assert 1 not in sl
    assert sl.search(1) is None
    assert sl.delete(1) is False


def test_invalid_args():
    with pytest.raises(ValueError):
        SkipList(max_level=0)
    with pytest.raises(ValueError):
        SkipList(p=0)
    with pytest.raises(ValueError):
        SkipList(p=1)


def test_many_inserts_deterministic():
    sl = SkipList(seed=123, max_level=8)
    n = 100
    for i in range(n):
        sl.insert(i, i)
    assert len(sl) == n
    assert sl.keys() == list(range(n))
    for i in range(0, n, 10):
        assert sl.search(i) == i
        assert sl.delete(i) is True
    assert len(sl) == n - 10
