"""A simple fixed-size thread pool for running callables concurrently.

Workers pull tasks from a shared queue. Submit returns a Future that can be
waited on for the result or exception. Shutdown drains remaining work.
"""
from __future__ import annotations

import queue
import threading
from typing import Any, Callable, Generic, Optional, TypeVar

T = TypeVar("T")


class Future(Generic[T]):
    """A simple future that holds the result or exception of a submitted task."""

    def __init__(self) -> None:
        self._event = threading.Event()
        self._result: Optional[T] = None
        self._exception: Optional[BaseException] = None

    def set_result(self, result: T) -> None:
        self._result = result
        self._event.set()

    def set_exception(self, exc: BaseException) -> None:
        self._exception = exc
        self._event.set()

    def done(self) -> bool:
        return self._event.is_set()

    def result(self, timeout: Optional[float] = None) -> T:
        if not self._event.wait(timeout):
            raise TimeoutError("future timed out")
        if self._exception is not None:
            raise self._exception
        return self._result  # type: ignore[return-value]

    def exception(self, timeout: Optional[float] = None) -> Optional[BaseException]:
        if not self._event.wait(timeout):
            raise TimeoutError("future timed out")
        return self._exception


class ThreadPool:
    """Fixed number of worker threads processing a task queue."""

    def __init__(self, num_workers: int, max_queue_size: int = 0) -> None:
        if num_workers <= 0:
            raise ValueError("num_workers must be positive")
        if max_queue_size < 0:
            raise ValueError("max_queue_size must be non-negative")
        self.num_workers = num_workers
        self._queue: queue.Queue[Optional[tuple[Callable[..., Any], tuple, dict, Future]]] = (
            queue.Queue(maxsize=max_queue_size)
        )
        self._workers: list[threading.Thread] = []
        self._shutdown = False
        self._lock = threading.Lock()
        for i in range(num_workers):
            t = threading.Thread(target=self._worker, name=f"worker-{i}", daemon=True)
            t.start()
            self._workers.append(t)

    def _worker(self) -> None:
        while True:
            item = self._queue.get()
            if item is None:  # sentinel
                self._queue.task_done()
                break
            fn, args, kwargs, future = item
            try:
                result = fn(*args, **kwargs)
                future.set_result(result)
            except BaseException as e:  # noqa: BLE001
                future.set_exception(e)
            finally:
                self._queue.task_done()

    def submit(self, fn: Callable[..., T], *args: Any, **kwargs: Any) -> Future[T]:
        """Submit a callable; return a Future for its result."""
        with self._lock:
            if self._shutdown:
                raise RuntimeError("cannot submit to a shut-down pool")
            future: Future[T] = Future()
            self._queue.put((fn, args, kwargs, future))
            return future

    def map(self, fn: Callable[..., T], *iterables: Any) -> list[T]:
        """Apply fn to each tuple of arguments; return results in order."""
        futures = [self.submit(fn, *args) for args in zip(*iterables)]
        return [f.result() for f in futures]

    def shutdown(self, wait: bool = True) -> None:
        """Stop accepting new work and optionally wait for in-flight tasks."""
        with self._lock:
            if self._shutdown:
                return
            self._shutdown = True
            for _ in self._workers:
                self._queue.put(None)
        if wait:
            for t in self._workers:
                t.join()
            self._queue.join()

    def __enter__(self) -> ThreadPool:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.shutdown(wait=True)
