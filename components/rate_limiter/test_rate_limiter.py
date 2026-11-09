import pytest

from rate_limiter import SlidingWindowLog, TokenBucket


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t

    def advance(self, s):
        self.t += s


def test_token_bucket_allows_burst_then_blocks():
    clk = FakeClock()
    tb = TokenBucket(capacity=3, rate=1, clock=clk)
    assert [tb.allow() for _ in range(4)] == [True, True, True, False]


def test_token_bucket_refills_over_time_up_to_capacity():
    clk = FakeClock()
    tb = TokenBucket(capacity=2, rate=2, clock=clk)
    tb.allow(); tb.allow()
    assert not tb.allow()
    clk.advance(0.5)                 # +1 token
    assert tb.allow()
    clk.advance(100)
    assert tb.tokens == pytest.approx(2)


def test_token_bucket_cost():
    tb = TokenBucket(capacity=5, rate=1, clock=FakeClock())
    assert tb.allow(cost=5)
    assert not tb.allow(cost=1)


def test_sliding_window_limits_and_recovers():
    clk = FakeClock()
    sw = SlidingWindowLog(limit=2, window=10, clock=clk)
    assert sw.allow() and sw.allow()
    assert not sw.allow()
    assert sw.retry_after() == pytest.approx(10)
    clk.advance(10)
    assert sw.allow()


def test_sliding_window_is_rolling_not_fixed():
    clk = FakeClock()
    sw = SlidingWindowLog(limit=2, window=10, clock=clk)
    sw.allow()            # t=0
    clk.advance(9)
    sw.allow()            # t=9
    clk.advance(2)        # t=11: t=0 expired, t=9 still inside
    assert sw.allow()
    assert not sw.allow()


@pytest.mark.parametrize("cls,args", [(TokenBucket, (0, 1)), (SlidingWindowLog, (1, 0))])
def test_invalid_args(cls, args):
    with pytest.raises(ValueError):
        cls(*args)
