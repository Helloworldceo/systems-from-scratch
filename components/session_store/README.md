# Session Store

**Category:** Backend · **Added:** 2026-11-24

## Problem
Keep short-lived user state (login sessions, CSRF tokens, shopping carts) that must
automatically disappear after a period of inactivity or a fixed lifetime.

## Design
- A single dictionary maps opaque session keys to `(value, absolute_expiry)`.
- Every read and write checks the current clock; expired entries are deleted on the spot.
- `create` generates a cryptographically secure key (`secrets.token_urlsafe`) or accepts a
  caller-supplied one.
- `renew` extends the lifetime of a still-valid session; `cleanup` sweeps all expired keys.
- An injectable clock makes expiry deterministic in tests; a lock protects concurrent use.

| Operation | Time | Space |
|---|---|---|
| create / get / set / delete / renew | O(1) | O(live sessions) |
| cleanup | O(n) | O(1) extra |

## Trade-offs
- Purely in-memory: all sessions are lost on process restart. Production systems persist
  them (Redis, Memcached, or a database with a background sweeper).
- Absolute expiry only (no sliding window unless the application calls `renew` on each
  request).
- Not distributed: every instance has its own store. Sticky sessions or a shared backend
  are required for horizontal scaling.
- Key generation uses the OS CSPRNG; collisions are negligible for practical sizes.

## Used in
Web frameworks (Flask/Django session middleware), Redis `EXPIRE`, browser cookies with
`Max-Age`, OAuth access-token stores.
