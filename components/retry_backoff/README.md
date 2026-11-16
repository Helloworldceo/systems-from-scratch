# Retry with exponential backoff and jitter

**Category:** Reliability · **Added:** 2026-11-16

## Problem
Transient failures (network blips, temporary overload, locks) should be retried,
but immediately and repeatedly hammering a failing dependency makes the outage worse.

## Design
`Retry` wraps a callable and re-executes it on specified exceptions.

- After the *n*th failure the base delay is `base_delay * 2**(n-1)`, capped at `max_delay`.
- A multiplicative jitter of ±`jitter` (default 10 %) is added so concurrent clients do not
  synchronise their retries (thundering herd).
- The clock and the sleep function are injectable, so unit tests advance a fake clock
  instead of calling `time.sleep`.
- Only the listed exception types are retried; anything else propagates immediately.

| Operation | Time | Space |
|---|---|---|
| call (k attempts) | O(k) + sum of delays | O(1) |

## Trade-offs
- Full jitter (delay chosen uniformly in [0, exp]) spreads load better than the equal-jitter
  used here; the latter is simpler and still effective for modest concurrency.
- A circuit breaker or bulkhead is usually composed with retries so that a down dependency
  is not retried forever.
- The implementation is single-threaded; for async use a different sleep (asyncio.sleep)
  and an async wrapper.
- Not idempotency-aware: the caller must ensure the operation can be safely repeated.

## Used in
HTTP clients (requests, urllib3), message-queue consumers, database connection pools,
AWS SDK, gRPC retry policies.
