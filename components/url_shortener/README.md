# URL Shortener

**Category:** Backend · **Added:** 2026-11-23

## Problem
Turn long URLs into short, shareable codes while guaranteeing that each long URL
maps to exactly one short code and that short codes never collide.

## Design
- A monotonic counter is encoded to base62 (0-9, A-Z, a-z) to produce short codes.
- Two maps keep the bidirectional mapping: short → long and long → short.
- `shorten` reuses an existing code for a previously seen long URL.
- If a generated code is already taken (collision), the counter advances until a free code is found.
- `expand` accepts either the full short URL or the bare code.

| Operation | Time | Space |
|---|---|---|
| shorten / expand | O(1) amortized | O(number of URLs) |

## Trade-offs
- Sequential codes are predictable; a cryptographic hash (with collision retry) or a random
  62-bit string is harder to guess but needs more collision handling.
- In-memory only: a real service would persist the maps (or use a database with a unique index)
  and would need distributed ID generation (e.g. snowflake) to avoid races.
- No expiration, analytics, or custom aliases; those are straightforward extensions.
- Not thread-safe: protect the maps with a lock for concurrent use.

## Used in
URL shortener services (bit.ly, tinyurl), link-sharing features in chat apps, QR-code payloads,
and referral or campaign tracking links.
