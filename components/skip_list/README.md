# Skip List

**Category:** Data structures · **Added:** 2026-11-12

## Problem
Maintain an ordered set of keys with fast search, insertion and deletion.
A balanced binary tree works but requires careful rebalancing. A skip list
achieves the same average performance with simpler, randomized structure.

## Design
- Multiple levels of linked lists. Level 0 is a complete sorted list.
- Each higher level is a sparse "express lane" of nodes promoted with probability `p`.
- Search starts at the highest level and drops down when the next node would overshoot.
- Insert and delete first find the predecessors at every level (the `update` array),
  then splice the node in or out.
- A fixed seed makes the random heights reproducible for tests.

| Operation | Average | Worst |
|---|---|---|
| search / insert / delete | O(log n) | O(n) |
| space | O(n) | O(n log n) |

## Trade-offs
- Average-case performance is excellent and the code is simpler than red-black trees.
- Worst-case is linear (though vanishingly rare with a good seed or high max level).
- Not thread-safe; external locking is required for concurrent use.
- Compared with a sorted list or tree map, it trades a small amount of extra memory
  for faster updates.

## Used in
Redis sorted sets (ZSET), LevelDB / RocksDB memtables, various concurrent skip-list
libraries, and as a teaching alternative to balanced trees.
