---
name: supabase
description: Supabase platform standards — Row-Level Security, the anon/service_role key boundary, Postgres and Edge functions, Storage, Realtime, and the CLI migration workflow. Use when working with RLS policies, Supabase clients, Edge Functions, or supabase/ migrations. Loads alongside the database (Postgres) domain.
metadata:
  triggers:
    files:
      - 'supabase/config.toml'
      - 'supabase/migrations/*.sql'
      - 'supabase/functions/**'
      - '**/supabase/**'
    keywords:
      - supabase
      - row level security
      - rls policy
      - auth.uid
      - service_role
      - anon key
      - edge function
      - security definer
      - search_path
      - verify_jwt
      - realtime
      - storage bucket
---

# Supabase Standards

Supabase is Postgres underneath, so this domain co-loads with `database` (generic
Postgres) and the `auth` / `security` concerns. It owns **only the platform
contract**: RLS, the key boundary, Postgres/Edge function security, and the CLI
migration workflow. Generic Postgres rules (types, constraints, indexing-in-general,
expand-contract, N+1, transactions) live in `database`; auth flows (JWT verification,
OAuth, password reset) live in `global/refs/auth.md` — this domain links to them
rather than restating them.

## Priority: P0 — Row-Level Security

- **RLS is OFF by default. Every table reachable through the API/PostgREST must
  `ENABLE ROW LEVEL SECURITY` in the same migration that creates it.** A table left
  unguarded behind a public `anon` key is a full data leak.
  Signal: a `create table` in `supabase/migrations` with no matching `alter table …
  enable row level security`.
- **RLS-on denies by default — write an explicit policy per operation
  (`select`/`insert`/`update`/`delete`).** Don't rely on one `for all` policy where
  operations need different predicates.
  Signal: a table with RLS enabled and no policy, or a blanket `for all using (true)`.
- **Pair every `UPDATE`/`DELETE` policy with a `SELECT` policy.** Postgres must read
  the existing row to evaluate the `USING` clause; without `SELECT` the row is
  invisible and the write silently affects nothing.
  Signal: an `update`/`delete` policy on a table with no `select` policy.
- **Use `WITH CHECK` on `INSERT`/`UPDATE`** so a user can't write a row they couldn't
  own or read (e.g. inserting someone else's `user_id`).
  Signal: an `insert`/`update` policy with `using` but no `with check`.
- **Wrap auth calls as `(select auth.uid())` / `(select auth.jwt())` in policy
  predicates** so the planner caches the result per-statement instead of
  re-evaluating per row.
  Signal: a bare `auth.uid()` in a policy on a table that gets scanned.
- **Never base a policy on `auth.jwt() -> 'user_metadata'`** — `user_metadata` is
  editable by the authenticated user. Use `app_metadata` (server-controlled) or a
  roles table joined via a `security definer` helper.
  Signal: a policy reading `user_metadata` for an authorization decision.
- **Index every column referenced in an RLS predicate** (`user_id`, `tenant_id`, …).
  RLS turns these into per-query filters; an unindexed predicate column is a full
  scan on every request. (Sharpens the `database` indexing rule.)
  Signal: an RLS predicate column absent from any index.

## Priority: P0 — Keys & Client Boundary

- **The `service_role` key bypasses RLS — backend / Edge Functions only.** Never ship
  it to a browser or mobile bundle, never put it in a client-public env
  (`NEXT_PUBLIC_*`, `EXPO_PUBLIC_*`, `VITE_*`). A leaked `service_role` key is root on
  the database.
  Signal: `service_role` / `SUPABASE_SERVICE_ROLE_KEY` referenced in client-bundled
  code or a public-prefixed env var.
- **The `anon` key is public but RLS-gated** — only safe in a client if RLS is enabled
  on every exposed table (ties back to RLS above).
  Signal: an `anon` client used against a table with RLS disabled.
- **A user-session client and a `service_role` client are separate instances.** A
  client carrying a user session sends the user JWT (RLS applies); do not attach a
  user session to the admin client, and the user session must not override the
  `service_role` apikey. In SSR, build a dedicated admin client.
  Signal: one shared client mixing a user session with the `service_role` key.

## Priority: P0 — Postgres & Edge Functions

- **Prefer `SECURITY INVOKER` (the default) for Postgres functions.** If a function
  must be `SECURITY DEFINER`, set `search_path = ''`, schema-qualify every relation
  (`public.table`), and never create it in an API-exposed schema.
  Signal: `security definer` with no `set search_path = ''`, or such a function in an
  exposed schema.
- **Edge Functions are publicly invokable by default — verify the caller.** Keep
  `verify_jwt` on (or check the JWT/authorization in code) for any function touching
  user data; read secrets from project secrets / env, never hardcode.
  Signal: an Edge Function reading user data with `verify_jwt = false` and no in-code
  auth check; a literal key in function source.
- **Treat Postgres as a pooled remote from Edge Functions** — use the connection
  pooler / serverless-friendly client; don't open a fresh direct connection per
  invocation.
  Signal: a `new Pool` / direct-connect per request in a function.

## Priority: P1 — Migrations & Workflow

- **All schema and RLS changes go through Supabase CLI migrations in
  `supabase/migrations`, version-controlled** — never schema-edit only in the
  dashboard (silent drift). Write RLS policies as explicit SQL; ORM-generated
  migrations don't capture them.
  Signal: a dashboard-only schema change with no migration file.
- **Storage buckets are private by default; gate access with storage RLS policies.**
  Signal: a `public = true` bucket holding user/private data.
- **P1 (design):** enable Realtime per-table deliberately, and remember RLS applies to
  Realtime too — a `postgres_changes` subscription only emits rows the subscriber can
  read.

## Anti-Patterns

- Table exposed with RLS disabled
- RLS on with no policy, or a blanket `for all using (true)`
- `update`/`delete` policy without a `select` policy
- `insert`/`update` policy without `with check`
- bare `auth.uid()` per-row in a policy
- policy keyed on `user_metadata` for authorization
- unindexed RLS predicate column
- `service_role` key in a client bundle or public-prefixed env var
- user session attached to the admin client
- `security definer` with no `search_path = ''`, or in an exposed schema
- Edge Function on user data with `verify_jwt` off and no in-code check
- hardcoded secrets in Edge Function source
- dashboard-only schema edits (drift)
- public storage buckets holding private data

## References

Load only what the task requires:

- [rls](refs/rls.md) — enable-RLS migration pattern, per-operation policies, `SELECT`+`UPDATE` pairing, `WITH CHECK`, `(select auth.uid())` wrapping, `app_metadata` vs `user_metadata`, indexing predicate columns
- [keys-and-clients](refs/keys-and-clients.md) — anon vs service_role, browser/mobile boundary, SSR admin-client separation, public-env pitfalls
- [database-functions](refs/database-functions.md) — `SECURITY INVOKER` default, `SECURITY DEFINER` + `search_path = ''` + schema qualification, exposed-schema rule, `auth.uid()` in helpers
- [edge-functions](refs/edge-functions.md) — Deno runtime, `verify_jwt` / in-code auth, project secrets, connection pooling for Postgres
- [migrations](refs/migrations.md) — CLI workflow, RLS-as-SQL, dashboard drift, storage and Realtime policies
- [checklist](refs/checklist.md) — pre-deploy review checklist
