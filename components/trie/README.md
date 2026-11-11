# Trie

**Category:** Data structures · **Added:** 2026-11-11

## Problem
Store a set of strings so that exact lookups, prefix checks and autocomplete
suggestions are efficient, especially when many strings share common prefixes.

## Design
- Each node holds a `dict` of character → child and an `is_end` flag.
- `insert` walks (or creates) the path for the word and marks the final node.
- `search` and `starts_with` walk the path; the former also checks `is_end`.
- `autocomplete` locates the prefix node then performs a DFS, collecting words
  in sorted character order so results are deterministic. An optional `limit`
  stops early.
- `delete` unmarks the end node and prunes any now-unused branches.

| Operation | Time | Space |
|---|---|---|
| insert / search / starts_with / delete | O(L) | O(total characters stored) |
| autocomplete | O(L + matches) | |

L = length of the word or prefix.

## Trade-offs
- Excellent for shared prefixes (far less memory than a plain set of strings).
- Not thread-safe: protect with a lock for concurrent use.
- Case-sensitive; normalize inputs if case-insensitivity is required.
- For a tiny fixed alphabet an array of children can be faster, but a dict keeps
  memory proportional to the characters that actually appear.

## Used in
Search-box autocomplete, IDE symbol completion, spell-checkers, routing tables
(binary or radix tries), dictionary implementations.
