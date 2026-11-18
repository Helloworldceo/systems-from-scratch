# Bulkhead

**Category:** Reliability · **Added:** 2026-11-18

## Problem
Prevent a slow or failing dependency from exhausting shared resources (threads, connections)
and cascading failure to the rest of the system.

## Design
A bulkhead is a concurrency limiter: at most `max_concurrent` calls may be in flight at once.
Callers that find the bulkhead full are rejected immediately (or after a short wait) instead of
queueing forever.

- A counter protected by a `threading.Condition` tracks in-flight calls.
- `try_acquire` / `acquire` take a slot; `release` returns it and wakes a waiter.
- Context managers (`with bulkhead:` and `bulkhead.slot()`) guarantee release even on exceptions.
- Stats (`admitted`, `rejected`, `in_flight`) are kept for observability.

| Operation | Time | Space |
|---|---|---|
| try_acquire / release | O(1) | O(1) |
| acquire (with wait) | O(1) + wait | O(1) |

## Trade-offs
- Immediate rejection (timeout=0) gives the fastest failure signal and protects the caller pool,
  but discards work. A short wait can absorb brief spikes.
- This is a *semaphore-style* bulkhead. A *thread-pool* bulkhead isolates CPU/IO completely by
  dedicating threads; it is heavier.
- Not a substitute for a rate limiter: bulkhead limits concurrency, rate limiter limits throughput
  over time. They are often used together.
- The implementation is educational and single-process; production systems often share the limit
  via Redis or a sidecar.

## Used in
Netflix Hystrix, Resilience4j, Envoy outlier detection, database connection pools, API gateways
that protect downstream services.
