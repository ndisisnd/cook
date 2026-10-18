---
name: database
description: Database standards for PostgreSQL persistence and Redis caching. Use when designing schemas, writing migrations, optimizing queries, configuring Redis, or implementing cache invalidation.
metadata:
  triggers:
    files:
      - '**/*.entity.ts'
      - 'prisma/schema.prisma'
      - 'prisma/migrations/*/migration.sql'
      - '**/migrations/*.sql'
      - 'drizzle.config.ts'
      - 'drizzle/**/*.sql'
      - '**/redis.config.ts'
    keywords:
      - postgres
      - postgresql
      - prisma
      - TypeOrmModule
      - PrismaService
      - PostgresModule
      - redis
      - ttl
      - eviction
  targets: "PostgreSQL 16+ (17/18 features flagged) · Redis 7.2+ / Valkey 8+"
  last_reviewed: 2026-10-18
---

# Database Standards

Targets: PostgreSQL 16+ (17/18-only features are flagged) · Redis 7.2+ / Valkey 8+.
Supabase-specific rules (`auth.uid()`, `service_role`, Supavisor) live in `supabase`.

## Priority: P0 — PostgreSQL Correctness

### Schema & Access

- Isolate persistence logic behind repositories or database services. Do not scatter raw database access across handlers.
- Enforce integrity in the database with primary keys, foreign keys, `NOT NULL`, `CHECK`, and `UNIQUE` constraints.
- Use `timestamptz`, `text`, `numeric` or integer minor units for money, and `GENERATED ALWAYS AS IDENTITY` or UUIDs for keys (see [postgresql-anti-patterns](refs/postgresql-anti-patterns.md)).

### Migrations

- Use explicit, version-controlled migrations for every schema change. ORM schema sync is dev-only:
  - TypeORM: never `synchronize: true` outside local dev.
  - Prisma: `prisma migrate deploy` in CI/prod; `migrate dev` and `db push` are dev-only.
  - Drizzle: `drizzle-kit generate` + `migrate` for shared environments; `drizzle-kit push` is prototyping-only.
- Destructive or renaming changes use expand-contract — the recipe is [postgresql-implementation](refs/postgresql-implementation.md).
- On live tables, set `lock_timeout`, build indexes `CONCURRENTLY`, and add constraints `NOT VALID` then `VALIDATE` — see the migration section of [postgresql-checklist](refs/postgresql-checklist.md).
- Generated ORM migrations do not capture Row-Level Security. Write RLS as explicit SQL.

### Queries & Performance

- Paginate every list query (keyset for deep pages).
- Index every hot filter, join, foreign-key, and RLS-predicate column.
- Use short transactions for multi-step mutations. Prevent N+1 with joins or batching.
- Project only the columns you need; no `SELECT *` in application queries.
- Behind a transaction-mode pooler (PgBouncer, Supavisor), do not rely on session state — see the pooling section of [postgresql-best-practices](refs/postgresql-best-practices.md).

## Priority: P0 — Redis Safety

### Data Design

- Redis/Valkey is a cache, queue, or coordination layer — never the sole source of truth for critical business data.
- Namespace keys with colons (`app:user:123`). Every non-permanent key needs a TTL; add TTL jitter on high-volume keys.
- Prefer hashes for field-addressable objects over large JSON blobs.

### Commands & Operations

- Never use `KEYS` in production; use `SCAN`. Use `UNLINK` for large keys. Bound every range read.
- Use pipelines for bulk operations and Redis Functions (`FCALL`) or Lua scripts for atomic multi-step logic.
- Use ACL users, TLS, and disabled dangerous commands in production.

## Anti-Patterns

- ORM schema sync (`synchronize: true`, `prisma db push`, `drizzle-kit push`) against shared databases
- Destructive schema changes without expand-contract; long-locking DDL without `lock_timeout`
- Missing indexes on hot filters, joins, foreign keys, or RLS columns
- Session-level `SET`, advisory locks, or SQL `PREPARE` through a transaction-mode pooler
- Treating Redis as the durable source of truth; `KEYS` in production; TTL-less ephemeral keys

## References

Load only what the task requires:

PostgreSQL:
- [postgresql-implementation](refs/postgresql-implementation.md) — canonical expand-contract migration recipe
- [postgresql-best-practices](refs/postgresql-best-practices.md) — indexing, pooling, RLS pointer, partitioning, locking, diagnostics, PG17/18 features
- [postgresql-checklist](refs/postgresql-checklist.md) — review checklist incl. safe-migration rules
- [postgresql-anti-patterns](refs/postgresql-anti-patterns.md) — types, SQL constructs, and operations to avoid
- [sql-gotchas](refs/sql-gotchas.md) — `UPDATE ... FROM`, timezone, `NULL`, `ILIKE`, and `JSONB` caveats

Redis / Valkey:
- [redis-best-practices](refs/redis-best-practices.md) — caching, memory, commands, clients, security, licensing
- [redis-checklist](refs/redis-checklist.md) — review checklist for Redis setup and cache behavior
