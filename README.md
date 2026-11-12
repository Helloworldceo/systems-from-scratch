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

## Run the tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md).

---
Maintained by [@Helloworldceo](https://github.com/Helloworldceo)
