"""Connection pool with a fixed maximum size.

Reuses idle connections and creates new ones on demand up to `max_size`.
Thread-safe. Timeouts use the real clock; tests avoid waiting by using timeout=0.
"""
from __future__ import annotations

import queue
import threading
from contextlib import contextmanager
from typing import Callable, Generic, Iterator, Optional, TypeVar

T = TypeVar("T")


class PoolTimeout(Exception):
    """Raised when acquire cannot obtain a connection in time."""


class ConnectionPool(Generic[T]):
    def __init__(self, factory: Callable[[], T], max_size: int):
        if max_size <= 0:
            raise ValueError("max_size must be positive")
        if not callable(factory):
            raise TypeError("factory must be callable")
        self.factory = factory
        self.max_size = max_size
        self._available: queue.Queue[T] = queue.Queue()
        self._lock = threading.Lock()
        self._created = 0
        self._in_use = 0

    def __len__(self) -> int:
        """Number of connections currently in use."""
        return self._in_use

    @property
    def idle(self) -> int:
        return self._available.qsize()

    @property
    def total(self) -> int:
        return self._created

    def _try_create(self) -> Optional[T]:
        with self._lock:
            if self._created < self.max_size:
                conn = self.factory()
                self._created += 1
                return conn
            return None

    def acquire(self, timeout: Optional[float] = None) -> T:
        """Checkout a connection. Raises PoolTimeout if none is available in time."""
        # Fast path: idle connection.
        try:
            conn = self._available.get_nowait()
            with self._lock:
                self._in_use += 1
            return conn
        except queue.Empty:
            pass

        # Create if under capacity.
        conn = self._try_create()
        if conn is not None:
            with self._lock:
                self._in_use += 1
            return conn

        # Wait for a release.
        try:
            if timeout is None:
                conn = self._available.get()
            else:
                conn = self._available.get(timeout=timeout)
            with self._lock:
                self._in_use += 1
            return conn
        except queue.Empty:
            raise PoolTimeout("no connection available") from None

    def release(self, conn: T) -> None:
        """Return a connection to the pool."""
        with self._lock:
            if self._in_use <= 0:
                raise RuntimeError("release without matching acquire")
            self._in_use -= 1
        self._available.put(conn)

    @contextmanager
    def connection(self, timeout: Optional[float] = None) -> Iterator[T]:
        conn = self.acquire(timeout=timeout)
        try:
            yield conn
        finally:
            self.release(conn)

    def close(self) -> None:
        """Discard all idle connections. In-use connections are left to the caller."""
        while True:
            try:
                self._available.get_nowait()
                with self._lock:
                    self._created -= 1
            except queue.Empty:
                break
