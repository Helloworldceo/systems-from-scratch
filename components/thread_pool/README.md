# Thread pool

**Category:** Concurrency · **Added:** 2026-11-28

## Problem
Run many short tasks concurrently without paying the cost of creating a new
thread for every task, and without unbounded growth of threads.

## Design
- A fixed number of worker threads pull work from a shared `queue.Queue`.
- `submit` enqueues a callable plus a `Future` and returns the future immediately.
- Each worker runs the callable, then sets the result or exception on the future.
- Shutdown inserts sentinel values so workers exit cleanly; `wait=True` joins them.
- A context manager calls `shutdown` on exit.

| Operation | Time | Space |
|---|---|---|
| submit | O(1) amortized | O(queue size) |
| result (wait) | O(task time) | O(1) per future |
| shutdown | O(num_workers) | — |

## Trade-offs
- Fixed size prevents resource exhaustion but can queue tasks under load.
- No work-stealing or dynamic sizing (unlike some production pools).
- Exceptions from tasks are captured and re-raised on `result()`; they do not
  kill the worker.
- Daemon threads are used so an un-shutdown pool does not keep the process alive.
- Python's `concurrent.futures.ThreadPoolExecutor` is similar and more feature-rich;
  this version shows the queue-and-worker pattern explicitly.

## Used in
Web servers, job runners, connection handlers, any workload that fans out
independent CPU- or I/O-bound tasks.
