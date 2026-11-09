# Rate Limiter

**Category:** Reliability · **Added:** 2026-11-09

## Problem
Protect a service from overload and abuse by capping how often a client can call it.

## Designs
**Token bucket** (`TokenBucket`): the bucket holds up to `capacity` tokens and refills at `rate`
per second. Each request spends tokens. It allows short bursts while enforcing an average rate.
State is two numbers, so it's O(1) time and space.

**Sliding window log** (`SlidingWindowLog`): keeps the timestamps of recent requests and allows
a new one only if fewer than `limit` fall inside the last `window` seconds. It's exact, with no
boundary bursts, but uses O(limit) memory per client.

| | Token bucket | Sliding window log |
|---|---|---|
| Bursts | Allowed up to capacity | Never above limit |
| Memory | O(1) | O(limit) |
| Accuracy | Average rate | Exact |

## Trade-offs
- A *fixed* window counter is cheaper still but lets through 2× the limit around window edges.
- A *sliding window counter* (weighted current + previous window) approximates the log in O(1).
- In a distributed system the state lives in a shared store (for example Redis with Lua scripts)
  so all instances see the same counts.
- The clock is injectable, so the tests are deterministic and never sleep.

## Used in
API gateways (Kong, Envoy, AWS API Gateway), login-attempt throttling, Stripe and GitHub API limits.
