import pytest

from middleware import MiddlewareChain


def test_no_middleware_calls_final():
    chain = MiddlewareChain()
    calls = []

    def final(req):
        calls.append(req)
        return {"status": 200, "body": req.get("path", "/")}

    resp = chain.handle({"path": "/ok"}, final)
    assert resp == {"status": 200, "body": "/ok"}
    assert calls == [{"path": "/ok"}]
    assert len(chain) == 0


def test_middleware_modifies_request_before_next():
    chain = MiddlewareChain()

    def add_header(req, nxt):
        req = dict(req)
        req["headers"] = {"x-trace": "1"}
        return nxt(req)

    def final(req):
        return {"seen": req.get("headers")}

    chain.use(add_header)
    assert chain.handle({}, final) == {"seen": {"x-trace": "1"}}


def test_middleware_can_short_circuit():
    chain = MiddlewareChain()
    reached = []

    def auth(req, nxt):
        if req.get("user") is None:
            return {"status": 401, "body": "unauthorized"}
        return nxt(req)

    def final(req):
        reached.append(True)
        return {"status": 200}

    chain.use(auth)
    assert chain.handle({}, final) == {"status": 401, "body": "unauthorized"}
    assert reached == []
    assert chain.handle({"user": "alice"}, final) == {"status": 200}
    assert reached == [True]


def test_onion_order_of_execution():
    chain = MiddlewareChain()
    log = []

    def outer(req, nxt):
        log.append("outer-before")
        resp = nxt(req)
        log.append("outer-after")
        return resp

    def inner(req, nxt):
        log.append("inner-before")
        resp = nxt(req)
        log.append("inner-after")
        return resp

    def final(req):
        log.append("final")
        return {"ok": True}

    chain.use(outer)
    chain.use(inner)
    assert chain.handle({}, final) == {"ok": True}
    assert log == [
        "outer-before",
        "inner-before",
        "final",
        "inner-after",
        "outer-after",
    ]


def test_middleware_transforms_response():
    chain = MiddlewareChain()

    def add_status(req, nxt):
        resp = nxt(req)
        return {**resp, "middleware": "touched"}

    def final(req):
        return {"body": "hello"}

    chain.use(add_status)
    assert chain.handle({}, final) == {"body": "hello", "middleware": "touched"}


def test_invalid_inputs():
    chain = MiddlewareChain()
    with pytest.raises(TypeError):
        chain.use(None)
    with pytest.raises(TypeError):
        chain.handle({}, None)
    with pytest.raises(TypeError):
        chain.handle("not-a-dict", lambda r: {})
