"""In-memory session store with per-session TTL.

Sessions expire after their TTL and are cleaned on access or via an explicit
sweep. An injectable clock keeps tests deterministic.
"""
from __future__ import annotations

import secrets
import threading
import time
from typing import Any, Callable, Generic, Hashable, Optional, TypeVar

Clock = Callable[[], float]
K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


class SessionStore(Generic[K, V]):
    """Stores sessions identified by opaque keys with an absolute expiry time.

    `default_ttl` is the lifetime in seconds for new sessions unless overridden.
    Expired sessions are treated as missing. All operations are O(1) amortized.
    """

    def __init__(self, default_ttl: float, clock: Clock = time.monotonic):
        if default_ttl <= 0:
            raise ValueError("default_ttl must be positive")
        self.default_ttl = default_ttl
        self._clock = clock
        self._sessions: dict[K, tuple[V, float]] = {}
        self._lock = threading.RLock()

    def create(self, value: V, ttl: Optional[float] = None, key: Optional[K] = None) -> K:
        """Create a new session and return its key.

        If `key` is omitted a cryptographically secure random key is generated.
        """
        if ttl is not None and ttl <= 0:
            raise ValueError("ttl must be positive")
        with self._lock:
            if key is None:
                # Generate until unused (collision is extremely unlikely).
                while True:
                    key = secrets.token_urlsafe(16)  # type: ignore[assignment]
                    if key not in self._sessions:
                        break
            elif key in self._sessions and self._is_live(self._sessions[key]):
                raise ValueError("session key already exists")
            expiry = self._clock() + (ttl if ttl is not None else self.default_ttl)
            self._sessions[key] = (value, expiry)
            return key

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """Return the session value or `default` if missing or expired."""
        with self._lock:
            entry = self._sessions.get(key)
            if entry is None or not self._is_live(entry):
                if entry is not None:
                    del self._sessions[key]
                return default
            return entry[0]

    def set(self, key: K, value: V, ttl: Optional[float] = None) -> None:
        """Create or replace a session, resetting its expiry."""
        if ttl is not None and ttl <= 0:
            raise ValueError("ttl must be positive")
        with self._lock:
            expiry = self._clock() + (ttl if ttl is not None else self.default_ttl)
            self._sessions[key] = (value, expiry)

    def delete(self, key: K) -> bool:
        """Remove a session. Returns True if it existed (even if expired)."""
        with self._lock:
            return self._sessions.pop(key, None) is not None

    def renew(self, key: K, ttl: Optional[float] = None) -> bool:
        """Extend the expiry of an existing live session. Returns False if missing/expired."""
        if ttl is not None and ttl <= 0:
            raise ValueError("ttl must be positive")
        with self._lock:
            entry = self._sessions.get(key)
            if entry is None or not self._is_live(entry):
                if entry is not None:
                    del self._sessions[key]
                return False
            value, _ = entry
            new_expiry = self._clock() + (ttl if ttl is not None else self.default_ttl)
            self._sessions[key] = (value, new_expiry)
            return True

    def cleanup(self) -> int:
        """Remove all expired sessions. Returns the number removed."""
        with self._lock:
            now = self._clock()
            expired = [k for k, (_, exp) in self._sessions.items() if exp <= now]
            for k in expired:
                del self._sessions[k]
            return len(expired)

    def __len__(self) -> int:
        """Number of currently live sessions (expired ones are not counted)."""
        with self._lock:
            self.cleanup()
            return len(self._sessions)

    def __contains__(self, key: K) -> bool:
        return self.get(key) is not None

    def _is_live(self, entry: tuple[V, float]) -> bool:
        return entry[1] > self._clock()

    @property
    def size(self) -> int:
        """Alias for len() that forces a cleanup."""
        return len(self)
