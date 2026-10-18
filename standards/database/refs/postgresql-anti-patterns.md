---
last_reviewed: 2026-10-18
---

# PostgreSQL Anti-Patterns ("Don't Do This")

Synthesized from the official Postgres Wiki.

## 1. Data Types

- **Don't use `money`**:
  - **Why?** Locale-dependent output, confusing rounding, hard to migrate.
  - **Do:** Use `numeric(precision, scale)` or integer minor units (cents).
- **Don't use `char(n)` or `varchar(n)` as a length check**:
  - **Why?** `char(n)` pads with spaces; changing `varchar(n)` later needs a migration.
  - **Do:** Use `text`, with a `CHECK (length(col) <= n)` when a limit is a business rule.
- **Don't use `serial`**:
  - **Why?** Non-standard, sequence-ownership and permission hassles.
  - **Do:** Use `GENERATED ALWAYS AS IDENTITY`, or UUIDs (`uuidv7()` on PG18+, `gen_random_uuid()` before).
- **Don't use `timestamp` (without time zone)**:
  - **Why?** No zone information; breaks for global users and DST.
  - **Do:** Use `timestamptz`.

## 2. SQL Constructs

- **Don't use `NOT IN` with a subquery or list that can contain NULL**:
  - **Why?** `val NOT IN (1, NULL)` evaluates to `NULL`, never `TRUE`.
  - **Do:** Use `NOT EXISTS`.
- **Don't use `BETWEEN` for timestamps**:
  - **Why?** `BETWEEN` is inclusive at both ends.
  - **Do:** `created_at >= '2023-01-01' AND created_at < '2023-02-01'`.
- **Don't use quoted or mixed-case identifiers**:
  - **Why?** Postgres folds unquoted identifiers to lowercase; `"UserTable"` then needs quoting forever.
  - **Do:** Use `snake_case` for everything.

## 3. Operations

- **Don't use `psql -W`**:
  - **Why?** Forces a password prompt, blocking automation.
  - **Do:** Use a `.pgpass` file or environment variables.
- **Don't use Rules (`CREATE RULE`)**:
  - **Why?** Query rewriting is hard to reason about and can double-execute functions.
  - **Do:** Use triggers (`CREATE TRIGGER`).
- **Don't disable or ignore autovacuum**:
  - **Why?** Table bloat degrades performance; unchecked, transaction ID wraparound forces the database read-only.
  - **Do:** Keep autovacuum on; tune per table (`ALTER TABLE ... SET (autovacuum_vacuum_scale_factor = 0.01)`) for large, high-churn tables.
- **Don't use MD5 password authentication**:
  - **Why?** Deprecated in PG18; removal is planned for a future major version.
  - **Do:** Use `scram-sha-256`.

## 4. Concurrency

- **Don't hold transactions open**:
  - **Why?** Holds locks, blocks vacuum cleanup, increases deadlock risk.
  - **Do:** Commit as soon as the unit of work is done; set `idle_in_transaction_session_timeout` (and `transaction_timeout` on PG17+).
- **Don't use `LOCK TABLE`**:
  - **Why?** Serializes all access to the table.
  - **Do:** Use row-level locks or transaction-scoped advisory locks (`pg_advisory_xact_lock`).
