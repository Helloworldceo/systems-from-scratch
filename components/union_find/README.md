# Union-Find (Disjoint Set)

**Category:** Data structures · **Added:** 2026-11-15

## Problem
Efficiently answer "are these two items in the same group?" and "merge these two groups"
when the groups change over time. Classic use: Kruskal's MST, connected components,
equivalence relations.

## Design
- Each element points to a parent; the representative is the root of its tree.
- **Path compression**: after `find`, every node on the path points directly at the root.
- **Union by rank**: attach the shorter tree under the taller one so trees stay shallow.
- Elements are added lazily on first `find` or `union`.
- Nearly O(1) amortized per operation (inverse Ackermann).

| Operation | Time | Space |
|---|---|---|
| find / union / connected | nearly O(1) amortized | O(n) |

## Trade-offs
- Rank (or size) + path compression is the practical optimum; without them a long chain
  degrades to O(n).
- Not thread-safe: protect with a lock for concurrent use.
- For a fixed universe of integers a plain array is faster and simpler; the dict version
  supports any hashable keys and dynamic addition.
- Does not support split / undo; for that a different structure is needed.

## Used in
Kruskal's minimum spanning tree, percolation, network connectivity, image segmentation,
equivalence-class maintenance, and many union-find based algorithms.
