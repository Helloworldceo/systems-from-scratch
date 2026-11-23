import pytest

from url_shortener import URLShortener


def test_shorten_and_expand():
    s = URLShortener()
    short = s.shorten("https://example.com/very/long/path")
    assert short.startswith("https://s.example/")
    assert s.expand(short) == "https://example.com/very/long/path"
    assert s.expand(short.split("/")[-1]) == "https://example.com/very/long/path"


def test_same_url_returns_same_short():
    s = URLShortener()
    a = s.shorten("https://example.com/a")
    b = s.shorten("https://example.com/a")
    assert a == b
    assert len(s) == 1


def test_different_urls_different_shorts():
    s = URLShortener()
    a = s.shorten("https://example.com/a")
    b = s.shorten("https://example.com/b")
    assert a != b
    assert s.expand(a) != s.expand(b)


def test_expand_unknown_returns_none():
    s = URLShortener()
    assert s.expand("https://s.example/missing") is None
    assert s.expand("missing") is None
    assert s.expand("") is None


def test_invalid_long_url():
    s = URLShortener()
    with pytest.raises(ValueError):
        s.shorten("")
    with pytest.raises(ValueError):
        s.shorten(None)  # type: ignore[arg-type]


def test_collision_handling():
    s = URLShortener()
    # Force a collision by pre-inserting the next code.
    s._counter = 0
    next_code = s._encode(1)
    s._short_to_long[next_code] = "https://taken.example"
    short = s.shorten("https://new.example")
    assert short.endswith(s._encode(2))
    assert s.expand(short) == "https://new.example"
    assert len(s) == 2


def test_custom_domain():
    s = URLShortener(domain="http://go/")
    short = s.shorten("https://example.com")
    assert short.startswith("http://go/")
    assert s.expand(short) == "https://example.com"
