import pytest

from jwt_lite import (
    ExpiredTokenError,
    InvalidTokenError,
    NotYetValidError,
    decode,
    encode,
)


class FakeClock:
    def __init__(self, t: float = 1_000_000.0):
        self.t = t

    def __call__(self) -> float:
        return self.t

    def advance(self, s: float) -> None:
        self.t += s


def test_round_trip():
    secret = "test-secret"
    payload = {"sub": "user42", "role": "admin"}
    token = encode(payload, secret)
    assert decode(token, secret) == payload


def test_wrong_secret_rejected():
    token = encode({"a": 1}, "good")
    with pytest.raises(InvalidTokenError):
        decode(token, "bad")


def test_tampered_payload_rejected():
    secret = "s"
    token = encode({"v": 1}, secret)
    # Flip a character in the payload segment.
    parts = token.split(".")
    bad = parts[1][:-1] + ("A" if parts[1][-1] != "A" else "B")
    tampered = ".".join([parts[0], bad, parts[2]])
    with pytest.raises(InvalidTokenError):
        decode(tampered, secret)


def test_exp_claim_with_fake_clock():
    clk = FakeClock(1000)
    token = encode({"exp": 1010}, "sec")
    assert decode(token, "sec", clock=clk)["exp"] == 1010
    clk.advance(20)
    with pytest.raises(ExpiredTokenError):
        decode(token, "sec", clock=clk)


def test_nbf_claim_with_fake_clock():
    clk = FakeClock(1000)
    token = encode({"nbf": 1010}, "sec")
    with pytest.raises(NotYetValidError):
        decode(token, "sec", clock=clk)
    clk.advance(15)
    assert decode(token, "sec", clock=clk)["nbf"] == 1010


def test_malformed_token():
    with pytest.raises(InvalidTokenError):
        decode("not.a.jwt.token", "x")
    with pytest.raises(InvalidTokenError):
        decode("onlyone", "x")
