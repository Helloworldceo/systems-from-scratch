# Circuit Breaker

**Category:** Reliability · **Added:** 2026-11-17

## Problem
Stop hammering a failing dependency. After too many consecutive failures, fail
fast for a while, then cautiously probe whether the dependency has recovered.

## Design
Three states:

- **Closed** — requests pass through. Consecutive failures are counted; a success
  resets the count. Reaching `failure_threshold` trips the breaker.
- **Open** — requests are rejected immediately with `CircuitOpenError`. After
  `recovery_timeout` seconds the breaker moves to half-open.
- **Half-open** — a limited number of trial calls are allowed. Enough successes
  (`success_threshold`) close the circuit; any failure re-opens it.

The clock is injectable so tests never sleep. A lock makes state transitions
thread-safe.

| Operation | Time | Space |
|---|---|---|
| allow / call / record | O(1) | O(1) |

## Trade-offs
- Counting consecutive failures is simple and effective for hard outages; a
  sliding-window error rate is better for intermittent failures.
- Half-open probes must be limited or a recovering service can be overwhelmed
  by a thundering herd.
- The breaker is per-instance; in a fleet each replica has its own state unless
  you share it (for example via Redis).

## Used in
Hystrix, Resilience4j, Envoy outlier detection, service meshes, and any client
that talks to a flaky downstream.
