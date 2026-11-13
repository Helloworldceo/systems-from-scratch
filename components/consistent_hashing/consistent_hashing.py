"""Consistent hashing ring with virtual nodes.

Maps keys and nodes onto a circular hash space. Each physical node is
represented by several virtual nodes so that load is more even and adding
or removing a node only moves a fraction of the keys.
"""
from __future__ import annotations

import bisect
import hashlib
from typing import Hashable, Iterable, Optional


class ConsistentHash:
    """Hash ring that assigns keys to nodes with virtual nodes for balance."""

    def __init__(
        self,
        nodes: Optional[Iterable[str]] = None,
        virtual_nodes: int = 100,
    ):
        if virtual_nodes <= 0:
            raise ValueError("virtual_nodes must be positive")
        self.virtual_nodes = virtual_nodes
        self._ring: dict[int, str] = {}
        self._sorted: list[int] = []
        self.nodes: set[str] = set()
        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key: str) -> int:
        digest = hashlib.md5(key.encode("utf-8")).hexdigest()
        return int(digest, 16)

    def add_node(self, node: str) -> None:
        if not isinstance(node, str) or not node:
            raise ValueError("node must be a non-empty string")
        if node in self.nodes:
            return
        self.nodes.add(node)
        for i in range(self.virtual_nodes):
            h = self._hash(f"{node}#{i}")
            self._ring[h] = node
            bisect.insort(self._sorted, h)

    def remove_node(self, node: str) -> bool:
        if node not in self.nodes:
            return False
        self.nodes.remove(node)
        for i in range(self.virtual_nodes):
            h = self._hash(f"{node}#{i}")
            del self._ring[h]
        self._sorted = sorted(self._ring)
        return True

    def get_node(self, key: str) -> str:
        if not self._ring:
            raise ValueError("no nodes in the ring")
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        h = self._hash(key)
        idx = bisect.bisect_right(self._sorted, h)
        if idx == len(self._sorted):
            idx = 0
        return self._ring[self._sorted[idx]]

    def get_nodes(self, key: str, n: int) -> list[str]:
        """Return up to n distinct nodes, walking clockwise from the key."""
        if n <= 0:
            raise ValueError("n must be positive")
        if not self._ring:
            raise ValueError("no nodes in the ring")
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        h = self._hash(key)
        start = bisect.bisect_right(self._sorted, h)
        seen: set[str] = set()
        out: list[str] = []
        length = len(self._sorted)
        for i in range(length):
            idx = (start + i) % length
            node = self._ring[self._sorted[idx]]
            if node not in seen:
                seen.add(node)
                out.append(node)
                if len(out) == n:
                    break
        return out

    def __len__(self) -> int:
        return len(self.nodes)

    def __contains__(self, node: str) -> bool:
        return node in self.nodes
