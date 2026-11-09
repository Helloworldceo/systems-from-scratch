"""LFU (least-frequently-used) cache with O(1) get and put.

A frequency map plus per-frequency doubly linked lists keep both frequency
counts and relative order, so the least-frequently-used (and among equals
the least-recent) entry can be evicted in O(1).
"""
from __future__ import annotations

from typing import Generic, Hashable, Optional, TypeVar

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


class _Node(Generic[K, V]):
    __slots__ = ("key", "value", "freq", "prev", "next")

    def __init__(self, key: Optional[K] = None, value: Optional[V] = None, freq: int = 1):
        self.key = key
        self.value = value
        self.freq = freq
        self.prev: Optional[_Node] = None
        self.next: Optional[_Node] = None


class _FreqList:
    """Doubly linked list of nodes that share the same frequency."""

    def __init__(self) -> None:
        self.head = _Node()
        self.tail = _Node()
        self.head.next = self.tail
        self.tail.prev = self.head
        self.size = 0

    def empty(self) -> bool:
        return self.size == 0

    def append(self, node: _Node) -> None:
        # Insert just before tail (most recent within this frequency).
        node.prev = self.tail.prev
        node.next = self.tail
        self.tail.prev.next = node
        self.tail.prev = node
        self.size += 1

    def remove(self, node: _Node) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev
        self.size -= 1

    def pop_front(self) -> _Node:
        # Least recent within this frequency.
        node = self.head.next
        self.remove(node)
        return node


class LFUCache(Generic[K, V]):
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self._map: dict[K, _Node[K, V]] = {}
        self._freq: dict[int, _FreqList] = {}
        self._min_freq = 0
        self.hits = 0
        self.misses = 0

    def __len__(self) -> int:
        return len(self._map)

    def __contains__(self, key: K) -> bool:
        return key in self._map

    def _touch(self, node: _Node) -> None:
        """Increment frequency and move node to the new frequency list."""
        freq = node.freq
        self._freq[freq].remove(node)
        if self._freq[freq].empty() and self._min_freq == freq:
            self._min_freq += 1
            del self._freq[freq]
        node.freq = freq + 1
        if node.freq not in self._freq:
            self._freq[node.freq] = _FreqList()
        self._freq[node.freq].append(node)

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        node = self._map.get(key)
        if node is None:
            self.misses += 1
            return default
        self.hits += 1
        self._touch(node)
        return node.value

    def put(self, key: K, value: V) -> None:
        if self.capacity == 0:
            return
        node = self._map.get(key)
        if node is not None:
            node.value = value
            self._touch(node)
            return
        if len(self._map) >= self.capacity:
            # Evict least-frequent, least-recent within that frequency.
            victim = self._freq[self._min_freq].pop_front()
            del self._map[victim.key]
            if self._freq[self._min_freq].empty():
                del self._freq[self._min_freq]
        node = _Node(key, value, freq=1)
        self._map[key] = node
        if 1 not in self._freq:
            self._freq[1] = _FreqList()
        self._freq[1].append(node)
        self._min_freq = 1

    def delete(self, key: K) -> bool:
        node = self._map.pop(key, None)
        if node is None:
            return False
        freq = node.freq
        self._freq[freq].remove(node)
        if self._freq[freq].empty():
            del self._freq[freq]
            if self._min_freq == freq and self._map:
                self._min_freq = min(self._freq)
        return True

    def keys(self) -> list[K]:
        """Keys ordered by increasing frequency, then least- to most-recent within frequency."""
        out: list[K] = []
        for f in sorted(self._freq):
            lst = self._freq[f]
            node = lst.head.next
            while node is not lst.tail:
                out.append(node.key)
                node = node.next
        return out
