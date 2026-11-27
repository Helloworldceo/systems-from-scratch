# Pagination (offset and cursor)

**Category:** Backend · **Added:** 2026-11-27

## Problem
Return large result sets in manageable chunks without loading everything into memory
or exposing unstable page numbers when the underlying data changes.

## Design
Two complementary styles:

**Offset pagination** (`OffsetPaginator` / `offset_page`): the classic
`page` + `page_size` model. The server slices the sequence at
`offset = (page - 1) * page_size`. Simple and supports jumping to an
arbitrary page, but the offset becomes wrong if items are inserted or
deleted between requests, and deep pages are expensive on databases.

**Cursor pagination** (`CursorPaginator` / `cursor_page`): the client
receives an opaque base64 cursor that encodes the sort key of the last
item it saw. The next request asks for items strictly after that key.
Cursors are stable under inserts that happen after the cursor, and the
server never needs to skip large numbers of rows. The trade-off is that
you cannot jump to page 7 without walking the previous pages.

Both return a `Page` object with `items`, `has_next` / `has_prev`, and
either `offset`/`total` or `next_cursor`/`prev_cursor`.

| Style | Jump to page | Stable under inserts | Deep-page cost |
|---|---|---|---|
| Offset | yes | no | O(offset) |
| Cursor | no | yes | O(page_size) |

## Trade-offs
- Offset is easy to implement and debug; cursor is preferred for public
  APIs and infinite scroll because it avoids "missing" or duplicate rows
  when the collection mutates.
- Cursors must be opaque. Clients should treat them as black boxes; the
  encoding (base64 of a small JSON payload) can change.
- Both implementations work on in-memory sequences. In a real service the
  same logic is pushed into the database query (`LIMIT/OFFSET` or
  `WHERE id > :cursor ORDER BY id LIMIT n`).
- `page_size` is capped only by the caller; production code usually
  enforces a maximum (for example 100) to protect the backend.

## Used in
GitHub, Stripe, Twitter/X, and most REST APIs that expose list endpoints;
database drivers and ORMs that offer `LIMIT`/`OFFSET` or keyset pagination.
