"""Pagination helpers: offset-based and cursor-based.

Both styles return a Page object with the slice of items and metadata
needed to request the next or previous page. Cursor values are opaque
base64 strings so clients treat them as black boxes.
"""
from __future__ import annotations

import base64
import json
from typing import Any, Callable, Generic, Optional, Sequence, TypeVar

T = TypeVar("T")
K = TypeVar("K")

KeyFunc = Callable[[T], Any]


class Page(Generic[T]):
    """A single page of results plus navigation metadata."""

    def __init__(
        self,
        items: list[T],
        *,
        page_size: int,
        total: Optional[int] = None,
        offset: Optional[int] = None,
        next_cursor: Optional[str] = None,
        prev_cursor: Optional[str] = None,
        has_next: bool = False,
        has_prev: bool = False,
    ):
        self.items = items
        self.page_size = page_size
        self.total = total
        self.offset = offset
        self.next_cursor = next_cursor
        self.prev_cursor = prev_cursor
        self.has_next = has_next
        self.has_prev = has_prev

    @property
    def page(self) -> Optional[int]:
        """1-based page number for offset pagination, or None for cursor."""
        if self.offset is None or self.page_size <= 0:
            return None
        return (self.offset // self.page_size) + 1

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self):
        return iter(self.items)


def _encode_cursor(payload: dict) -> str:
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _decode_cursor(cursor: str) -> dict:
    try:
        padding = "=" * (-len(cursor) % 4)
        raw = base64.urlsafe_b64decode(cursor + padding)
        return json.loads(raw.decode())
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"invalid cursor: {cursor!r}") from exc


class OffsetPaginator:
    """Classic page/page_size pagination over a sequence.

    Suitable for small or medium collections where counting is cheap.
    """

    def __init__(self, page_size: int = 20):
        if page_size <= 0:
            raise ValueError("page_size must be positive")
        self.page_size = page_size

    def paginate(
        self,
        items: Sequence[T],
        page: int = 1,
        page_size: Optional[int] = None,
    ) -> Page[T]:
        size = page_size if page_size is not None else self.page_size
        if size <= 0:
            raise ValueError("page_size must be positive")
        if page < 1:
            raise ValueError("page must be >= 1")

        total = len(items)
        offset = (page - 1) * size
        if offset >= total and total > 0:
            # empty page past the end
            slice_items: list[T] = []
        else:
            slice_items = list(items[offset : offset + size])

        has_next = offset + size < total
        has_prev = page > 1
        return Page(
            slice_items,
            page_size=size,
            total=total,
            offset=offset,
            has_next=has_next,
            has_prev=has_prev,
        )


class CursorPaginator:
    """Cursor-based pagination that avoids offset drift on changing data.

    The cursor encodes the sort key of the last item seen. Clients pass the
    `next_cursor` from the previous page; the server returns items strictly
    after that key.
    """

    def __init__(self, page_size: int = 20, key: Optional[KeyFunc] = None):
        if page_size <= 0:
            raise ValueError("page_size must be positive")
        self.page_size = page_size
        self._key = key if key is not None else (lambda x: x)

    def paginate(
        self,
        items: Sequence[T],
        cursor: Optional[str] = None,
        page_size: Optional[int] = None,
        reverse: bool = False,
    ) -> Page[T]:
        size = page_size if page_size is not None else self.page_size
        if size <= 0:
            raise ValueError("page_size must be positive")

        keyed = [(self._key(item), item) for item in items]
        # stable sort
        keyed.sort(key=lambda pair: pair[0], reverse=reverse)

        start = 0
        if cursor is not None:
            payload = _decode_cursor(cursor)
            after = payload.get("after")
            if after is None:
                raise ValueError("cursor missing 'after'")
            # find first item strictly after the cursor key
            for i, (k, _) in enumerate(keyed):
                if (not reverse and k > after) or (reverse and k < after):
                    start = i
                    break
            else:
                start = len(keyed)

        page_items = [item for _, item in keyed[start : start + size]]
        has_next = start + size < len(keyed)
        has_prev = start > 0

        next_cursor = None
        if has_next and page_items:
            last_key = self._key(page_items[-1])
            next_cursor = _encode_cursor({"after": last_key})

        prev_cursor = None
        if has_prev and page_items:
            first_key = self._key(page_items[0])
            # encode the key just before the first of this page so going back works
            prev_cursor = _encode_cursor({"after": first_key, "dir": "prev"})

        return Page(
            page_items,
            page_size=size,
            total=len(items),
            next_cursor=next_cursor,
            prev_cursor=prev_cursor,
            has_next=has_next,
            has_prev=has_prev,
        )


def offset_page(
    items: Sequence[T], page: int = 1, page_size: int = 20
) -> Page[T]:
    """Convenience wrapper around OffsetPaginator."""
    return OffsetPaginator(page_size).paginate(items, page=page)


def cursor_page(
    items: Sequence[T],
    cursor: Optional[str] = None,
    page_size: int = 20,
    key: Optional[KeyFunc] = None,
    reverse: bool = False,
) -> Page[T]:
    """Convenience wrapper around CursorPaginator."""
    return CursorPaginator(page_size, key=key).paginate(
        items, cursor=cursor, reverse=reverse
    )
