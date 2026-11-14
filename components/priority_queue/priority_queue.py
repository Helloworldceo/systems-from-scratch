"""Min-heap priority queue with O(log n) decrease-key.

A binary heap stores (priority, item) pairs. A position map lets any item be
located in O(1) so its priority can be lowered and the heap restored in O(log n).
"""
from __future__ import annotations

from typing import Generic, Hashable, TypeVar

T = TypeVar("T", bound=Hashable)


class PriorityQueue(Generic[T]):
    """Min-heap priority queue supporting decrease-key."""

    def __init__(self) -> None:
        self._heap: list[tuple[float, T]] = []
        self._pos: dict[T, int] = {}

    def __len__(self) -> int:
        return len(self._heap)

    def __contains__(self, item: T) -> bool:
        return item in self._pos

    def push(self, item: T, priority: float) -> None:
        if item in self._pos:
            raise ValueError(f"item {item!r} already in queue")
        self._heap.append((priority, item))
        idx = len(self._heap) - 1
        self._pos[item] = idx
        self._sift_up(idx)

    def pop(self) -> T:
        if not self._heap:
            raise IndexError("pop from empty priority queue")
        if len(self._heap) == 1:
            item = self._heap.pop()[1]
            del self._pos[item]
            return item
        self._swap(0, len(self._heap) - 1)
        item = self._heap.pop()[1]
        del self._pos[item]
        self._sift_down(0)
        return item

    def peek(self) -> T:
        if not self._heap:
            raise IndexError("peek from empty priority queue")
        return self._heap[0][1]

    def decrease_key(self, item: T, new_priority: float) -> None:
        if item not in self._pos:
            raise KeyError(f"item {item!r} not in queue")
        idx = self._pos[item]
        old_priority = self._heap[idx][0]
        if new_priority >= old_priority:
            raise ValueError("new priority must be strictly smaller")
        self._heap[idx] = (new_priority, item)
        self._sift_up(idx)

    def priority_of(self, item: T) -> float:
        if item not in self._pos:
            raise KeyError(f"item {item!r} not in queue")
        return self._heap[self._pos[item]][0]

    def _sift_up(self, idx: int) -> None:
        while idx > 0:
            parent = (idx - 1) // 2
            if self._heap[idx][0] < self._heap[parent][0]:
                self._swap(idx, parent)
                idx = parent
            else:
                break

    def _sift_down(self, idx: int) -> None:
        n = len(self._heap)
        while True:
            left = 2 * idx + 1
            right = 2 * idx + 2
            smallest = idx
            if left < n and self._heap[left][0] < self._heap[smallest][0]:
                smallest = left
            if right < n and self._heap[right][0] < self._heap[smallest][0]:
                smallest = right
            if smallest == idx:
                break
            self._swap(idx, smallest)
            idx = smallest

    def _swap(self, i: int, j: int) -> None:
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]
        self._pos[self._heap[i][1]] = i
        self._pos[self._heap[j][1]] = j
