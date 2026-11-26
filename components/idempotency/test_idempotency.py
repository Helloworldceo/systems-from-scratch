import pytest

from idempotency import IdempotencyConflict, IdempotencyHandler


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t

    def advance(self, seconds: float):
        self.t += seconds


def test_first_execution_runs_and_caches():
    calls = []

    def op():
        calls.append(1)
        return "ok"

    h = IdempotencyHandler(ttl=60, clock=FakeClock())
    assert h.execute("k1", op) == "ok"
    assert h.execute("k1", op) == "ok"
    assert calls == [1]
    assert h.get("k1") == "ok"
    assert "k1" in h


def test_different_keys_are_independent():
    h = IdempotencyHandler(ttl=60, clock=FakeClock())
    assert h.execute("a", lambda: 1) == 1
    assert h.execute("b", lambda: 2) == 2
    assert h.execute("a", lambda: 99) == 1
    assert h.get("b") == 2


def test_exceptions_are_not_cached():
    attempts = []

    def op():
        attempts.append(1)
        if len(attempts) == 1:
            raise RuntimeError("boom")
        return "recovered"

    h = IdempotencyHandler(ttl=60, clock=FakeClock())
    with pytest.raises(RuntimeError):
        h.execute("k", op)
    assert h.get("k") is None
    assert h.execute("k", op) == "recovered"
    assert len(attempts) == 2


def test_ttl_expiry_allows_reexecution():
    clk = FakeClock()
    h = IdempotencyHandler(ttl=10, clock=clk)
    runs = []

    def op():
        runs.append(1)
        return len(runs)

    assert h.execute("k", op) == 1
    clk.advance(9)
    assert h.execute("k", op) == 1  # still cached
    clk.advance(2)  # now expired
    assert h.execute("k", op) == 2
    assert len(runs) == 2


def test_in_progress_conflict():
    h = IdempotencyHandler(ttl=60, clock=FakeClock())

    def outer():
        with pytest.raises(IdempotencyConflict):
            h.execute("k", lambda: "inner")
        return "done"

    assert h.execute("k", outer) == "done"
    # After completion the nested call is no longer in progress; subsequent is cached.
    assert h.execute("k", lambda: "never") == "done"


def test_forget_and_invalid_ttl():
    h = IdempotencyHandler(ttl=60, clock=FakeClock())
    h.execute("k", lambda: 42)
    assert h.forget("k") is True
    assert h.get("k") is None
    assert h.forget("missing") is False

    with pytest.raises(ValueError):
        IdempotencyHandler(ttl=0)
    with pytest.raises(ValueError):
        IdempotencyHandler(ttl=-1)
