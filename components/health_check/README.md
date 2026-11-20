# Health checker

**Category:** Reliability · **Added:** 2026-11-20

## Problem
Orchestrators and load balancers need to know whether a process is alive and
whether it is ready to receive traffic. A failing liveness check should restart
the process; a failing readiness check should only stop sending new requests.

## Design
`HealthChecker` holds two independent registries of named check functions.

- `add_liveness` / `add_readiness` register a callable that returns `True` when
  healthy.
- `liveness()` / `readiness()` run every registered check and return a
  `HealthStatus` whose `healthy` flag is the conjunction of the results.
- An exception inside a check is treated as failure.
- An empty registry is considered healthy (nothing has reported a problem).

| Operation | Time | Space |
|---|---|---|
| add / remove | O(1) | O(checks) |
| liveness / readiness | O(checks) | O(checks) |

## Trade-offs
- Checks are synchronous and run in the caller's thread; a slow check blocks the
  probe endpoint. Production systems usually give each check a timeout.
- The checker itself does not restart processes or update load-balancer state;
  it only reports. The orchestrator decides what to do with the answer.
- Separating liveness from readiness prevents a temporary dependency outage from
  causing unnecessary restarts.
- Not thread-safe: protect the registries with a lock if checks are added at
  runtime from multiple threads.

## Used in
Kubernetes liveness and readiness probes, AWS ELB health checks, Consul health
checks, service-mesh readiness gates.
