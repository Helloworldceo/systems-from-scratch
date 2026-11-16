"""Retry a callable with exponential backoff and jitter.

After each failure the wait is min(max_delay, base_delay * 2**(attempt-1))
plus a small random jitter. The clock and sleep function are injectable so
tests stay deterministic and never call time.sleep.
"""
from __future__ import annotations

import random
import time
from typing import Any, Callable, TypeVar

T = TypeVar("T")
Clock = Callable[[], float]
Sleep = Callable[[float], None]


class Retry:
    """Retry a call up to max_attempts times on specified exceptions."""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 0.1,
        max_delay: float = 10.0,
        jitter: float = 0.1,
        exceptions: tuple[type[Exception], ...] = (Exception,),
        clock: Clock = time.monotonic,
        sleep: Sleep = time.sleep,
        rng: random.Random | None = None,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if base_delay < 0 or max_delay < 0 or jitter < 0:
            raise ValueError("delays and jitter must be non-negative")
        if max_delay < base_delay:
            raise ValueError("max_delay must be >= base_delay")
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter
        self.exceptions = exceptions
        self._clock = clock
        self._sleep = sleep
        self._rng = rng if rng is not None else random.Random()

    def _delay(self, attempt: int) -> float:
        """Delay after the given failed attempt (1-based)."""
        exp = min(self.max_delay, self.base_delay * (2 ** (attempt - 1)))
        span = self.jitter * exp
        j = self._rng.uniform(-span, span) if span > 0 else 0.0
        return max(0.0, exp + j)

    def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Call func, retrying on failure according to the policy."""
        last_exc: Exception | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                return func(*args, **kwargs)
            except self.exceptions as exc:
                last_exc = exc
                if attempt == self.max_attempts:
                    raise
                self._sleep(self._delay(attempt))
        # unreachable
        assert last_exc is not None
        raise last_exc
