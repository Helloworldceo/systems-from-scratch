"""Two classic rate limiters: token bucket and sliding window log.

Both accept an injectable clock so they can be tested deterministically.
"""
from __future__ import annotations

import threading
import time
from collections import deque
from typing import Callable

Clock = Callable[[], float]


class TokenBucket:
    """Allows bursts up to `capacity`, refilling at `rate` tokens per second."""

    def __init__(self, capacity: float, rate: float, clock: Clock = time.monotonic):
        if capacity <= 0 or rate <= 0:
            raise ValueError("capacity and rate must be positive")
        self.capacity = capacity
        self.rate = rate
        self._clock = clock
        self._tokens = capacity
        self._last = clock()
        self._lock = threading.Lock()

    def _refill(self) -> None:
        now = self._clock()
        self._tokens = min(self.capacity, self._tokens + (now - self._last) * self.rate)
        self._last = now

    def allow(self, cost: float = 1.0) -> bool:
        with self._lock:
            self._refill()
            if self._tokens >= cost:
                self._tokens -= cost
                return True
            return False

    @property
    def tokens(self) -> float:
        with self._lock:
            self._refill()
            return self._tokens


class SlidingWindowLog:
    """At most `limit` requests in any rolling `window` seconds."""

    def __init__(self, limit: int, window: float, clock: Clock = time.monotonic):
        if limit <= 0 or window <= 0:
            raise ValueError("limit and window must be positive")
        self.limit = limit
        self.window = window
        self._clock = clock
        self._log: deque[float] = deque()
        self._lock = threading.Lock()

    def allow(self) -> bool:
        with self._lock:
            now = self._clock()
            while self._log and self._log[0] <= now - self.window:
                self._log.popleft()
            if len(self._log) < self.limit:
                self._log.append(now)
                return True
            return False

    def retry_after(self) -> float:
        """Seconds until the next request would be allowed (0 if allowed now)."""
        with self._lock:
            now = self._clock()
            if len(self._log) < self.limit:
                return 0.0
            return max(0.0, self._log[0] + self.window - now)
