# Idempotency-key handler

**Category:** Backend · **Added:** 2026-11-26

## Problem
Make non-idempotent operations (payments, order creation, emails) safe to retry.
A client that retries after a network timeout must not create a second charge or
duplicate side effect.

## Design
- Each request carries a unique **idempotency key** (client-generated).
- The handler records the result of the first *successful* execution of the
  operation under that key, together with an expiry time.
- A later call with the same key returns the cached result immediately; the
  operation is not run again.
- While an operation is still running, a second concurrent call with the same
  key raises `IdempotencyConflict` so the caller can wait or reject.
- Failures are **not** cached, so a transient error can be retried.
- An injectable clock makes TTL behaviour deterministic in tests.

| Operation | Time | Space |
|---|---|---|
| execute (hit) | O(1) | O(number of live keys) |
| execute (miss) | O(1) + cost of operation | |

## Trade-offs
- Only successful results are stored. Some systems also cache the error response
  so every retry sees the same failure; that requires a policy for which errors
  are permanent.
- In-progress detection prevents duplicate work under concurrent retries but
  requires the caller to handle `IdempotencyConflict` (retry later, or return 409).
- In a multi-instance deployment the store must be shared (Redis, database)
  and the "in progress" marker must be atomic (SETNX or a lock).
- Keys should be high-entropy and unique per logical request; they are not
  authentication tokens.

## Used in
Stripe, PayPal, AWS, and most payment / order APIs; any API that must tolerate
client retries without creating duplicate side effects.
