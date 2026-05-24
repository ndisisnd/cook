# Supabase Row-Level Security

RLS is the entire security model when a client holds the `anon` key. Get a policy
wrong and the data is either invisible or world-readable. This ref is the detailed
home for the SKILL's P0 RLS rules. Generic Postgres concerns (indexing in general,
constraints, expand-contract) stay in
[`database/refs/postgresql-best-practices.md`](../../database/refs/postgresql-best-practices.md);
here we cover only the Supabase platform contract.

## Enable RLS on every exposed table — in the same migration

A new table is reachable through PostgREST/the API the moment it exists, and RLS is
**off by default**. An unguarded table behind a public `anon` key is a full data
leak.

```sql
-- Good: create + enable in one migration, no window where the table is open
create table public.profiles (
  id uuid primary key references auth.users (id),
  user_id uuid not null,
  display_name text
);
alter table public.profiles enable row level security;

-- Never: create table with no enable — exposed and unprotected
create table public.profiles (...);
```

## RLS-on means deny-by-default — write a policy per operation

Once enabled, every row is denied until a policy grants it. Write a separate policy
per operation when the predicates differ; do not paper over it with `for all using
(true)`, which re-opens the table.

```sql
-- Good: explicit per-operation policies
create policy "select own" on public.profiles
  for select using ((select auth.uid()) = user_id);
create policy "insert own" on public.profiles
  for insert with check ((select auth.uid()) = user_id);

-- Never: blanket allow re-exposes everything
create policy "open" on public.profiles for all using (true);
```

## Pair every UPDATE / DELETE with a SELECT policy

Postgres must read the existing row to evaluate an `UPDATE`/`DELETE` `USING` clause.
With no `SELECT` policy the row is invisible, so the write silently matches nothing.

```sql
-- Good
create policy "select own" on public.posts
  for select using ((select auth.uid()) = author_id);
create policy "delete own" on public.posts
  for delete using ((select auth.uid()) = author_id);

-- Never: delete policy with no select policy — deletes affect 0 rows, silently
create policy "delete own" on public.posts
  for delete using ((select auth.uid()) = author_id);
```

## Use WITH CHECK on INSERT / UPDATE

`USING` filters which rows are visible to the operation; `WITH CHECK` validates the
*new* row's contents. Without it a user can insert or rewrite a row they could never
own — e.g. setting someone else's `user_id`.

```sql
-- Good: the row being written must belong to the caller
create policy "insert own" on public.profiles
  for insert with check ((select auth.uid()) = user_id);
create policy "update own" on public.profiles
  for update using ((select auth.uid()) = user_id)
             with check ((select auth.uid()) = user_id);

-- Never: using but no with check — caller can write a row owned by someone else
create policy "update own" on public.profiles
  for update using ((select auth.uid()) = user_id);
```

## Wrap auth calls as (select auth.uid()) / (select auth.jwt())

A bare `auth.uid()` in a predicate is re-evaluated **per row**. Wrapping it in a
scalar subquery lets the planner evaluate it once per statement (an initplan) and
cache the result — a large win on any scanned table.

```sql
-- Good: evaluated once per statement
using ((select auth.uid()) = user_id)

-- Slow: re-evaluated for every row scanned
using (auth.uid() = user_id)
```

## Authorize on app_metadata, never user_metadata

`user_metadata` is editable by the authenticated user via the client SDK — basing a
policy on it lets a user grant themselves access. `app_metadata` is server-controlled
(set with the admin API), or join a roles table through a `security definer` helper.

```sql
-- Good: server-controlled claim
create policy "admins read all" on public.audit_log
  for select using (
    (select auth.jwt() -> 'app_metadata' ->> 'role') = 'admin'
  );

-- Never: user_metadata is attacker-controlled
create policy "admins read all" on public.audit_log
  for select using (
    (select auth.jwt() -> 'user_metadata' ->> 'role') = 'admin'
  );
```

## Index every column referenced in an RLS predicate

RLS predicates become a per-query filter on every request. An unindexed `user_id` /
`tenant_id` referenced in a policy is a sequential scan on each call. This sharpens
the generic indexing rule in `database` — the difference is that here the predicate
column is *implicit*, added by the policy, so it is easy to miss.

```sql
create index on public.profiles (user_id);   -- referenced by every policy above
```

## Storage and Realtime inherit RLS

`storage.objects` is a normal table — gate bucket access with RLS policies on it, and
keep buckets private by default. Realtime `postgres_changes` only emits rows the
subscriber's RLS lets them `SELECT`, so the same policies protect the live stream;
enable Realtime per-table deliberately rather than globally.
