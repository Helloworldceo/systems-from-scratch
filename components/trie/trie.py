"""Trie (prefix tree) with insert, search, prefix check and autocomplete.

Shared prefixes are stored once. Autocomplete walks the subtree under a prefix
and returns matching words in deterministic (sorted) order.
"""
from __future__ import annotations

from typing import Dict, List, Optional


class _Node:
    __slots__ = ("children", "is_end")

    def __init__(self) -> None:
        self.children: Dict[str, _Node] = {}
        self.is_end: bool = False


class Trie:
    """Set of strings supporting O(L) lookup and prefix-based autocomplete."""

    def __init__(self) -> None:
        self._root = _Node()
        self.size = 0

    def __len__(self) -> int:
        return self.size

    def insert(self, word: str) -> None:
        """Insert a word. Duplicate inserts are no-ops."""
        if not word:
            raise ValueError("word must be non-empty")
        node = self._root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = _Node()
            node = node.children[ch]
        if not node.is_end:
            node.is_end = True
            self.size += 1

    def search(self, word: str) -> bool:
        """True if the exact word is present."""
        node = self._find(word)
        return node is not None and node.is_end

    def starts_with(self, prefix: str) -> bool:
        """True if any stored word begins with prefix."""
        return self._find(prefix) is not None

    def autocomplete(self, prefix: str = "", limit: Optional[int] = None) -> List[str]:
        """Words that start with prefix, in sorted order. Optional result limit."""
        node = self._find(prefix)
        if node is None:
            return []
        results: List[str] = []
        self._collect(node, prefix, results, limit)
        return results

    def delete(self, word: str) -> bool:
        """Remove a word. Returns True if it was present. Prunes unused nodes."""
        if not word:
            return False
        deleted = [False]

        def _delete(node: _Node, index: int) -> bool:
            if index == len(word):
                if not node.is_end:
                    return False
                node.is_end = False
                deleted[0] = True
                self.size -= 1
                return len(node.children) == 0
            ch = word[index]
            child = node.children.get(ch)
            if child is None:
                return False
            should_prune = _delete(child, index + 1)
            if should_prune:
                del node.children[ch]
            return not node.is_end and len(node.children) == 0

        _delete(self._root, 0)
        return deleted[0]

    def _find(self, s: str) -> Optional[_Node]:
        node = self._root
        for ch in s:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def _collect(
        self,
        node: _Node,
        current: str,
        results: List[str],
        limit: Optional[int],
    ) -> None:
        if limit is not None and len(results) >= limit:
            return
        if node.is_end:
            results.append(current)
        for ch in sorted(node.children):
            self._collect(node.children[ch], current + ch, results, limit)
            if limit is not None and len(results) >= limit:
                return
