# Supabase Pre-Deploy Checklist

Review gate for any change touching Supabase. Pairs with the SKILL's `Signal:`s — each
line is something a reviewer (or review mode) can confirm against the diff.

## RLS

- [ ] Every table reachable through the API has `enable row level security` in the
      **same migration** that creates it.
- [ ] No table is left with RLS on and zero policies, and no `for all using (true)`
      blanket policy re-opens a table.
- [ ] Every `UPDATE` / `DELETE` policy has a matching `SELECT` policy.
- [ ] Every `INSERT` / `UPDATE` policy has a `WITH CHECK` clause.
- [ ] Auth calls in policies are wrapped as `(select auth.uid())` / `(select auth.jwt())`.
- [ ] No policy makes an authorization decision from `user_metadata` (use
      `app_metadata` or a roles table).
- [ ] Every column referenced by an RLS predicate is indexed.

## Keys & clients

- [ ] Public clients use `sb_publishable_...` keys (or legacy `anon` only for
      compatibility) and only access tables that have RLS enabled.
- [ ] No `sb_secret`, `SUPABASE_SECRET_KEYS`, `service_role`, or
      `SUPABASE_SERVICE_ROLE_KEY` in client-bundled code, a `NEXT_PUBLIC_*` /
      `EXPO_PUBLIC_*` / `VITE_*` env var, a URL/query param, or unsanitized logs.
- [ ] The user-session client and the secret-key / legacy `service_role` admin
      client are separate instances; no user session is attached to the admin client.

## Functions

- [ ] Postgres functions are `SECURITY INVOKER` unless they must be `DEFINER`.
- [ ] Every `SECURITY DEFINER` function sets `search_path = ''`, schema-qualifies its
      relations, and is not in an API-exposed schema.
- [ ] Edge Functions touching user data keep `verify_jwt = true` for user-JWT
      callers, or use `verify_jwt = false` with an in-code signature / `apikey`
      check for webhooks and service calls; publishable/secret keys are not sent as
      bearer tokens.
- [ ] No secrets are hardcoded; Postgres is reached through the pooler/client, not a
      fresh per-request connection.

## Workflow

- [ ] All schema and RLS changes are CLI migrations in `supabase/migrations/`, not
      dashboard-only edits.
- [ ] Storage buckets holding private data are `public = false` with storage RLS
      policies.
- [ ] Realtime is enabled per table deliberately, with RLS in mind.
