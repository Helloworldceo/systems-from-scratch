# Consistent Hashing

**Category:** Data structures · **Added:** 2026-11-13

## Problem
Assign keys to a changing set of servers so that adding or removing a server
moves only a small fraction of the keys, not everything.

## Design
- Keys and nodes are hashed onto a circular ring (0 … 2ⁱ²⁸-1 via MD5).
- Each physical node is placed at `virtual_nodes` positions so the load is more uniform.
- A key is owned by the first node clockwise from its hash (wraps around).
- Adding/removing a node only affects the keys that fall between the neighbouring points.

| Operation | Time | Space |
|---|---|---|
| add / remove node | O(V log N) | O(N · V) |
| get_node | O(log (N · V)) | |

V = virtual nodes per physical node, N = number of physical nodes.

## Trade-offs
- More virtual nodes improve balance but use more memory and make membership changes slightly slower.
- MD5 is used only as a fast, deterministic 128-bit hash; it is not a security boundary.
- Not thread-safe: protect the ring with a lock if it is shared.
- Real systems often combine this with consistent hashing libraries (Ketama, Jump Hash, Maglev) or with a coordination service.

## Used in
Distributed caches (Memcached, Redis Cluster), CDNs, Dynamo-style key-value stores, load balancers.
