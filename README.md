# Systems From Scratch

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

## Run the tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md).

---
Maintained by [@Helloworldceo](https://github.com/Helloworldceo)
