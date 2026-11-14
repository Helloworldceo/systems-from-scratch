import pytest

from priority_queue import PriorityQueue


def test_push_pop_min():
    pq = PriorityQueue()
    pq.push("c", 3)
    pq.push("a", 1)
    pq.push("b", 2)
    assert pq.pop() == "a"
    assert pq.pop() == "b"
    assert pq.pop() == "c"
    assert len(pq) == 0


def test_decrease_key_reorders():
    pq = PriorityQueue()
    pq.push("a", 5)
    pq.push("b", 4)
    pq.push("c", 3)
    assert pq.peek() == "c"
    pq.decrease_key("a", 1)
    assert pq.peek() == "a"
    assert pq.pop() == "a"
    assert pq.pop() == "c"


def test_empty_and_contains():
    pq = PriorityQueue()
    assert len(pq) == 0
    assert "x" not in pq
    with pytest.raises(IndexError):
        pq.pop()
    with pytest.raises(IndexError):
        pq.peek()
    pq.push(1, 10)
    assert 1 in pq
    assert pq.priority_of(1) == 10


def test_duplicate_item_and_invalid_decrease():
    pq = PriorityQueue()
    pq.push("x", 2.0)
    with pytest.raises(ValueError):
        pq.push("x", 1.0)
    with pytest.raises(ValueError):
        pq.decrease_key("x", 2.0)
    with pytest.raises(ValueError):
        pq.decrease_key("x", 3.0)
    with pytest.raises(KeyError):
        pq.decrease_key("missing", 0)


def test_multiple_decreases_and_order():
    pq = PriorityQueue()
    for i in range(5):
        pq.push(i, float(i + 10))
    pq.decrease_key(4, 0)
    pq.decrease_key(2, 1)
    assert [pq.pop() for _ in range(5)] == [4, 2, 0, 1, 3]


def test_single_element():
    pq = PriorityQueue()
    pq.push("only", 42)
    assert pq.peek() == "only"
    assert pq.pop() == "only"
    assert len(pq) == 0
