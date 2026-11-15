import pytest

from union_find import UnionFind


def test_basic_union_and_find():
    uf = UnionFind()
    assert uf.union(1, 2) is True
    assert uf.find(1) == uf.find(2)
    assert uf.connected(1, 2)
    assert uf.count == 1
    assert len(uf) == 2


def test_already_connected_returns_false():
    uf = UnionFind()
    uf.union("a", "b")
    assert uf.union("a", "b") is False
    assert uf.union("b", "a") is False
    assert uf.count == 1


def test_multiple_components():
    uf = UnionFind()
    uf.union(1, 2)
    uf.union(3, 4)
    assert not uf.connected(1, 3)
    assert uf.count == 2
    uf.union(2, 3)
    assert uf.connected(1, 4)
    assert uf.count == 1


def test_lazy_add_and_contains():
    uf = UnionFind()
    assert 10 not in uf
    assert uf.find(10) == 10
    assert 10 in uf
    assert len(uf) == 1
    assert uf.count == 1


def test_union_by_rank_and_path_compression():
    uf = UnionFind()
    # Build a chain that would be deep without compression / rank
    for i in range(5):
        uf.union(i, i + 1)
    root = uf.find(0)
    assert all(uf.find(i) == root for i in range(6))
    assert uf.count == 1
    # After path compression the parent links are flattened
    assert all(uf._parent[i] == root for i in range(6))


def test_empty_and_single():
    uf = UnionFind()
    assert uf.count == 0
    assert len(uf) == 0
    uf.add("solo")
    assert uf.connected("solo", "solo")
    assert uf.count == 1
