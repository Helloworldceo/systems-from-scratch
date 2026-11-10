# Bloom Filter

**Category:** Data structures · **Added:** 2026-11-10

## Problem
Answer "have I seen this item before?" with a fixed amount of memory and no
false negatives, accepting a controllable false-positive rate. Useful when the
set is huge and an exact structure would be too large.

## Design
- A **bit array** of `m` bits, initially all zero.
- `k` independent hash functions map each item to `k` positions.
- `add` sets those `k` bits; `__contains__` returns true only if all `k` are set.
- Hashes are produced with double hashing (`h1 + i·h2`) over SHA-256 so the
  implementation stays in the standard library and is deterministic.
- `from_capacity(n, p)` sizes the filter for an expected number of items and a
  target false-positive rate using the classic formulas.

| Operation | Time | Space |
|---|---|---|
| add / contains | O(k) | O(m) bits |

## Trade-offs
- No false negatives, but false positives are possible and increase with load.
- Items cannot be deleted (counting Bloom filters or cuckoo filters allow that).
- Hash quality and independence affect the real false-positive rate; the estimate
  assumes ideal hashes.
- Not thread-safe: protect concurrent adds with a lock.

## Used in
Web caches (to avoid disk lookups), database query engines (skip irrelevant
SSTables), spam filters, network routers, Bitcoin's transaction filters.
