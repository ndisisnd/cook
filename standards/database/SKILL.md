---
name: database
description: Database standards for PostgreSQL persistence and Redis caching. Use when designing schemas, writing migrations, optimizing queries, configuring Redis, or implementing cache invalidation.
metadata:
  triggers:
    files:
      - '**/*.entity.ts'
      - 'prisma/schema.prisma'
      - '**/migrations/*.sql'
      - '**/redis.config.ts'
    keywords:
      - postgres
      - postgresql
      - migration
      - TypeOrmModule
      - PrismaService
      - PostgresModule
      - redis
      - cache
      - ttl
      - eviction
---

# Database Standards

## Priority: P0 — PostgreSQL Correctness

### Schema & Access

- Isolate persistence logic behind repositories or database services. Do not scatter raw database access across handlers.
- Model relations explicitly. Avoid redundant raw ID mirror fields when the ORM relation already expresses the dependency.
- Enforce integrity in the database with primary keys, foreign keys, `NOT NULL`, `CHECK`, and `UNIQUE` constraints.
- Prefer `timestamptz` for timestamps, `text` or unbounded `varchar` for strings, and `numeric` or integer minor units for money.

### Migrations

- Never use `synchronize: true` in production.
- Use explicit migrations for every schema change.
- Follow expand-contract for destructive changes: add, backfill, deploy, then remove.
- Generated ORM migrations do not reliably capture Row-Level Security. Write RLS policies as explicit SQL.
- On hot tables, avoid blocking changes and prefer concurrent index creation where supported.

### Queries & Performance

- Paginate every list query.
- Index every hot filter, join, and foreign-key column. Columns referenced by RLS predicates must be indexed.
- Use transactions for multi-step mutations.
- Prevent N+1 access patterns with joins, batching, or ORM query builders.
- Avoid `SELECT *` in application queries; project only the columns you need.

## Priority: P0 — Redis Safety

### Data Design

- Redis is a cache, queue, or coordination layer. It must not be the sole source of truth for critical business data.
- Namespace keys with colons, for example `app:user:123`.
- Every non-permanent key needs a TTL or a deliberate eviction strategy.
- Add TTL jitter for high-volume cache keys to avoid synchronized expirations.
- Prefer hashes for field-addressable objects over large JSON blobs.

### Commands & Operations

- Never use `KEYS` in production. Use `SCAN` and related cursor-based commands.
- Use `UNLINK` instead of `DEL` for large-key deletion.
- Bound `ZRANGE`, `LRANGE`, and `HGETALL` usage. Do not fetch unbounded collections.
- Use pipelines for bulk operations and `EVALSHA` for atomic multi-step cache logic.
- Keep application and Redis in the same region and connect through stable hostnames.

### Security & Resilience

- Use Redis ACLs instead of a shared global password where possible.
- Enable TLS for production traffic.
- Disable or rename dangerous commands such as `FLUSHALL`, `CONFIG`, and `SHUTDOWN`.
- Use connection pooling plus retry and timeout settings tuned for transient failures.

## Anti-Patterns

- `synchronize: true` in production
- Destructive schema changes without expand-contract sequencing
- Missing indexes on hot filters, joins, or RLS columns
- `timestamp` without time zone for user or cross-region data
- `money`, `char(n)`, or `serial` in new PostgreSQL schema work
- N+1 queries, long-running transactions, or blanket `SELECT *`
- Treating Redis as the durable source of truth
- `KEYS` in production, unbounded range reads, or TTL-less ephemeral keys
- Storing large opaque blobs in Redis when field-level access is needed

## References

Load only what the task requires:

- [postgresql-implementation](refs/postgresql-implementation.md) — expand-contract migration examples
- [postgresql-best-practices](refs/postgresql-best-practices.md) — indexing, partitioning, locking, extensions, and diagnostics
- [postgresql-checklist](refs/postgresql-checklist.md) — review checklist for migrations and complex queries
- [postgresql-anti-patterns](refs/postgresql-anti-patterns.md) — schema and SQL pitfalls to avoid
- [sql-gotchas](refs/sql-gotchas.md) — `UPDATE ... FROM`, timezone, `NULL`, `ILIKE`, and `JSONB` caveats
- [redis-best-practices](refs/redis-best-practices.md) — caching, memory, command efficiency, and security details
- [redis-checklist](refs/redis-checklist.md) — review checklist for Redis setup and cache behavior
