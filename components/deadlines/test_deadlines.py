import pytest

from deadlines import Deadline, DeadlineExceeded


class FakeClock:
    def __init__(self, t=0.0):
        self.t = t

    def __call__(self):
        return self.t

    def advance(self, s):
        self.t += s


def test_from_timeout_and_remaining():
    clk = FakeClock()
    d = Deadline.from_timeout(10, clock=clk)
    assert d.remaining() == pytest.approx(10)
    assert not d.expired()
    clk.advance(4)
    assert d.remaining() == pytest.approx(6)
    clk.advance(6)
    assert d.expired()
    assert d.remaining() == 0


def test_never_deadline():
    d = Deadline.never()
    assert not d.expired()
    assert d.remaining() == float("inf")
    d.check()  # does not raise


def test_child_tightens_deadline():
    clk = FakeClock()
    parent = Deadline.from_timeout(10, clock=clk)
    child = parent.with_timeout(3)
    assert child.remaining() == pytest.approx(3)
    clk.advance(4)
    assert child.expired()
    assert not parent.expired()  # parent still has 6s


def test_child_cannot_extend_parent():
    clk = FakeClock()
    parent = Deadline.from_timeout(5, clock=clk)
    child = parent.with_timeout(20)
    assert child.deadline == parent.deadline
    assert child.remaining() == pytest.approx(5)
    clk.advance(5)
    assert child.expired() and parent.expired()


def test_check_raises_when_expired():
    clk = FakeClock()
    d = Deadline.from_timeout(1, clock=clk)
    d.check()
    clk.advance(1)
    with pytest.raises(DeadlineExceeded):
        d.check()


def test_invalid_timeout():
    with pytest.raises(ValueError):
        Deadline.from_timeout(-1)
    d = Deadline.never()
    with pytest.raises(ValueError):
        d.with_timeout(-0.1)


def test_zero_timeout_expires_immediately():
    clk = FakeClock()
    d = Deadline.from_timeout(0, clock=clk)
    assert d.expired()
    assert d.remaining() == 0
    with pytest.raises(DeadlineExceeded):
        d.check()
