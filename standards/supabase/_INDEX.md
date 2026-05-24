<!-- AUTO-GENERATED from SKILL.md frontmatters — do not edit manually -->
# supabase Skills Index

## File Match (auto-check against the file you are editing)

| Skill | File pattern | Keywords |
| ----- | ------------ | -------- |
| **supabase** | `supabase/config.toml`, `supabase/migrations/*.sql`, `supabase/functions/**`, `**/supabase/**` | supabase, row level security, rls policy, policy, auth.uid, service_role, anon key, edge function, security definer, search_path, app_metadata, verify_jwt, realtime, storage bucket |
| supabase → rls | `supabase/migrations/*.sql` | row level security, rls policy, policy, auth.uid, auth.jwt, with check, app_metadata, user_metadata |
| supabase → keys-and-clients | `**/supabase/**` | service_role, service role key, anon key, supabase-js |
| supabase → database-functions | `supabase/migrations/*.sql` | security definer, security invoker, search_path |
| supabase → edge-functions | `supabase/functions/**` | edge function, deno, verify_jwt |
| supabase → migrations | `supabase/migrations/*.sql`, `supabase/config.toml` | supabase cli, postgrest, storage bucket, realtime |

> Load `<SKILLS>/supabase/SKILL.md` for any Supabase platform work — RLS policies, the anon/service_role key boundary, Postgres/Edge functions, and the CLI migration workflow. It co-loads with `<SKILLS>/database/SKILL.md` (generic Postgres) on a `supabase/migrations/*.sql` change — domains stack.
> Load `<SKILLS>/supabase/refs/rls.md` when writing or reviewing Row-Level Security policies, `auth.uid()`/`auth.jwt()` predicates, `WITH CHECK`, or `app_metadata` vs `user_metadata` authorization.
> Load `<SKILLS>/supabase/refs/keys-and-clients.md` when touching the `anon`/`service_role` keys, browser/mobile client setup, or SSR admin-client separation.
> Load `<SKILLS>/supabase/refs/database-functions.md` when writing Postgres functions — `SECURITY INVOKER`/`SECURITY DEFINER`, `search_path`, or RLS helper functions.
> Load `<SKILLS>/supabase/refs/edge-functions.md` when writing Deno Edge Functions — `verify_jwt`, in-code auth, project secrets, or Postgres connection handling.
> Load `<SKILLS>/supabase/refs/migrations.md` when touching `supabase/migrations`, the Supabase CLI workflow, storage buckets, or Realtime publications.
> Load `<SKILLS>/supabase/refs/checklist.md` when reviewing a Supabase change end-to-end before deploy.

> **Co-load:** Supabase is Postgres, so a `supabase/migrations/*.sql` change resolves **both** `domain:database` and `domain:supabase`; an Edge Function under `supabase/functions/**` resolves `domain:supabase` (and `domain:typescript`, being Deno TS). Supabase-specific intent (`row level security`, `service_role`, `auth.uid`) routes to `supabase`; generic Postgres terms (`migration`, `postgres`, `index`, `transaction`, `rls`) stay on `database`.
