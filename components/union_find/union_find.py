"""Union-Find (disjoint set) with path compression and union by rank.

Supports dynamic addition of elements. find is nearly O(1) amortized;
union is O(1) amortized with both optimizations.
"""
from __future__ import annotations

from typing import Hashable, TypeVar

T = TypeVar("T", bound=Hashable)


class UnionFind:
    """Disjoint-set union structure.

    Elements are added lazily on first use of find or union.
    """

    def __init__(self) -> None:
        self._parent: dict[T, T] = {}
        self._rank: dict[T, int] = {}
        self._count = 0

    def add(self, x: T) -> None:
        """Add an element as its own set if not already present."""
        if x not in self._parent:
            self._parent[x] = x
            self._rank[x] = 0
            self._count += 1

    def find(self, x: T) -> T:
        """Return the representative of the set containing x (with path compression)."""
        if x not in self._parent:
            self.add(x)
        if self._parent[x] != x:
            self._parent[x] = self.find(self._parent[x])
        return self._parent[x]

    def union(self, x: T, y: T) -> bool:
        """Merge the sets containing x and y. Return True if they were different."""
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self._rank[px] < self._rank[py]:
            px, py = py, px
        self._parent[py] = px
        if self._rank[px] == self._rank[py]:
            self._rank[px] += 1
        self._count -= 1
        return True

    def connected(self, x: T, y: T) -> bool:
        """Return True if x and y are in the same set."""
        return self.find(x) == self.find(y)

    @property
    def count(self) -> int:
        """Number of disjoint sets."""
        return self._count

    def __len__(self) -> int:
        """Number of elements added so far."""
        return len(self._parent)

    def __contains__(self, x: T) -> bool:
        return x in self._parent
