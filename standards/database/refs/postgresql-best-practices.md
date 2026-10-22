---
last_reviewed: 2026-10-18
---

# PostgreSQL Detailed Best Practices

## 1. Indexing Strategy

- **B-tree (default)**: equality and range. Put the most selective, always-filtered columns first in multi-column indexes (PG18 skip scan helps when the leading column is unfiltered, but do not design around it).
- **GIN**: JSONB containment (`@>`), full-text `tsvector`, `pg_trgm` pattern search.
- **BRIN**: very large, naturally ordered tables (append-only time series).
- **Partial**: `CREATE INDEX ... ON users (email) WHERE deleted_at IS NULL;`
- **Covering**: `CREATE INDEX ... ON users (email) INCLUDE (id, name);` enables index-only scans.

## 2. Connection Pooling

- Postgres uses one process per connection; put a pooler in front of high-concurrency or serverless apps.
- **Transaction mode** (PgBouncer `pool_mode = transaction`, Supavisor) hands a server connection to a client per transaction. It breaks session state:
  - Session `SET` leaks to other clients — use `SET LOCAL` inside a transaction, or connection-string parameters.
  - Session advisory locks (`pg_advisory_lock`) — use `pg_advisory_xact_lock`.
  - `LISTEN`/`NOTIFY`, `WITH HOLD` cursors, temp tables spanning transactions — use a direct or session-mode connection.
  - SQL-level `PREPARE` — not supported. Protocol-level prepared statements need PgBouncer 1.21+ with `max_prepared_statements` > 0; otherwise disable them in the driver (e.g. Prisma `pgbouncer=true`).
- Run migrations over a direct (or session-mode) connection, not the transaction pooler.
- Supabase pooler (Supavisor) ports and modes: see `supabase/refs/edge-functions.md`.

## 3. Explain Analyze

- `EXPLAIN (ANALYZE, BUFFERS) SELECT ...`
- Seq Scan on a large table usually means a missing or unusable index. Compare estimated vs actual rows to spot stale statistics (`ANALYZE` after bulk loads).

## 4. Row-Level Security

- Enable RLS on every table exposed to untrusted roles: `ALTER TABLE t ENABLE ROW LEVEL SECURITY;`
- Write one policy per operation; use `WITH CHECK` on `INSERT`/`UPDATE`; index predicate columns.
- Keep policy predicates cheap: functions in policies can run per row. Wrap stable session lookups in a scalar subquery (`(SELECT current_setting('app.tenant_id'))`) so they run once per statement.
- Table owners and roles with `BYPASSRLS` skip policies; use `ALTER TABLE ... FORCE ROW LEVEL SECURITY` if the owner role also serves app traffic.
- Supabase specifics (`auth.uid()`, `service_role`, `security_invoker` views) live in `supabase/refs/rls.md`.

## 5. Partitioning

- Use declarative partitioning for very large tables or time-series with bulk retention.
- Range (by date) or list (by tenant/category).
- `DROP TABLE` / `DETACH PARTITION` on an old partition is instant; `DELETE` is slow and causes bloat.

## 6. Concurrency & Locking

- **Isolation**: Read Committed (default) per statement; Repeatable Read for consistent reports; Serializable needs retry logic on serialization failures.
- **Deadlocks**: Lock rows in a consistent order; keep transactions short.
- **Queues**: `SELECT ... FOR UPDATE SKIP LOCKED` for work queues.

## 7. Monitoring & Diagnostics

- `pg_stat_statements`: track `calls`, `total_exec_time`, `mean_exec_time`, `shared_blks_hit`.
- `log_min_duration_statement` (200–1000 ms), `log_lock_waits = on`, `log_checkpoints = on`.

## 8. Extensions & IDs

- **UUIDs**: `uuidv7()` on PG18+ (time-ordered, index-friendly); `gen_random_uuid()` (built in since PG13) before 18. Do not add `uuid-ossp` for new work.
- `pg_trgm` for fuzzy / `ILIKE '%...%'` search; `postgis` for geospatial.
- Do not use JSONB for stable relational data.

## 9. PG17 / PG18 Features (version-gated)

Use only when the deployed server version is confirmed.

- **PG17**: `JSON_TABLE()` and SQL/JSON query functions; `MERGE ... RETURNING` with `merge_action()`; `COPY ... (ON_ERROR ignore)`; `transaction_timeout`; incremental backups (`pg_basebackup --incremental`).
- **PG18**:
  - `uuidv7()`.
  - Virtual generated columns are the default (`GENERATED ALWAYS AS (...)`); add `STORED` to persist.
  - `RETURNING old.col, new.col` on `INSERT`/`UPDATE`/`DELETE`/`MERGE`.
  - B-tree skip scan for multi-column indexes.
  - Asynchronous I/O (`io_method`) for sequential scans, bitmap heap scans, and vacuum.
  - `NOT NULL` constraints can be added `NOT VALID`.
  - MD5 password authentication deprecated — use `scram-sha-256`.
