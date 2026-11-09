# LFU Cache

**Category:** Data structures · **Added:** 2026-11-09

## Problem
Keep the most useful items in a fixed amount of memory. When the cache is full,
drop the item that has been used least often (and, among equals, the least recent).

## Design
- A **hash map** (`key -> node`) gives O(1) lookup.
- A **frequency map** (`freq -> doubly linked list`) groups nodes by access count.
- Within each frequency list the head is least recent and the tail is most recent,
  so eviction of the overall LFU entry is O(1).
- `get` and `put` on an existing key increment its frequency and move it to the
  corresponding list; a new key starts at frequency 1.

| Operation | Time | Space |
|---|---|---|
| get / put / delete | O(1) | O(capacity) |

## Trade-offs
- LFU resists one-time scans better than LRU, but a sudden change in access
  pattern can leave old high-frequency items occupying space for a long time
  (aging / windowed LFU or ARC address this).
- Not thread-safe: wrap calls in a lock for concurrent use.
- More bookkeeping than LRU (extra map + per-frequency lists).

## Used in
CDN edge caches, database buffer pools, operating-system page replacement,
Redis `volatile-lfu` / `allkeys-lfu`.
