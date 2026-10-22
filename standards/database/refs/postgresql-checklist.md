---
last_reviewed: 2026-10-18
---

# PostgreSQL Review Checklist

Use this checklist before finalizing any schema migration or complex query.

## Schema Design

- [ ] **Primary keys**: Every table has one (`bigint` identity or UUID).
- [ ] **Data types**: No `char(n)`, `varchar(n)`, `money`, `serial`, or `float` for money. Timestamps are `timestamptz`.
- [ ] **Foreign keys**: Every FK column is indexed (Postgres does not do this automatically).
- [ ] **Constraints**: `NOT NULL`, `CHECK`, and `UNIQUE` enforce integrity in the database.
- [ ] **Normalization**: Roughly 3NF; JSONB only for genuinely dynamic data.

## Performance (Query/Index)

- [ ] **Index usage**: `EXPLAIN (ANALYZE, BUFFERS)` shows no unexpected Seq Scan on large tables.
- [ ] **SARGable**: Predicates are index-friendly; no leading-wildcard `LIKE '%term'` without `pg_trgm`.
- [ ] **No `SELECT *`**: Explicit column selection.
- [ ] **Pagination**: Keyset/cursor pagination for deep or infinite lists.

## Security

- [ ] **RLS**: Enabled with per-operation policies on tables exposed to untrusted roles.
- [ ] **Least privilege**: The application role cannot `DROP`, `TRUNCATE`, or alter schema.

## Migrations

- [ ] **Lock budget**: The migration sets `SET lock_timeout = '5s'` (or similar) so a blocked DDL fails fast instead of queuing all traffic behind it.
- [ ] **Indexes on live tables**: Built with `CREATE INDEX CONCURRENTLY`. It cannot run inside a transaction block — most migration tools (Prisma, TypeORM, Flyway, Supabase CLI) wrap each file in one, so use the tool's no-transaction escape hatch or a separate migration.
- [ ] **New constraints**: `FOREIGN KEY` and `CHECK` are added `NOT VALID`, then `VALIDATE CONSTRAINT` in a separate step (only a light lock while validating).
- [ ] **NOT NULL on an existing column**: Added via a validated `CHECK (col IS NOT NULL)` first, then `SET NOT NULL` (PG12+ skips the scan). PG18+ can add `NOT NULL ... NOT VALID` directly.
- [ ] **Defaults**: `ADD COLUMN ... DEFAULT <constant>` is metadata-only (PG11+). A volatile default (`now()`, `random()`, `gen_random_uuid()`) rewrites the whole table — add the column without it and backfill.
- [ ] **Type changes**: `ALTER COLUMN ... TYPE` that rewrites the table is treated as expand-contract ([postgresql-implementation](postgresql-implementation.md)).
- [ ] **Renames/drops**: No `RENAME`/`DROP` of anything deployed code still reads.
- [ ] **Revertible**: A down-migration or documented roll-forward exists.

## Concurrency & Monitoring

- [ ] **Transaction size**: Transactions are short; no network calls inside them.
- [ ] **Deadlock safety**: Multi-row updates lock rows in a consistent order (e.g., by `id`).
- [ ] **Logging**: `log_min_duration_statement` is enabled in production.
- [ ] **Analysis**: `pg_stat_statements` reviewed for the touched queries.
