---
name: supabase
description: Supabase platform standards — Row-Level Security, publishable/anon and secret/service_role key boundaries, Postgres and Edge functions, Storage, Realtime, and the CLI migration workflow. Use when working with RLS policies, Supabase clients, Edge Functions, or supabase/ migrations. Loads alongside the database (Postgres) domain.
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
      - publishable key
      - secret key
      - sb_publishable
      - sb_secret
      - service_role
      - anon key
      - apikey
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

- **Use publishable keys (`sb_publishable_...`) for public clients; treat legacy
  `anon` as the compatibility form.** Public clients are only safe when RLS protects
  every exposed table for the `anon` / `authenticated` roles.
  Signal: a publishable or legacy `anon` client used against a table with RLS disabled.
- **Secret keys (`sb_secret_...`) and legacy `service_role` keys bypass RLS —
  backend / Edge Functions only.** Never ship them to a browser or mobile bundle,
  never put them in a client-public env (`NEXT_PUBLIC_*`, `EXPO_PUBLIC_*`, `VITE_*`),
  and never pass them in URLs or query params. A leaked secret key is root on the
  database.
  Signal: `sb_secret`, `SUPABASE_SECRET_KEYS`, `service_role`, or
  `SUPABASE_SERVICE_ROLE_KEY` referenced in client-bundled code, a public-prefixed
  env var, a URL/query param, or unsanitized logs.
- **A user-session client and an admin client are separate instances.** A client
  carrying a user session sends the user JWT (RLS applies); do not attach a user
  session to the admin client, and the user session must not override the admin API
  key. In SSR, build a dedicated admin client from a secret key / legacy
  `service_role` key.
  Signal: one shared client mixing a user session with `sb_secret` / `service_role`.

## Priority: P0 — Postgres & Edge Functions

- **Prefer `SECURITY INVOKER` (the default) for Postgres functions.** If a function
  must be `SECURITY DEFINER`, set `search_path = ''`, schema-qualify every relation
  (`public.table`), and never create it in an API-exposed schema.
  Signal: `security definer` with no `set search_path = ''`, or such a function in an
  exposed schema.
- **Edge Functions are publicly invokable by default — match `verify_jwt` to the
  caller credential and verify inside the handler when needed.** Keep `verify_jwt`
  on for user-JWT calls. Turn it off for webhooks or API-key service calls, then
  verify the provider signature or `apikey` header in code. Publishable/secret keys
  are not JWTs and must not be sent as `Authorization: Bearer ...`.
  Signal: an Edge Function reading user data with `verify_jwt = false` and no
  signature / `apikey` / authorization check; a publishable or secret key sent as a
  bearer token; a literal key in function source.
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
- `sb_secret` / `service_role` key in a client bundle, public-prefixed env var, URL, or log
- user session attached to the admin client
- `security definer` with no `search_path = ''`, or in an exposed schema
- Edge Function on user data with `verify_jwt` off and no in-code check
- hardcoded secrets in Edge Function source
- dashboard-only schema edits (drift)
- public storage buckets holding private data

## References

Load only what the task requires:

- [rls](refs/rls.md) — enable-RLS migration pattern, per-operation policies, `SELECT`+`UPDATE` pairing, `WITH CHECK`, `(select auth.uid())` wrapping, `app_metadata` vs `user_metadata`, indexing predicate columns
- [keys-and-clients](refs/keys-and-clients.md) — publishable/anon vs secret/service_role, browser/mobile boundary, SSR admin-client separation, public-env pitfalls
- [database-functions](refs/database-functions.md) — `SECURITY INVOKER` default, `SECURITY DEFINER` + `search_path = ''` + schema qualification, exposed-schema rule, `auth.uid()` in helpers
- [edge-functions](refs/edge-functions.md) — Deno runtime, user JWT vs API-key auth, `verify_jwt` / in-code auth, project secrets, connection pooling for Postgres
- [migrations](refs/migrations.md) — CLI workflow, RLS-as-SQL, dashboard drift, storage and Realtime policies
- [checklist](refs/checklist.md) — pre-deploy review checklist
