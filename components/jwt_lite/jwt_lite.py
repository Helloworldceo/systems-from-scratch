"""Minimal HS256 JSON Web Token encode and verify.

Uses only the standard library. Header and payload are base64url-encoded JSON;
the signature is HMAC-SHA256 of the first two segments.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Any, Callable, Mapping, Optional

Clock = Callable[[], float]


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(s: str) -> bytes:
    padding = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + padding)


def _json_encode(obj: Mapping) -> bytes:
    # Compact separators so the signature is stable.
    return json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8")


class JWTError(Exception):
    """Base class for JWT failures."""


class InvalidTokenError(JWTError):
    """Malformed token or bad signature."""


class ExpiredTokenError(JWTError):
    """The exp claim is in the past."""


class NotYetValidError(JWTError):
    """The nbf claim is in the future."""


def encode(
    payload: Mapping[str, Any],
    secret: str | bytes,
    *,
    headers: Optional[Mapping[str, Any]] = None,
) -> str:
    """Return a compact JWT string signed with HS256."""
    if not isinstance(payload, Mapping):
        raise TypeError("payload must be a mapping")
    hdr = {"alg": "HS256", "typ": "JWT"}
    if headers:
        hdr.update(headers)
    if hdr.get("alg") != "HS256":
        raise ValueError("only HS256 is supported")
    header_b64 = _b64url_encode(_json_encode(hdr))
    payload_b64 = _b64url_encode(_json_encode(payload))
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    key = secret.encode("utf-8") if isinstance(secret, str) else secret
    sig = hmac.new(key, signing_input, hashlib.sha256).digest()
    sig_b64 = _b64url_encode(sig)
    return f"{header_b64}.{payload_b64}.{sig_b64}"


def decode(
    token: str,
    secret: str | bytes,
    *,
    algorithms: Optional[list[str]] = None,
    clock: Clock = time.time,
    leeway: float = 0.0,
) -> dict[str, Any]:
    """Verify the signature and time claims; return the payload dict.

    Raises InvalidTokenError, ExpiredTokenError or NotYetValidError.
    """
    if algorithms is None:
        algorithms = ["HS256"]
    if "HS256" not in algorithms:
        raise InvalidTokenError("HS256 not allowed")
    parts = token.split(".")
    if len(parts) != 3:
        raise InvalidTokenError("token must have three segments")
    header_b64, payload_b64, sig_b64 = parts
    try:
        header = json.loads(_b64url_decode(header_b64))
        payload = json.loads(_b64url_decode(payload_b64))
    except (json.JSONDecodeError, ValueError) as e:
        raise InvalidTokenError("invalid base64 or JSON") from e
    if not isinstance(header, dict) or header.get("alg") != "HS256":
        raise InvalidTokenError("unsupported or missing alg")
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    key = secret.encode("utf-8") if isinstance(secret, str) else secret
    expected = hmac.new(key, signing_input, hashlib.sha256).digest()
    try:
        actual = _b64url_decode(sig_b64)
    except ValueError as e:
        raise InvalidTokenError("bad signature encoding") from e
    if not hmac.compare_digest(expected, actual):
        raise InvalidTokenError("signature verification failed")
    now = clock()
    exp = payload.get("exp")
    if exp is not None:
        if not isinstance(exp, (int, float)):
            raise InvalidTokenError("exp must be a number")
        if now > exp + leeway:
            raise ExpiredTokenError("token has expired")
    nbf = payload.get("nbf")
    if nbf is not None:
        if not isinstance(nbf, (int, float)):
            raise InvalidTokenError("nbf must be a number")
        if now < nbf - leeway:
            raise NotYetValidError("token not yet valid")
    return payload
