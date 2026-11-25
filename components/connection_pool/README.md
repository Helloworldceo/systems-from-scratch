# Connection Pool

**Category:** Backend · **Added:** 2026-11-25

## Problem
Opening a new database or network connection is expensive. A pool keeps a bounded
set of live connections ready for reuse so callers can borrow and return them quickly.

## Design
- A **factory** creates connections on demand.
- An **idle queue** holds free connections; a counter tracks how many have been created.
- `acquire` first tries an idle connection, then creates one if under `max_size`,
  otherwise waits (with optional timeout).
- `release` returns the connection to the idle queue.
- A context manager (`connection`) guarantees release even on exceptions.
- All mutations are protected by a lock; the queue itself is thread-safe.

| Operation | Time | Space |
|---|---|---|
| acquire / release (no wait) | O(1) | O(max_size) |
| acquire (wait) | O(timeout) | O(max_size) |

## Trade-offs
- Fixed maximum prevents resource exhaustion but can cause wait timeouts under load.
- No idle-timeout or health-check eviction; a real pool would periodically validate
  connections and discard stale ones.
- Connections are opaque objects supplied by the caller; the pool does not know how
  to close them beyond discarding references.
- Not suitable for processes that fork after the pool is created (file descriptors
  would be shared).

## Used in
Database client libraries (psycopg, SQLAlchemy, JDBC), HTTP connection pools
(urllib3, requests), gRPC channel pools.
