"""HTTP router with path parameters.

Matches method + path against registered routes. Patterns use `{name}`
placeholders that capture one path segment. The clock is not involved;
everything is pure matching.
"""
from __future__ import annotations

import re
from typing import Callable, Optional

Handler = Callable[..., object]


class Route:
    __slots__ = ("method", "pattern", "handler", "_regex", "param_names")

    def __init__(self, method: str, pattern: str, handler: Handler):
        self.method = method.upper()
        self.pattern = pattern
        self.handler = handler
        self.param_names, self._regex = _compile(pattern)

    def match(self, path: str) -> Optional[dict[str, str]]:
        m = self._regex.fullmatch(path)
        return m.groupdict() if m else None


def _compile(pattern: str) -> tuple[list[str], re.Pattern[str]]:
    if not pattern.startswith("/"):
        raise ValueError("path must start with /")
    # Split on / but keep leading empty for root.
    parts = pattern.split("/")
    param_names: list[str] = []
    regex_parts: list[str] = []
    for i, part in enumerate(parts):
        if i == 0:
            continue  # leading empty from split
        if not part:
            # consecutive slashes or trailing empty only allowed at end for root-ish
            if i != len(parts) - 1:
                raise ValueError("empty path segment")
            continue
        if part.startswith("{") and part.endswith("}"):
            name = part[1:-1]
            if not name or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
                raise ValueError(f"invalid parameter name: {part}")
            if name in param_names:
                raise ValueError(f"duplicate parameter: {name}")
            param_names.append(name)
            regex_parts.append(f"(?P<{name}>[^/]+)")
        else:
            if "{" in part or "}" in part:
                raise ValueError(f"malformed segment: {part}")
            regex_parts.append(re.escape(part))
    # Reconstruct: /seg1/seg2 or just /
    if not regex_parts:
        regex = r"/"
    else:
        regex = "/" + "/".join(regex_parts)
    # Optional trailing slash only for non-root? Keep strict for simplicity.
    return param_names, re.compile(regex)


class HTTPRouter:
    """Registers routes and matches method + path to a handler plus params."""

    def __init__(self) -> None:
        self._routes: list[Route] = []

    def add(self, method: str, path: str, handler: Handler) -> None:
        if not callable(handler):
            raise TypeError("handler must be callable")
        route = Route(method, path, handler)
        self._routes.append(route)

    def route(self, method: str, path: str) -> Callable[[Handler], Handler]:
        """Decorator form of add."""

        def deco(fn: Handler) -> Handler:
            self.add(method, path, fn)
            return fn

        return deco

    def match(
        self, method: str, path: str
    ) -> Optional[tuple[Handler, dict[str, str]]]:
        """Return (handler, params) for the first matching route, or None."""
        method = method.upper()
        # Normalise empty path to root.
        if path == "":
            path = "/"
        for route in self._routes:
            if route.method == method:
                params = route.match(path)
                if params is not None:
                    return route.handler, params
        return None

    def __len__(self) -> int:
        return len(self._routes)
