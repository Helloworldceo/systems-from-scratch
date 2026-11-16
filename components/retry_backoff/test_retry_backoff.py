import random

import pytest

from retry_backoff import Retry


class FakeClock:
    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        return self.t

    def advance(self, s: float) -> None:
        self.t += s


class FakeSleep:
    def __init__(self, clock: FakeClock) -> None:
        self.clock = clock
        self.slept: list[float] = []

    def __call__(self, s: float) -> None:
        self.slept.append(s)
        self.clock.advance(s)


def test_succeeds_on_first_try_no_sleep():
    clk = FakeClock()
    slp = FakeSleep(clk)
    r = Retry(max_attempts=3, sleep=slp, clock=clk, rng=random.Random(0))
    assert r.call(lambda: 42) == 42
    assert slp.slept == []


def test_retries_then_succeeds():
    clk = FakeClock()
    slp = FakeSleep(clk)
    r = Retry(max_attempts=4, base_delay=0.1, max_delay=10, jitter=0, sleep=slp, clock=clk, rng=random.Random(0))
    calls = {"n": 0}

    def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            raise ValueError("boom")
        return "ok"

    assert r.call(flaky) == "ok"
    assert calls["n"] == 3
    assert len(slp.slept) == 2
    assert slp.slept == pytest.approx([0.1, 0.2])


def test_exhausts_attempts_and_raises():
    clk = FakeClock()
    slp = FakeSleep(clk)
    r = Retry(max_attempts=3, base_delay=0.1, jitter=0, sleep=slp, clock=clk)
    calls = {"n": 0}

    def always_fail() -> None:
        calls["n"] += 1
        raise RuntimeError("nope")

    with pytest.raises(RuntimeError, match="nope"):
        r.call(always_fail)
    assert calls["n"] == 3
    assert len(slp.slept) == 2


def test_does_not_retry_unrelated_exceptions():
    clk = FakeClock()
    slp = FakeSleep(clk)
    r = Retry(max_attempts=3, exceptions=(ValueError,), sleep=slp, clock=clk)

    def boom() -> None:
        raise TypeError("wrong")

    with pytest.raises(TypeError):
        r.call(boom)
    assert slp.slept == []


def test_jitter_and_cap():
    clk = FakeClock()
    slp = FakeSleep(clk)
    rng = random.Random(1)
    r = Retry(
        max_attempts=5,
        base_delay=1.0,
        max_delay=3.0,
        jitter=0.5,
        sleep=slp,
        clock=clk,
        rng=rng,
    )
    calls = {"n": 0}

    def fail() -> None:
        calls["n"] += 1
        raise Exception("x")

    with pytest.raises(Exception):
        r.call(fail)
    assert calls["n"] == 5
    assert len(slp.slept) == 4
    # delays: ~1, ~2, ~3 (capped), ~3 (capped)
    assert all(0.5 <= d <= 4.5 for d in slp.slept)  # loose bounds with jitter
    assert slp.slept[2] <= 4.5  # capped around 3


def test_invalid_args():
    with pytest.raises(ValueError):
        Retry(max_attempts=0)
    with pytest.raises(ValueError):
        Retry(base_delay=-1)
    with pytest.raises(ValueError):
        Retry(base_delay=5, max_delay=1)
