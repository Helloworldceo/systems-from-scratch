# LRU Cache

**Category:** Data structures · **Added:** 2026-11-09

## Problem
Keep the most useful items in a fixed amount of memory. When the cache is full,
drop the item that was used least recently.

## Design
- A **hash map** (`key -> node`) gives O(1) lookup.
- A **doubly linked list** keeps usage order: the head is most recent, the tail least recent.
- Sentinel head/tail nodes remove edge cases when the list is empty.
- `get` and `put` move the touched node to the front; eviction removes `tail.prev`.

| Operation | Time | Space |
|---|---|---|
| get / put / delete | O(1) | O(capacity) |

## Trade-offs
- LRU suits workloads with temporal locality; a single large scan can flush hot items
  (LFU, 2Q or ARC handle that better).
- Not thread-safe: wrap calls in a lock for concurrent use.
- Python's `collections.OrderedDict` with `move_to_end` gives the same behaviour in fewer
  lines; this version shows the underlying mechanics.

## Used in
CPU caches, database buffer pools, CDN edge caches, `functools.lru_cache`, Redis `allkeys-lru`.
