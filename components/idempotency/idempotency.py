"""Idempotency-key handler for safe retries of non-idempotent operations.

The first successful execution of an operation under a given key is stored
(with a TTL). Later calls with the same key return the cached result instead
of re-executing. Concurrent in-progress requests for the same key are rejected.
An injectable clock keeps tests deterministic.
"""
from __future__ import annotations

import threading
import time
from typing import Any, Callable, Generic, Hashable, Optional, TypeVar

K = TypeVar("K", bound=Hashable)
R = TypeVar("R")

Clock = Callable[[], float]


class IdempotencyConflict(Exception):
    """Raised when a request with the same key is already in progress."""


class IdempotencyHandler(Generic[K]):
    """Stores successful results of keyed operations so retries are safe.

    Only successful (non-raising) results are cached. Failures can be retried.
    Expired entries are removed on access. All public methods are thread-safe.
    """

    def __init__(self, ttl: float = 86400.0, clock: Clock = time.monotonic):
        if ttl <= 0:
            raise ValueError("ttl must be positive")
        self.ttl = ttl
        self._clock = clock
        # key -> (expiry, result)
        self._completed: dict[K, tuple[float, Any]] = {}
        self._in_progress: set[K] = set()
        self._lock = threading.RLock()

    def execute(self, key: K, operation: Callable[[], R]) -> R:
        """Run `operation` once per key; return the cached result on retries.

        Raises IdempotencyConflict if another call with the same key is still
        running. Exceptions from `operation` are not cached.
        """
        with self._lock:
            self._cleanup()
            if key in self._completed:
                return self._completed[key][1]
            if key in self._in_progress:
                raise IdempotencyConflict(f"key {key!r} is already in progress")
            self._in_progress.add(key)

        try:
            result = operation()
        except BaseException:
            with self._lock:
                self._in_progress.discard(key)
            raise

        with self._lock:
            self._in_progress.discard(key)
            expiry = self._clock() + self.ttl
            self._completed[key] = (expiry, result)
        return result

    def get(self, key: K, default: Optional[Any] = None) -> Optional[Any]:
        """Return the cached result if the key has completed and is not expired."""
        with self._lock:
            self._cleanup()
            entry = self._completed.get(key)
            if entry is None:
                return default
            return entry[1]

    def is_completed(self, key: K) -> bool:
        """True if a successful result for this key is still cached."""
        return self.get(key) is not None

    def forget(self, key: K) -> bool:
        """Remove a completed or in-progress entry. Returns True if something was removed."""
        with self._lock:
            removed = False
            if key in self._completed:
                del self._completed[key]
                removed = True
            if key in self._in_progress:
                self._in_progress.discard(key)
                removed = True
            return removed

    def cleanup(self) -> int:
        """Remove all expired completed entries. Returns the number removed."""
        with self._lock:
            return self._cleanup()

    def _cleanup(self) -> int:
        now = self._clock()
        expired = [k for k, (exp, _) in self._completed.items() if exp <= now]
        for k in expired:
            del self._completed[k]
        return len(expired)

    def __len__(self) -> int:
        """Number of currently cached (non-expired) results."""
        with self._lock:
            self._cleanup()
            return len(self._completed)

    def __contains__(self, key: K) -> bool:
        return self.is_completed(key)
