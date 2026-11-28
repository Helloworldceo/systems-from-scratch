# JWT lite

**Category:** Backend · **Added:** 2026-11-28

## Problem
Issue and verify short-lived tokens that prove a client is authenticated without storing session state on the server.

## Design
A JWT is three base64url segments joined by dots: header, payload, signature.

- Header is `{"alg":"HS256","typ":"JWT"}` (plus any extra headers).
- Payload is a JSON object of claims (`sub`, `exp`, `nbf`, custom fields, …).
- Signature is HMAC-SHA256 of `base64url(header).base64url(payload)` using a shared secret.

`encode` builds the token; `decode` checks the signature with a constant-time compare, then validates `exp` / `nbf` against an injectable clock so tests stay deterministic.

| Operation | Time | Space |
|---|---|---|
| encode / decode | O(n) where n is payload size | O(n) |

## Trade-offs
- HS256 is simple and fast but the secret must be shared; for multi-party use prefer an asymmetric algorithm (not implemented here).
- The payload is only signed, not encrypted — never put secrets in it.
- No support for `iss` / `aud` checks, key rotation or the `none` algorithm (intentionally rejected).
- Python's `hmac.compare_digest` prevents timing attacks on the signature.

## Used in
Stateless API authentication, OAuth2 access tokens, session cookies that don't need a server-side store.
