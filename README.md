# Systems From Scratch

[![tests](https://github.com/Helloworldceo/systems-from-scratch/actions/workflows/tests.yml/badge.svg)](https://github.com/Helloworldceo/systems-from-scratch/actions/workflows/tests.yml)

Core building blocks of real software, implemented from scratch in Python with tests and
design notes: caches, rate limiters, queues, storage engines and distributed-systems protocols.

Each component lives in `components/<name>/` with:
- a readable implementation using only the standard library
- pytest tests (deterministic, no sleeps or network)
- a design note: the problem, how it works, complexity, trade-offs and where it's used

A new component is added most days, following [`BACKLOG.md`](BACKLOG.md).

## Components

| Component | Category | Added |
|---|---|---|
| [LRU cache](components/lru_cache) | Data structures | 2026-11-09 |
| [Rate limiter](components/rate_limiter) | Reliability | 2026-11-09 |
| [LFU cache](components/lfu_cache) | Data structures | 2026-11-09 |
| [Bloom filter](components/bloom_filter) | Data structures | 2026-11-10 |
| [Trie](components/trie) | Data structures | 2026-11-11 |
| [Skip list](components/skip_list) | Data structures | 2026-11-12 |
| [Consistent hashing](components/consistent_hashing) | Data structures | 2026-11-13 |
| [Priority queue](components/priority_queue) | Data structures | 2026-11-14 |
| [Union-Find](components/union_find) | Data structures | 2026-11-15 |
| [Retry with backoff](components/retry_backoff) | Reliability | 2026-11-16 |
| [Circuit breaker](components/circuit_breaker) | Reliability | 2026-11-17 |
| [Bulkhead](components/bulkhead) | Reliability | 2026-11-18 |
| [Timeout and deadline propagation](components/deadlines) | Reliability | 2026-11-19 |
| [Health checker](components/health_check) | Reliability | 2026-11-20 |
| [HTTP router](components/http_router) | Backend | 2026-11-21 |
| [Middleware chain](components/middleware) | Backend | 2026-11-22 |
| [URL shortener](components/url_shortener) | Backend | 2026-11-23 |
| [Session store](components/session_store) | Backend | 2026-11-24 |

## Run the tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md).

---
Maintained by [@Helloworldceo](https://github.com/Helloworldceo)
