"""Skip list: a probabilistic ordered dictionary with O(log n) average operations.

A skip list is a multi-level linked list. Higher levels act as express lanes,
giving average O(log n) search, insert and delete without rebalancing.
"""
from __future__ import annotations

import random
from typing import Any, Callable, Generic, Iterator, Optional, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class _Node(Generic[K, V]):
    __slots__ = ("key", "value", "forward")

    def __init__(self, key: Optional[K], value: Optional[V], level: int):
        self.key = key
        self.value = value
        self.forward: list[Optional[_Node[K, V]]] = [None] * (level + 1)


class SkipList(Generic[K, V]):
    """Ordered map implemented as a skip list.

    Keys must be comparable. Duplicate keys overwrite the previous value.
    Heights are chosen randomly; pass a seed for reproducible behaviour.
    """

    def __init__(
        self,
        max_level: int = 16,
        p: float = 0.5,
        seed: Optional[int] = None,
    ):
        if max_level < 1:
            raise ValueError("max_level must be at least 1")
        if not 0 < p < 1:
            raise ValueError("p must be between 0 and 1 exclusive")
        self.max_level = max_level
        self.p = p
        self._rng = random.Random(seed)
        self._level = 0
        self._header = _Node(None, None, max_level)
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __contains__(self, key: K) -> bool:
        return self.search(key) is not None

    def _random_level(self) -> int:
        level = 0
        while self._rng.random() < self.p and level < self.max_level:
            level += 1
        return level

    def search(self, key: K) -> Optional[V]:
        """Return the value for key, or None if missing."""
        current = self._header
        for i in range(self._level, -1, -1):
            while current.forward[i] is not None and current.forward[i].key < key:  # type: ignore[operator]
                current = current.forward[i]  # type: ignore[assignment]
        current = current.forward[0]
        if current is not None and current.key == key:
            return current.value
        return None

    def insert(self, key: K, value: V) -> None:
        """Insert or update a key-value pair."""
        update = [self._header] * (self.max_level + 1)
        current = self._header
        for i in range(self._level, -1, -1):
            while current.forward[i] is not None and current.forward[i].key < key:  # type: ignore[operator]
                current = current.forward[i]  # type: ignore[assignment]
            update[i] = current

        current = current.forward[0]
        if current is not None and current.key == key:
            current.value = value
            return

        level = self._random_level()
        if level > self._level:
            for i in range(self._level + 1, level + 1):
                update[i] = self._header
            self._level = level

        node = _Node(key, value, level)
        for i in range(level + 1):
            node.forward[i] = update[i].forward[i]
            update[i].forward[i] = node
        self._size += 1

    def delete(self, key: K) -> bool:
        """Remove key. Return True if it was present."""
        update = [self._header] * (self.max_level + 1)
        current = self._header
        for i in range(self._level, -1, -1):
            while current.forward[i] is not None and current.forward[i].key < key:  # type: ignore[operator]
                current = current.forward[i]  # type: ignore[assignment]
            update[i] = current

        current = current.forward[0]
        if current is None or current.key != key:
            return False

        for i in range(self._level + 1):
            if update[i].forward[i] is not current:
                break
            update[i].forward[i] = current.forward[i]

        while self._level > 0 and self._header.forward[self._level] is None:
            self._level -= 1
        self._size -= 1
        return True

    def keys(self) -> list[K]:
        """All keys in sorted order."""
        out: list[K] = []
        node = self._header.forward[0]
        while node is not None:
            out.append(node.key)  # type: ignore[arg-type]
            node = node.forward[0]
        return out

    def items(self) -> list[tuple[K, V]]:
        """All (key, value) pairs in sorted order."""
        out: list[tuple[K, V]] = []
        node = self._header.forward[0]
        while node is not None:
            out.append((node.key, node.value))  # type: ignore[arg-type]
            node = node.forward[0]
        return out

    def __iter__(self) -> Iterator[K]:
        return iter(self.keys())
