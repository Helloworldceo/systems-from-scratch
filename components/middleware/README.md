# Middleware Chain

**Category:** Backend · **Added:** 2026-11-22

## Problem
Cross-cutting concerns such as authentication, logging, tracing and response
rewriting should be reusable and composable without cluttering every handler.

## Design
- A `MiddlewareChain` holds an ordered list of middlewares registered with `use`.
- Each middleware is a callable `(request, next) -> response`.
- `handle` builds the onion: the first middleware is outermost, the final handler
  is the core. Calling `next` continues the chain; not calling it short-circuits.
- Requests and responses are plain dicts so the component stays dependency-free
  and easy to test.
- No I/O, clocks or global state; pure function composition.

| Operation | Time | Space |
|---|---|---|
| use | O(1) | O(middlewares) |
| handle | O(middlewares) | O(middlewares) call frames |

## Trade-offs
- Linear composition is ideal for a handful of middlewares; a large number of
  always-on middlewares adds stack depth and call overhead.
- Dict-based request/response is simple but untyped; a real framework would use
  structured objects and validation.
- Order is significant: authentication should run before business logic, logging
  often wraps everything.
- Not thread-safe for concurrent `use` while handling; freeze the chain after setup.
- No built-in error handling or timeout; those can be additional middlewares.

## Used in
Web frameworks (Express, Koa, Django middleware, FastAPI dependencies), API
gateways, reverse proxies, and any request pipeline that needs pluggable
cross-cutting behaviour.
