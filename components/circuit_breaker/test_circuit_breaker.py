import pytest

from circuit_breaker import CircuitBreaker, CircuitOpenError, CircuitState


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t

    def advance(self, s):
        self.t += s


def test_starts_closed_and_passes_calls():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=10, clock=FakeClock())
    assert cb.state is CircuitState.CLOSED
    assert cb.call(lambda: 42) == 42
    assert cb.state is CircuitState.CLOSED


def test_trips_open_after_failure_threshold():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=10, clock=FakeClock())

    def boom():
        raise RuntimeError("fail")

    with pytest.raises(RuntimeError):
        cb.call(boom)
    assert cb.state is CircuitState.CLOSED
    with pytest.raises(RuntimeError):
        cb.call(boom)
    assert cb.state is CircuitState.OPEN
    with pytest.raises(CircuitOpenError):
        cb.call(lambda: 1)


def test_opens_to_half_open_after_timeout():
    clk = FakeClock()
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout=5, clock=clk)
    with pytest.raises(RuntimeError):
        cb.call(lambda: (_ for _ in ()).throw(RuntimeError()))
    assert cb.state is CircuitState.OPEN
    clk.advance(4.9)
    assert cb.state is CircuitState.OPEN
    clk.advance(0.2)
    assert cb.state is CircuitState.HALF_OPEN


def test_half_open_success_closes_circuit():
    clk = FakeClock()
    cb = CircuitBreaker(
        failure_threshold=1,
        recovery_timeout=5,
        success_threshold=1,
        clock=clk,
    )
    with pytest.raises(RuntimeError):
        cb.call(lambda: (_ for _ in ()).throw(RuntimeError()))
    clk.advance(5)
    assert cb.state is CircuitState.HALF_OPEN
    assert cb.call(lambda: "ok") == "ok"
    assert cb.state is CircuitState.CLOSED
    assert cb.call(lambda: 1) == 1


def test_half_open_failure_reopens():
    clk = FakeClock()
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout=5, clock=clk)
    with pytest.raises(RuntimeError):
        cb.call(lambda: (_ for _ in ()).throw(RuntimeError()))
    clk.advance(5)
    assert cb.state is CircuitState.HALF_OPEN
    with pytest.raises(RuntimeError):
        cb.call(lambda: (_ for _ in ()).throw(RuntimeError()))
    assert cb.state is CircuitState.OPEN


def test_success_resets_failure_count():
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=10, clock=FakeClock())

    def boom():
        raise RuntimeError()

    with pytest.raises(RuntimeError):
        cb.call(boom)
    with pytest.raises(RuntimeError):
        cb.call(boom)
    assert cb.call(lambda: 1) == 1
    with pytest.raises(RuntimeError):
        cb.call(boom)
    assert cb.state is CircuitState.CLOSED  # only 1 consecutive failure


def test_invalid_args():
    with pytest.raises(ValueError):
        CircuitBreaker(0, 1)
    with pytest.raises(ValueError):
        CircuitBreaker(1, 0)
