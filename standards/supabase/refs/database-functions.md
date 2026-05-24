# Postgres Functions on Supabase

Postgres functions (RPCs, triggers, RLS helpers) run inside the database with a
chosen privilege level. The wrong choice quietly bypasses RLS for everyone.

## Prefer SECURITY INVOKER (the default)

`SECURITY INVOKER` runs the function as the calling user, so RLS still applies. Reach
for `SECURITY DEFINER` only when a function genuinely must act with elevated rights
(e.g. a roles-lookup helper used inside a policy).

## A SECURITY DEFINER function must pin search_path and schema-qualify

A `DEFINER` function runs as its owner and **ignores RLS**. If `search_path` is left
mutable, a caller can shadow a referenced table/function with one in a schema they
control and hijack the elevated execution. Set `search_path = ''` and fully qualify
every relation; never create such a function in an API-exposed schema (`public`,
or any schema added to PostgREST's exposed list).

```sql
-- Good: pinned search_path, schema-qualified, lives in a private schema
create function private.current_role()
  returns text
  language sql
  security definer
  set search_path = ''          -- empty: nothing is implicitly resolved
as $$
  select r.role from public.user_roles r where r.user_id = (select auth.uid());
$$;

-- Never: definer with a mutable search_path in an exposed schema
create function public.current_role()
  returns text
  language sql
  security definer               -- runs as owner, bypasses RLS
as $$ select role from user_roles where user_id = auth.uid(); $$;
```

Use such a helper from a policy to avoid recursive RLS on the roles table itself:

```sql
create policy "admins manage" on public.audit_log
  for all using (private.current_role() = 'admin');
```

## auth.uid() inside helpers

`auth.uid()` reads the request JWT, so it works inside functions called on the request
path. Wrap it as `(select auth.uid())` in any SQL that scans rows, for the same
per-statement caching reason as in [`rls.md`](rls.md).
