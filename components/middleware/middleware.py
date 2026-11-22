"""Middleware chain for composing request/response handlers.

A list of middlewares is applied around a final handler in registration
order. Each middleware receives the request and a `next` callable; it may
inspect or mutate the request, call `next` (possibly more than once), or
short-circuit by returning a response without calling `next`.
"""
from __future__ import annotations

from typing import Any, Callable

Request = dict[str, Any]
Response = dict[str, Any]
Handler = Callable[[Request], Response]
Middleware = Callable[[Request, Handler], Response]


class MiddlewareChain:
    """Ordered chain of middlewares wrapping a final handler."""

    def __init__(self) -> None:
        self._middlewares: list[Middleware] = []

    def use(self, middleware: Middleware) -> None:
        """Append a middleware. Call order is the order of `use`."""
        if not callable(middleware):
            raise TypeError("middleware must be callable")
        self._middlewares.append(middleware)

    def __len__(self) -> int:
        return len(self._middlewares)

    def handle(self, request: Request, final: Handler) -> Response:
        """Run the request through the chain and return the final response."""
        if not callable(final):
            raise TypeError("final handler must be callable")
        if not isinstance(request, dict):
            raise TypeError("request must be a dict")

        def make_next(index: int) -> Handler:
            if index >= len(self._middlewares):
                return final

            mw = self._middlewares[index]

            def next_handler(req: Request) -> Response:
                return mw(req, make_next(index + 1))

            return next_handler

        return make_next(0)(request)
