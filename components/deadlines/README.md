# Timeout and deadline propagation

**Category:** Reliability · **Added:** 2026-11-19

## Problem
A request has a limited budget of time. Nested calls (database queries, other
services) must stop as soon as that budget is exhausted, and a child must not
be able to extend its parent's deadline.

## Design
A `Deadline` holds an absolute expiration time (or `None` for no limit) and an
injectable clock.

- `from_timeout(t)` sets the deadline to now + t.
- `remaining()` and `expired()` report the state.
- `with_timeout(t)` returns a child whose deadline is the earlier of the parent
  and now + t, so time only ever shrinks.
- `check()` raises `DeadlineExceeded` once the deadline has passed.

| Operation | Time | Space |
|---|---|---|
| remaining / expired / with_timeout | O(1) | O(1) |

## Trade-offs
- Absolute deadlines (rather than relative timeouts) make propagation exact and
  race-free: the child sees the same wall-clock expiration.
- Callers must check the deadline themselves; this module does not cancel work.
- In a real system the deadline is usually carried in a request header or
  context object and converted to a local `Deadline` at each hop.
- The clock is injectable so tests never sleep.

## Used in
gRPC deadlines, Go `context.Context`, AWS request timeouts, service meshes that
propagate `x-request-deadline`.
