# Migrations & Workflow

Supabase schema lives in version-controlled SQL, applied through the Supabase CLI.
Generic Postgres migration discipline — expand-contract, concurrent index builds,
non-blocking changes on hot tables — is owned by
[`database/refs/postgresql-best-practices.md`](../../database/refs/postgresql-best-practices.md);
this ref covers the Supabase-specific workflow.

## All schema and RLS changes go through CLI migrations

Edits made only in the Studio dashboard create silent drift: the live schema diverges
from the repo and the next `db push` / deploy can clobber or resurrect objects. Every
change lands as a file in `supabase/migrations/`.

```bash
supabase migration new add_profiles      # creates a timestamped .sql file
# edit the generated SQL, commit it
supabase db push                          # apply to the linked project
```

## Write RLS policies as explicit SQL

ORM-generated migrations do not capture RLS policies (the generic `database` rule
"generated ORM migrations don't reliably capture Row-Level Security" points here).
The `enable row level security` statement and every `create policy` belong in the
same migration that creates the table — see [`rls.md`](rls.md).

## Storage buckets are private by default — gate with storage RLS

Create buckets private and add policies on `storage.objects`. A `public = true`
bucket serves its objects to anyone with the URL — only correct for genuinely public
assets, never for user or private data.

```sql
-- Good: private bucket + an RLS policy scoping objects to their owner's folder
insert into storage.buckets (id, name, public) values ('avatars', 'avatars', false);

create policy "own folder read" on storage.objects
  for select using (
    bucket_id = 'avatars'
    and (select auth.uid())::text = (storage.foldername(name))[1]
  );

-- Never: a public bucket holding private user data
insert into storage.buckets (id, name, public) values ('docs', 'docs', true);
```

## Realtime is opt-in per table

Add a table to the `supabase_realtime` publication deliberately, not wholesale. RLS
applies to Realtime: a `postgres_changes` subscription only emits rows the subscriber
can `SELECT`, so the table's policies are also its broadcast filter.
