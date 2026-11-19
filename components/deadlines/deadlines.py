"""Timeout and deadline propagation.

A deadline is an absolute expiration time carried with a request. Nested calls
inherit it and may only tighten it, so work stops when the caller runs out of
time. An injectable clock keeps tests deterministic.
"""
from __future__ import annotations

import time
from typing import Callable, Optional

Clock = Callable[[], float]


class DeadlineExceeded(TimeoutError):
    """Raised when a deadline has already expired."""


class Deadline:
    """An absolute deadline that can be checked and tightened."""

    def __init__(self, deadline: Optional[float], clock: Clock = time.monotonic):
        self.deadline = deadline
        self._clock = clock

    @classmethod
    def from_timeout(cls, timeout: float, clock: Clock = time.monotonic) -> Deadline:
        """Create a deadline that expires `timeout` seconds from now."""
        if timeout < 0:
            raise ValueError("timeout must be non-negative")
        if timeout == float("inf"):
            return cls(None, clock)
        return cls(clock() + timeout, clock)

    @classmethod
    def never(cls, clock: Clock = time.monotonic) -> Deadline:
        """A deadline that never expires."""
        return cls(None, clock)

    def expired(self) -> bool:
        """True if the deadline has passed (or is exactly now)."""
        if self.deadline is None:
            return False
        return self._clock() >= self.deadline

    def remaining(self) -> float:
        """Seconds left until the deadline (0 if expired, inf if none)."""
        if self.deadline is None:
            return float("inf")
        return max(0.0, self.deadline - self._clock())

    def with_timeout(self, timeout: float) -> Deadline:
        """Return a child deadline that is the earlier of this one and now+timeout.

        The child never extends the parent deadline.
        """
        if timeout < 0:
            raise ValueError("timeout must be non-negative")
        if timeout == float("inf"):
            return Deadline(self.deadline, self._clock)
        candidate = self._clock() + timeout
        if self.deadline is None:
            child = candidate
        else:
            child = min(self.deadline, candidate)
        return Deadline(child, self._clock)

    def check(self) -> None:
        """Raise DeadlineExceeded if the deadline has expired."""
        if self.expired():
            raise DeadlineExceeded("deadline exceeded")

    def __repr__(self) -> str:
        rem = self.remaining()
        if rem == float("inf"):
            return "Deadline(never)"
        return f"Deadline(remaining={rem:.3f}s)"
