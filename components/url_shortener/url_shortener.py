"""URL shortener with base62 encoding and collision handling.

Maps long URLs to short codes using a counter encoded in base62.
Handles collisions by retrying with the next counter value.
"""
from __future__ import annotations

from typing import Optional


class URLShortener:
    """In-memory URL shortener.

    Short codes are base62 encodings of a monotonic counter.
    Duplicate long URLs reuse the existing short code.
    """

    _ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    _BASE = len(_ALPHABET)

    def __init__(self, domain: str = "https://s.example/") -> None:
        if not domain:
            raise ValueError("domain must be non-empty")
        self.domain = domain.rstrip("/") + "/"
        self._short_to_long: dict[str, str] = {}
        self._long_to_short: dict[str, str] = {}
        self._counter = 0

    def _encode(self, n: int) -> str:
        if n == 0:
            return self._ALPHABET[0]
        chars = []
        while n:
            n, rem = divmod(n, self._BASE)
            chars.append(self._ALPHABET[rem])
        return "".join(reversed(chars))

    def shorten(self, long_url: str) -> str:
        """Return a short URL for long_url. Reuses existing code if present."""
        if not long_url or not isinstance(long_url, str):
            raise ValueError("long_url must be a non-empty string")
        existing = self._long_to_short.get(long_url)
        if existing is not None:
            return self.domain + existing
        # Find a free short code (collision handling).
        while True:
            self._counter += 1
            code = self._encode(self._counter)
            if code not in self._short_to_long:
                break
        self._short_to_long[code] = long_url
        self._long_to_short[long_url] = code
        return self.domain + code

    def expand(self, short_url: str) -> Optional[str]:
        """Return the original long URL, or None if unknown."""
        if not short_url or not isinstance(short_url, str):
            return None
        if short_url.startswith(self.domain):
            code = short_url[len(self.domain):]
        else:
            code = short_url.lstrip("/")
        return self._short_to_long.get(code)

    def __len__(self) -> int:
        return len(self._short_to_long)
