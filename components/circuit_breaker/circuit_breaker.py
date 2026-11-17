"""Circuit breaker with closed, open and half-open states.

Protects a dependency by short-circuiting calls after repeated failures and
probing recovery after a timeout. An injectable clock keeps tests deterministic.
"""
from __future__ import annotations

import threading
import time
from enum import Enum
from typing import Callable, TypeVar

T = TypeVar("T")
Clock = Callable[[], float]


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(Exception):
    """Raised when a call is rejected because the circuit is open."""


class CircuitBreaker:
    """Failure-counting circuit breaker.

    - CLOSED: calls pass; consecutive failures trip the circuit.
    - OPEN: calls are rejected until `recovery_timeout` elapses.
    - HALF_OPEN: a limited number of trial calls are allowed; successes close
      the circuit, a failure re-opens it.
    """

    def __init__(
        self,
        failure_threshold: int,
        recovery_timeout: float,
        success_threshold: int = 1,
        half_open_max_calls: int = 1,
        clock: Clock = time.monotonic,
    ) -> None:
        if failure_threshold <= 0 or recovery_timeout <= 0:
            raise ValueError("failure_threshold and recovery_timeout must be positive")
        if success_threshold <= 0 or half_open_max_calls <= 0:
            raise ValueError("success_threshold and half_open_max_calls must be positive")
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self.half_open_max_calls = half_open_max_calls
        self._clock = clock

        self._state = CircuitState.CLOSED
        self._failures = 0
        self._successes = 0
        self._half_open_calls = 0
        self._opened_at: float | None = None
        self._lock = threading.Lock()

    @property
    def state(self) -> CircuitState:
        with self._lock:
            self._maybe_transition()
            return self._state

    def _maybe_transition(self) -> None:
        if self._state is CircuitState.OPEN and self._opened_at is not None:
            if self._clock() - self._opened_at >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0
                self._successes = 0

    def allow(self) -> bool:
        """Return True if a call may proceed."""
        with self._lock:
            self._maybe_transition()
            if self._state is CircuitState.CLOSED:
                return True
            if self._state is CircuitState.OPEN:
                return False
            # HALF_OPEN
            if self._half_open_calls < self.half_open_max_calls:
                self._half_open_calls += 1
                return True
            return False

    def record_success(self) -> None:
        with self._lock:
            if self._state is CircuitState.HALF_OPEN:
                self._successes += 1
                if self._successes >= self.success_threshold:
                    self._state = CircuitState.CLOSED
                    self._failures = 0
                    self._successes = 0
                    self._half_open_calls = 0
                    self._opened_at = None
            else:
                self._failures = 0

    def record_failure(self) -> None:
        with self._lock:
            if self._state is CircuitState.HALF_OPEN:
                self._trip()
                return
            if self._state is CircuitState.CLOSED:
                self._failures += 1
                if self._failures >= self.failure_threshold:
                    self._trip()

    def _trip(self) -> None:
        self._state = CircuitState.OPEN
        self._opened_at = self._clock()
        self._failures = 0
        self._successes = 0
        self._half_open_calls = 0

    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute `func` if the circuit allows it; record the outcome."""
        if not self.allow():
            raise CircuitOpenError("circuit is open")
        try:
            result = func(*args, **kwargs)
        except Exception:
            self.record_failure()
            raise
        else:
            self.record_success()
            return result
