---
last_reviewed: 2026-10-18
---

# Redis Review Checklist

## Setup & Configuration

- [ ] **Client lifecycle**: One long-lived client per process (no connect-per-request); dedicated connections only for blocking commands and Pub/Sub.
- [ ] **Error handling**: An `error` listener is attached; timeouts and backoff are configured.
- [ ] **Security (ACL)**: Least-privilege ACL users instead of a global `requirepass`.
- [ ] **Security (TLS)**: TLS between app and Redis.
- [ ] **Dangerous commands**: `FLUSHALL`, `FLUSHDB`, `CONFIG`, `KEYS` blocked for the app user.
- [ ] **Engine/licence**: Redis vs Valkey and version choice is deliberate (Redis 7.4+ / 8+ licence terms differ from BSD).

## Performance & Commands

- [ ] **O(N) avoidance**: No `KEYS`; iteration uses `SCAN` family.
- [ ] **Background deletion**: Large keys deleted with `UNLINK`.
- [ ] **Range limits**: `ZRANGE`, `LRANGE`, `HGETALL` are bounded.
- [ ] **Atomicity**: Multi-step updates use Redis Functions (`FCALL`), `MULTI`/`EXEC`, or a Lua script — not read-modify-write from the app.
- [ ] **Pipelining**: Bulk operations are pipelined.

## Memory & Data Design

- [ ] **TTL**: Every ephemeral key has a TTL, with jitter on high-volume keys.
- [ ] **Data types**: Hashes for field-addressable objects instead of whole JSON strings.
- [ ] **Eviction policy**: `maxmemory` and `maxmemory-policy` match the workload.

## Monitoring & Ops

- [ ] **Instrumentation**: Hit ratio, memory, and client count are exported.
- [ ] **Big keys**: Keyspace checked for unexpectedly large values.
- [ ] **Latency**: `SLOWLOG` reviewed for new scripts and commands.
