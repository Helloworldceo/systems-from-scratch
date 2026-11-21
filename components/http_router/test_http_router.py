import pytest

from http_router import HTTPRouter


def test_static_route_and_root():
    r = HTTPRouter()
    calls = []

    def root():
        calls.append("root")
        return "ok"

    def health():
        return "up"

    r.add("GET", "/", root)
    r.add("GET", "/health", health)
    assert r.match("GET", "/")[0]() == "ok"
    assert r.match("get", "/health")[0]() == "up"
    assert calls == ["root"]


def test_path_parameters_extracted():
    r = HTTPRouter()

    def show(user_id, post_id):
        return (user_id, post_id)

    r.add("GET", "/users/{user_id}/posts/{post_id}", show)
    handler, params = r.match("GET", "/users/42/posts/7")
    assert params == {"user_id": "42", "post_id": "7"}
    assert handler(**params) == ("42", "7")


def test_method_and_path_mismatch():
    r = HTTPRouter()
    r.add("POST", "/items", lambda: None)
    assert r.match("GET", "/items") is None
    assert r.match("POST", "/missing") is None
    assert r.match("POST", "/items/extra") is None


def test_first_match_wins_and_order():
    r = HTTPRouter()
    r.add("GET", "/files/{name}", lambda **kw: "param")
    r.add("GET", "/files/static", lambda: "static")  # never reached
    handler, params = r.match("GET", "/files/static")
    assert handler(**params) == "param"
    assert params == {"name": "static"}


def test_decorator_and_multiple_methods():
    r = HTTPRouter()

    @r.route("PUT", "/kv/{key}")
    def put(key):
        return f"set {key}"

    @r.route("DELETE", "/kv/{key}")
    def delete(key):
        return f"del {key}"

    h, p = r.match("PUT", "/kv/foo")
    assert h(**p) == "set foo"
    h, p = r.match("DELETE", "/kv/bar")
    assert h(**p) == "del bar"
    assert len(r) == 2


def test_invalid_patterns_and_handler():
    r = HTTPRouter()
    with pytest.raises(ValueError):
        r.add("GET", "no-leading-slash", lambda: None)
    with pytest.raises(ValueError):
        r.add("GET", "/a/{}", lambda: None)
    with pytest.raises(ValueError):
        r.add("GET", "/a/{id}/{id}", lambda: None)
    with pytest.raises(ValueError):
        r.add("GET", "/a/{1bad}", lambda: None)
    with pytest.raises(ValueError):
        r.add("GET", "/a//b", lambda: None)
    with pytest.raises(TypeError):
        r.add("GET", "/ok", None)
