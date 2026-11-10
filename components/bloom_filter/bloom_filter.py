"""Bloom filter: probabilistic set membership with no false negatives.

A bit array and k independent hash functions mark an item as present by
setting k bits. Lookup checks that all k bits are set. Collisions produce
false positives; an item that was added is always reported present.
"""
from __future__ import annotations

import hashlib
import math
from typing import Any


class BloomFilter:
    """Space-efficient probabilistic set.

    Parameters
    ----------
    size:
        Number of bits in the filter.
    num_hashes:
        Number of hash functions (k).
    """

    def __init__(self, size: int, num_hashes: int):
        if size <= 0:
            raise ValueError("size must be positive")
        if num_hashes <= 0:
            raise ValueError("num_hashes must be positive")
        self.size = size
        self.num_hashes = num_hashes
        # Bit array packed into bytes.
        self._bits = bytearray((size + 7) // 8)
        self.added = 0  # number of insertions (including duplicates)

    def _hashes(self, item: Any):
        data = self._to_bytes(item)
        # Double-hashing technique: h_i = h1 + i * h2  (mod size)
        h1 = int.from_bytes(hashlib.sha256(data).digest()[:8], "little")
        h2 = int.from_bytes(hashlib.sha256(data + b"\x01").digest()[:8], "little")
        for i in range(self.num_hashes):
            yield (h1 + i * h2) % self.size

    @staticmethod
    def _to_bytes(item: Any) -> bytes:
        if isinstance(item, bytes):
            return item
        if isinstance(item, str):
            return item.encode("utf-8")
        return str(item).encode("utf-8")

    def _set_bit(self, index: int) -> None:
        byte_index, bit = divmod(index, 8)
        self._bits[byte_index] |= 1 << bit

    def _get_bit(self, index: int) -> bool:
        byte_index, bit = divmod(index, 8)
        return bool(self._bits[byte_index] & (1 << bit))

    def add(self, item: Any) -> None:
        """Insert an item. Idempotent for membership, but increments `added`."""
        for idx in self._hashes(item):
            self._set_bit(idx)
        self.added += 1

    def __contains__(self, item: Any) -> bool:
        """Return True if the item *might* be present (no false negatives)."""
        return all(self._get_bit(idx) for idx in self._hashes(item))

    def __len__(self) -> int:
        return self.added

    def estimated_false_positive_rate(self) -> float:
        """Approximate false-positive probability after the insertions so far.

        (1 - exp(-k * n / m))^k
        """
        if self.added == 0:
            return 0.0
        m, n, k = self.size, self.added, self.num_hashes
        return (1.0 - math.exp(-k * n / m)) ** k

    def bit_count(self) -> int:
        """Number of bits currently set (useful for diagnostics)."""
        return sum(bin(byte).count("1") for byte in self._bits)

    @classmethod
    def from_capacity(cls, capacity: int, error_rate: float) -> BloomFilter:
        """Create a filter sized for `capacity` items at the given error rate.

        Optimal m = -n ln(p) / (ln 2)^2
        Optimal k = (m / n) ln 2
        """
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if not 0 < error_rate < 1:
            raise ValueError("error_rate must be between 0 and 1")
        m = math.ceil(-capacity * math.log(error_rate) / (math.log(2) ** 2))
        k = max(1, round((m / capacity) * math.log(2)))
        return cls(m, k)
