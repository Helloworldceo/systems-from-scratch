import pytest

from consistent_hashing import ConsistentHash


def test_get_node_basic_and_stable():
    ring = ConsistentHash(["a", "b", "c"], virtual_nodes=50)
    node = ring.get_node("user-123")
    assert node in {"a", "b", "c"}
    assert ring.get_node("user-123") == node
    assert ring.get_node("user-456") in {"a", "b", "c"}


def test_add_node_moves_only_some_keys():
    ring = ConsistentHash(["a", "b"], virtual_nodes=20)
    keys = [f"key-{i}" for i in range(100)]
    before = {k: ring.get_node(k) for k in keys}
    ring.add_node("c")
    after = {k: ring.get_node(k) for k in keys}
    moved = sum(1 for k in keys if before[k] != after[k])
    assert 0 < moved < len(keys)
    assert all(after[k] in {"a", "b", "c"} for k in keys)


def test_remove_node():
    ring = ConsistentHash(["a", "b", "c"], virtual_nodes=10)
    assert ring.remove_node("b") is True
    assert "b" not in ring
    assert ring.remove_node("b") is False
    keys = [f"k{i}" for i in range(50)]
    for k in keys:
        assert ring.get_node(k) in {"a", "c"}


def test_get_nodes_replicas():
    ring = ConsistentHash(["n1", "n2", "n3", "n4"], virtual_nodes=30)
    replicas = ring.get_nodes("my-key", 3)
    assert len(replicas) == 3
    assert len(set(replicas)) == 3
    assert all(r in ring.nodes for r in replicas)
    assert ring.get_nodes("my-key", 1) == [ring.get_node("my-key")]


def test_virtual_nodes_improve_balance():
    # With many virtual nodes the assignment should be reasonably even
    ring = ConsistentHash(["a", "b", "c"], virtual_nodes=100)
    counts = {n: 0 for n in ring.nodes}
    for i in range(300):
        counts[ring.get_node(f"item-{i}")] += 1
    # each node should get a non-trivial share
    assert all(c > 50 for c in counts.values())


def test_empty_and_invalid():
    ring = ConsistentHash()
    with pytest.raises(ValueError):
        ring.get_node("x")
    with pytest.raises(ValueError):
        ConsistentHash(virtual_nodes=0)
    with pytest.raises(ValueError):
        ConsistentHash().add_node("")
    with pytest.raises(TypeError):
        ConsistentHash(["a"]).get_node(123)  # type: ignore[arg-type]
