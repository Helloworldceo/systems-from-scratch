import pytest

from health_check import HealthChecker, HealthStatus


def test_empty_is_healthy():
    hc = HealthChecker()
    assert hc.liveness().healthy
    assert hc.readiness().healthy
    assert bool(hc.liveness())


def test_all_checks_pass():
    hc = HealthChecker()
    hc.add_liveness("self", lambda: True)
    hc.add_readiness("db", lambda: True)
    hc.add_readiness("cache", lambda: True)
    live = hc.liveness()
    ready = hc.readiness()
    assert live.healthy and live.checks == {"self": True}
    assert ready.healthy and ready.checks == {"db": True, "cache": True}


def test_readiness_fails_while_liveness_ok():
    hc = HealthChecker()
    hc.add_liveness("process", lambda: True)
    hc.add_readiness("db", lambda: False)
    assert hc.liveness().healthy
    status = hc.readiness()
    assert not status.healthy
    assert status.checks == {"db": False}


def test_exception_counts_as_failure():
    hc = HealthChecker()
    def boom():
        raise RuntimeError("connection refused")
    hc.add_readiness("db", boom)
    status = hc.readiness()
    assert not status.healthy
    assert status.checks["db"] is False


def test_remove_check():
    hc = HealthChecker()
    hc.add_liveness("x", lambda: False)
    assert not hc.liveness().healthy
    assert hc.remove_liveness("x") is True
    assert hc.remove_liveness("x") is False
    assert hc.liveness().healthy


def test_invalid_registration():
    hc = HealthChecker()
    with pytest.raises(ValueError):
        hc.add_liveness("", lambda: True)
    with pytest.raises(ValueError):
        hc.add_readiness("ok", None)  # type: ignore
    with pytest.raises(ValueError):
        hc.add_liveness(123, lambda: True)  # type: ignore


def test_status_repr_and_bool():
    s = HealthStatus(True, {"a": True})
    assert bool(s)
    assert "healthy=True" in repr(s)
    s2 = HealthStatus(False, {})
    assert not s2
