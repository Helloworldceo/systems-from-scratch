# Priority Queue

**Category:** Data structures · **Added:** 2026-11-14

## Problem
Efficiently extract the item with the lowest priority and lower the priority of an
existing item (decrease-key), as needed by Dijkstra, A* and event-driven simulation.

## Design
- A binary **min-heap** stored as a list of `(priority, item)` pairs.
- A **position map** (`item → index`) lets any item be found in O(1).
- `push` and `pop` restore the heap in O(log n); `decrease_key` updates the priority
  and sifts the item upward.
- Items must be unique and hashable.

| Operation | Time | Space |
|---|---|---|
| push / pop / decrease_key | O(log n) | O(n) |
| peek / contains / len | O(1) | |

## Trade-offs
- Classic binary heap with handles (the position map) gives true O(log n) decrease-key;
  Python's `heapq` does not support it efficiently.
- Not thread-safe: protect with a lock for concurrent use.
- Priorities are compared with `<`; equal priorities leave the relative order undefined.
- Only decrease is supported; increasing a key would require a sift-down.

## Used in
Dijkstra's shortest path, A* search, OS process schedulers, discrete-event simulation,
Huffman coding.
