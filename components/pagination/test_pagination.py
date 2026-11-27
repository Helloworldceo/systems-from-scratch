import base64
import json

import pytest

from pagination import (
    CursorPaginator,
    OffsetPaginator,
    Page,
    _decode_cursor,
    _encode_cursor,
    cursor_page,
    offset_page,
)


def test_offset_basic_first_page():
    items = list(range(25))
    page = offset_page(items, page=1, page_size=10)
    assert isinstance(page, Page)
    assert page.items == list(range(10))
    assert page.page == 1
    assert page.offset == 0
    assert page.total == 25
    assert page.has_next is True
    assert page.has_prev is False
    assert len(page) == 10


def test_offset_middle_and_last_page():
    items = list(range(25))
    p2 = offset_page(items, page=2, page_size=10)
    assert p2.items == list(range(10, 20))
    assert p2.has_next and p2.has_prev
    assert p2.page == 2

    p3 = offset_page(items, page=3, page_size=10)
    assert p3.items == list(range(20, 25))
    assert p3.has_next is False
    assert p3.has_prev is True
    assert len(p3) == 5


def test_offset_empty_and_out_of_range():
    empty = OffsetPaginator(5).paginate([], page=1)
    assert empty.items == []
    assert empty.total == 0
    assert empty.has_next is False
    assert empty.has_prev is False

    past = offset_page(list(range(5)), page=10, page_size=10)
    assert past.items == []
    assert past.total == 5
    assert past.has_next is False


def test_offset_invalid_args():
    with pytest.raises(ValueError):
        OffsetPaginator(0)
    with pytest.raises(ValueError):
        offset_page([1, 2], page=0)
    with pytest.raises(ValueError):
        OffsetPaginator(10).paginate([1], page=1, page_size=0)


def test_cursor_forward_and_next():
    items = [{"id": i, "name": f"n{i}"} for i in range(15)]
    p = CursorPaginator(page_size=5, key=lambda x: x["id"])
    first = p.paginate(items)
    assert [x["id"] for x in first.items] == [0, 1, 2, 3, 4]
    assert first.has_next is True
    assert first.next_cursor is not None

    second = p.paginate(items, cursor=first.next_cursor)
    assert [x["id"] for x in second.items] == [5, 6, 7, 8, 9]
    assert second.has_prev is True

    third = p.paginate(items, cursor=second.next_cursor)
    assert [x["id"] for x in third.items] == [10, 11, 12, 13, 14]
    assert third.has_next is False


def test_cursor_custom_key_and_reverse():
    items = ["apple", "banana", "cherry", "date"]
    page = cursor_page(items, page_size=2, key=lambda s: s, reverse=True)
    # reverse sort: date, cherry, banana, apple
    assert page.items == ["date", "cherry"]
    assert page.has_next is True

    next_page = cursor_page(items, cursor=page.next_cursor, page_size=2, key=lambda s: s, reverse=True)
    assert next_page.items == ["banana", "apple"]
    assert next_page.has_next is False


def test_cursor_invalid():
    with pytest.raises(ValueError):
        CursorPaginator(0)
    with pytest.raises(ValueError):
        cursor_page([1, 2, 3], cursor="not-a-valid-cursor")
    with pytest.raises(ValueError):
        bad = _encode_cursor({"foo": 1})
        cursor_page([1], cursor=bad)


def test_encode_decode_roundtrip():
    payload = {"after": 42, "extra": "ok"}
    encoded = _encode_cursor(payload)
    assert isinstance(encoded, str)
    assert "=" not in encoded  # padding stripped
    decoded = _decode_cursor(encoded)
    assert decoded == payload
