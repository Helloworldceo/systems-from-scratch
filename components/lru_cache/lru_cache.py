"""LRU (least-recently-used) cache with O(1) get and put.

A hash map gives O(1) lookup; a doubly linked list keeps usage order so the
least-recently-used entry can be evicted in O(1).
"""
from __future__ import annotations

from typing import Generic, Hashable, Optional, TypeVar

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


class _Node(Generic[K, V]):
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev: Optional[_Node] = None
        self.next: Optional[_Node] = None


class LRUCache(Generic[K, V]):
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self._map: dict[K, _Node[K, V]] = {}
        # Sentinels: head.next is most recent, tail.prev is least recent.
        self._head: _Node = _Node()
        self._tail: _Node = _Node()
        self._head.next, self._tail.prev = self._tail, self._head
        self.hits = 0
        self.misses = 0

    def __len__(self) -> int:
        return len(self._map)

    def __contains__(self, key: K) -> bool:
        return key in self._map

    def _unlink(self, node: _Node) -> None:
        node.prev.next, node.next.prev = node.next, node.prev

    def _push_front(self, node: _Node) -> None:
        node.prev, node.next = self._head, self._head.next
        self._head.next.prev = node
        self._head.next = node

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        node = self._map.get(key)
        if node is None:
            self.misses += 1
            return default
        self.hits += 1
        self._unlink(node)
        self._push_front(node)
        return node.value

    def put(self, key: K, value: V) -> None:
        node = self._map.get(key)
        if node is not None:
            node.value = value
            self._unlink(node)
            self._push_front(node)
            return
        if len(self._map) >= self.capacity:
            lru = self._tail.prev
            self._unlink(lru)
            del self._map[lru.key]
        node = _Node(key, value)
        self._map[key] = node
        self._push_front(node)

    def delete(self, key: K) -> bool:
        node = self._map.pop(key, None)
        if node is None:
            return False
        self._unlink(node)
        return True

    def keys(self) -> list[K]:
        """Keys from most to least recently used."""
        out, node = [], self._head.next
        while node is not self._tail:
            out.append(node.key)
            node = node.next
        return out
