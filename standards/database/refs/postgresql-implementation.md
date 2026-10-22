---
last_reviewed: 2026-10-18
---

# Expand-Contract Migration Recipe

Canonical recipe for renaming or reshaping a column on a live table. Never `RENAME COLUMN` on a table that running code reads — old and new app versions overlap during a deploy.

Each step is its own migration or deploy:

1. **Expand** — add the new column (nullable, no volatile default).
2. **Dual-write** — deploy code that writes both old and new columns.
3. **Backfill** — copy old to new in batches, outside one long transaction.
4. **Switch reads** — deploy code that reads the new column.
5. **Stop writes** — deploy code that no longer writes the old column.
6. **Contract** — drop the old column in a later migration.

```sql
-- 1. Expand
ALTER TABLE orders ADD COLUMN order_status text;

-- 3. Backfill in batches (repeat until 0 rows updated)
UPDATE orders SET order_status = status
WHERE id IN (
  SELECT id FROM orders WHERE order_status IS NULL AND status IS NOT NULL
  ORDER BY id LIMIT 5000
);

-- After backfill, enforce NOT NULL without a long lock
ALTER TABLE orders ADD CONSTRAINT orders_order_status_nn
  CHECK (order_status IS NOT NULL) NOT VALID;
ALTER TABLE orders VALIDATE CONSTRAINT orders_order_status_nn;

-- 6. Contract (after no deployed code reads or writes status)
ALTER TABLE orders DROP COLUMN status;
```

Safe-migration rules (`lock_timeout`, `CONCURRENTLY`, `NOT VALID`) are in [postgresql-checklist](postgresql-checklist.md#migrations).
