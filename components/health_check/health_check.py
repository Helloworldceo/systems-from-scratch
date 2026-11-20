"""Health checker with liveness and readiness probes.

Liveness answers "is the process alive and should not be restarted?".
Readiness answers "is the process ready to accept traffic?".
Checks are named callables that return True when healthy; exceptions count as
failure. An empty set of checks is considered healthy.
"""
from __future__ import annotations

from typing import Callable, Dict

CheckFn = Callable[[], bool]


class HealthStatus:
    """Result of running a set of checks."""

    def __init__(self, healthy: bool, checks: Dict[str, bool]):
        self.healthy = healthy
        self.checks = checks

    def __bool__(self) -> bool:
        return self.healthy

    def __repr__(self) -> str:
        return f"HealthStatus(healthy={self.healthy}, checks={self.checks})"


class HealthChecker:
    """Registry of liveness and readiness checks."""

    def __init__(self) -> None:
        self._liveness: Dict[str, CheckFn] = {}
        self._readiness: Dict[str, CheckFn] = {}

    def add_liveness(self, name: str, check: CheckFn) -> None:
        """Register a liveness check under `name`."""
        self._validate(name, check)
        self._liveness[name] = check

    def add_readiness(self, name: str, check: CheckFn) -> None:
        """Register a readiness check under `name`."""
        self._validate(name, check)
        self._readiness[name] = check

    def remove_liveness(self, name: str) -> bool:
        """Remove a liveness check. Returns True if it existed."""
        return self._liveness.pop(name, None) is not None

    def remove_readiness(self, name: str) -> bool:
        """Remove a readiness check. Returns True if it existed."""
        return self._readiness.pop(name, None) is not None

    def liveness(self) -> HealthStatus:
        """Run all liveness checks."""
        return self._run(self._liveness)

    def readiness(self) -> HealthStatus:
        """Run all readiness checks."""
        return self._run(self._readiness)

    def _validate(self, name: str, check: CheckFn) -> None:
        if not isinstance(name, str) or not name:
            raise ValueError("name must be a non-empty string")
        if not callable(check):
            raise ValueError("check must be callable")

    def _run(self, checks: Dict[str, CheckFn]) -> HealthStatus:
        results: Dict[str, bool] = {}
        for name, fn in checks.items():
            try:
                results[name] = bool(fn())
            except Exception:
                results[name] = False
        healthy = all(results.values()) if results else True
        return HealthStatus(healthy, results)
