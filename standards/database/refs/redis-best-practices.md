---
last_reviewed: 2026-10-18
---

# Redis Detailed Best Practices

Applies to Redis 7.2+ and Valkey 8+ (command-compatible for everything below).

**Licensing**: Redis up to 7.2.4 and Valkey are BSD-3-Clause. Redis 7.4 is RSALv2/SSPLv1 only; Redis 8+ adds AGPLv3 as a third option. Choosing an engine or upgrading across 7.2 → 7.4/8 is a licensing decision — flag it, do not do it silently. Managed services (ElastiCache, Memorystore, Upstash) set their own terms.

## 1. Caching & Memory

- **Cache-aside**: check cache → on miss load from DB → set with TTL → return. Invalidate (delete) on write; do not update cache and DB in two non-atomic steps.
- **TTL jitter**: `TTL = base + random(0, 10% of base)` to avoid synchronized expiry.
- **Stampede protection**: on a hot-key miss, let one caller rebuild (lock key with `SET key val NX PX <ms>`) while others serve stale or wait.
- **Eviction**: `allkeys-lru` (or `allkeys-lfu`) for pure caches; `volatile-*` only when non-expiring keys must survive.
- **Compact encodings**: small hashes, lists, sets, and sorted sets use `listpack`. Keep them under `hash-max-listpack-entries` / `hash-max-listpack-value` (and the matching `zset-`/`set-` keys). The old `*-ziplist-*` names are aliases from Redis ≤ 6.2.

## 2. Command Efficiency

- Never `KEYS` in production; use `SCAN` / `HSCAN` / `SSCAN` / `ZSCAN`.
- `UNLINK` instead of `DEL` for large keys (background free).
- Bound `LRANGE`, `ZRANGE`, `HGETALL`, `SMEMBERS` on collections that can grow.
- Batch with pipelines or `MGET`/`MSET`; keep batches to hundreds, not hundreds of thousands.
- **Atomic multi-step logic**: on 7.0+, prefer Redis Functions (`FUNCTION LOAD` + `FCALL`) — persisted and replicated, no `NOSCRIPT` handling. In Cluster, load the library on every primary. `EVAL`/`EVALSHA` remains valid for one-off scripts; handle `NOSCRIPT` by falling back to `EVAL`.

## 3. Clients & Resilience

- `ioredis` and `node-redis` multiplex commands over one connection per client; they do not pool. Reuse one long-lived client per process; open dedicated connections only for blocking commands (`BLPOP`, `XREAD BLOCK`) and Pub/Sub subscribers.
- Set connect and command timeouts, retry with exponential backoff, and attach an `error` listener.
- Keep app and Redis in the same region; connect by hostname, not IP.

## 4. Monitoring

- Hit ratio: `keyspace_hits / (keyspace_hits + keyspace_misses)`.
- `INFO memory` (fragmentation ratio), `SLOWLOG GET`, `redis-cli --bigkeys` / `--memkeys`, connected-client spikes.

## 5. Security

- ACL users (`ACL SETUSER`) with least privilege instead of a single `requirepass`.
- Block dangerous commands per ACL user (`-flushall -flushdb -config -keys -debug`). `rename-command` is the legacy fallback.
- TLS for all production traffic; never expose the port publicly.
