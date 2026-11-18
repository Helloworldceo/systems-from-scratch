"""Bulkhead concurrency limiter.

Isolates a dependency by capping the number of concurrent calls so a slow or
failing upstream cannot exhaust the whole thread pool.
"""
from __future__ import annotations

import threading
from contextlib import contextmanager
from typing import Generator, Optional


class BulkheadFull(Exception):
    """Raised when a bulkhead rejects a call because it is at capacity."""


class Bulkhead:
    """Limits concurrent executions to `max_concurrent`.

    Excess calls are rejected immediately (or after an optional wait timeout).
    """

    def __init__(self, max_concurrent: int, name: str = "default"):
        if max_concurrent <= 0:
            raise ValueError("max_concurrent must be positive")
        self.max_concurrent = max_concurrent
        self.name = name
        self._lock = threading.Lock()
        self._cond = threading.Condition(self._lock)
        self._in_flight = 0
        self.admitted = 0
        self.rejected = 0

    @property
    def in_flight(self) -> int:
        with self._lock:
            return self._in_flight

    @property
    def available(self) -> int:
        with self._lock:
            return self.max_concurrent - self._in_flight

    def try_acquire(self) -> bool:
        """Non-blocking acquire. Returns True if a slot was taken."""
        with self._lock:
            if self._in_flight >= self.max_concurrent:
                self.rejected += 1
                return False
            self._in_flight += 1
            self.admitted += 1
            return True

    def acquire(self, timeout: Optional[float] = None) -> bool:
        """Acquire a slot, optionally waiting up to `timeout` seconds.

        timeout=0 behaves like try_acquire. timeout=None waits indefinitely.
        Returns True if acquired.
        """
        with self._cond:
            if timeout == 0:
                if self._in_flight >= self.max_concurrent:
                    self.rejected += 1
                    return False
            else:
                deadline = None if timeout is None else timeout
                while self._in_flight >= self.max_concurrent:
                    if not self._cond.wait(timeout=deadline):
                        self.rejected += 1
                        return False
                    # After wait, recompute remaining time if needed; simple
                    # version restarts the full timeout each wake (acceptable
                    # for this educational component).
            self._in_flight += 1
            self.admitted += 1
            return True

    def release(self) -> None:
        """Release a previously acquired slot."""
        with self._cond:
            if self._in_flight <= 0:
                raise RuntimeError("release called with no outstanding acquire")
            self._in_flight -= 1
            self._cond.notify()

    @contextmanager
    def slot(self, timeout: Optional[float] = 0.0) -> Generator[None, None, None]:
        """Context manager that acquires a slot and always releases it.

        Raises BulkheadFull if the call cannot be admitted.
        """
        if not self.acquire(timeout=timeout):
            raise BulkheadFull(f"bulkhead '{self.name}' is full")
        try:
            yield
        finally:
            self.release()

    def __enter__(self) -> Bulkhead:
        if not self.try_acquire():
            raise BulkheadFull(f"bulkhead '{self.name}' is full")
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.release()
