# HTTP Router

**Category:** Backend · **Added:** 2026-11-21

## Problem
Map an incoming HTTP method and path to the right handler, extracting named
parameters from the URL so a single route can serve many resources.

## Design
- Routes are registered with a method, a path pattern and a handler.
- Patterns start with `/` and use `{name}` placeholders for a single path segment.
- Each pattern is compiled once to a regular expression with named groups.
- Matching walks the registration order and returns the first hit: `(handler, params)`.
- A decorator form `@router.route(method, path)` is provided for convenience.
- The clock is irrelevant; matching is pure and deterministic.

| Operation | Time | Space |
|---|---|---|
| add | O(segments) | O(routes) |
| match | O(routes × segments) | O(1) extra |

## Trade-offs
- Linear scan is fine for tens of routes; a radix tree or method-grouped trie
  would make matching O(path length) for large routers.
- Only single-segment parameters are supported (no `*` wildcards or regex segments).
- First-match wins, so more specific routes must be registered before general ones.
- No middleware, query-string parsing or body handling; those are separate concerns.
- Not thread-safe for concurrent `add` while matching; freeze the router after setup.

## Used in
Web frameworks (Flask, FastAPI, Express), API gateways, reverse proxies that do
path-based routing, and any service that exposes a small set of HTTP endpoints.
