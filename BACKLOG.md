# Backlog

Work top to bottom. Tick an item (`[x]`) in the same PR that adds it.

## Data structures
- [x] LRU cache — `lru_cache`
- [x] LFU cache — `lfu_cache`
- [x] Bloom filter — `bloom_filter`
- [x] Trie with prefix search and autocomplete — `trie`
- [x] Skip list — `skip_list`
- [x] Consistent hashing ring with virtual nodes — `consistent_hashing`
- [x] Min-heap priority queue with decrease-key — `priority_queue`
- [ ] Union-find (disjoint set) — `union_find`

## Reliability
- [x] Rate limiter (token bucket, sliding window log) — `rate_limiter`
- [ ] Retry with exponential backoff and jitter — `retry_backoff`
- [ ] Circuit breaker (closed / open / half-open) — `circuit_breaker`
- [ ] Bulkhead (concurrency limiter) — `bulkhead`
- [ ] Timeout and deadline propagation — `deadlines`
- [ ] Health checker with liveness and readiness — `health_check`

## Backend
- [ ] HTTP router with path parameters — `http_router`
- [ ] Middleware chain — `middleware`
- [ ] URL shortener (base62, collision handling) — `url_shortener`
- [ ] Session store with TTL — `session_store`
- [ ] Connection pool — `connection_pool`
- [ ] Idempotency-key handler — `idempotency`
- [ ] Pagination (offset and cursor) — `pagination`
- [ ] JWT encode/verify (HS256, standard library only) — `jwt_lite`

## Concurrency
- [ ] Thread pool — `thread_pool`
- [ ] Job queue with workers and retries — `job_queue`
- [ ] Pub/sub event bus — `event_bus`
- [ ] Read-write lock — `rw_lock`
- [ ] Producer–consumer with bounded buffer — `bounded_buffer`
- [ ] Async task scheduler (cron-like) — `scheduler`

## Storage
- [ ] Key-value store with write-ahead log and recovery — `kv_wal`
- [ ] Mini Redis (GET/SET/DEL/EXPIRE over TCP) — `mini_redis`
- [ ] LSM tree basics (memtable, SSTable, compaction) — `lsm_tree`
- [ ] B-tree index — `b_tree`
- [ ] Inverted index full-text search — `inverted_index`
- [ ] Event sourcing with snapshots — `event_sourcing`

## Distributed systems
- [ ] Vector clocks — `vector_clocks`
- [ ] Lamport clock and total ordering — `lamport_clock`
- [ ] Gossip membership protocol (simulated) — `gossip`
- [ ] Leader election (bully algorithm, simulated) — `leader_election`
- [ ] Raft log replication (simplified, simulated) — `raft_lite`
- [ ] Two-phase commit (simulated) — `two_phase_commit`
- [ ] Distributed lock with fencing tokens — `distributed_lock`
- [ ] CRDTs: G-counter, PN-counter, LWW-register — `crdts`

## Tooling
- [ ] Diff algorithm (Myers) — `diff`
- [ ] Mini template engine — `template_engine`
- [ ] JSON parser — `json_parser`
- [ ] Expression evaluator (tokenizer + Pratt parser) — `expr_eval`
- [ ] Structured logger with levels and JSON output — `logger`
- [ ] Feature flags with percentage rollout — `feature_flags`
