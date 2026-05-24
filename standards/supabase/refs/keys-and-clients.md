# Keys & Client Boundary

Supabase ships two API keys with opposite trust levels. Mixing them up is the most
common cause of a Supabase data breach.

| Key | Respects RLS? | Where it may live |
| --- | --- | --- |
| `anon` | **Yes** — fully RLS-gated | Browser, mobile, any public client (only safe if RLS is on every exposed table) |
| `service_role` | **No** — bypasses RLS entirely | Backend / Edge Functions / trusted server only |

JWT verification, OAuth/PKCE, session and refresh-token handling as *auth flows* are
owned by [`global/refs/auth.md`](../../global/refs/auth.md) — this ref covers only the
key boundary and client construction.

## service_role bypasses RLS — backend only

A leaked `service_role` key is root on the database: it reads and writes every row
regardless of policy. It must never reach a browser or mobile bundle, and never sit
in a client-public env var.

```ts
// Never: service_role behind a client-public prefix — shipped to every browser
const supabase = createClient(url, process.env.NEXT_PUBLIC_SUPABASE_SERVICE_ROLE_KEY!);
// Same trap with EXPO_PUBLIC_* / VITE_* — all are bundled into the client.

// Good: service_role only in server-side code, from a non-public env var
const admin = createClient(url, process.env.SUPABASE_SERVICE_ROLE_KEY!, {
  auth: { autoRefreshToken: false, persistSession: false },
});
```

cook cannot mechanically scan a built bundle for a leaked key — this stays a
keyword/review-mode signal. In review, flag any `service_role` /
`SUPABASE_SERVICE_ROLE_KEY` reference in client-bundled code or a `NEXT_PUBLIC_*` /
`EXPO_PUBLIC_*` / `VITE_*` env var.

## anon key is public but RLS-gated

The `anon` key is *designed* to ship to clients — its safety depends entirely on RLS
being enabled on every table it can reach. An `anon` client against an RLS-disabled
table is the same full leak as a leaked `service_role` key. See
[`rls.md`](rls.md).

## Keep the user-session client and the admin client separate

A client carrying a user session sends that user's JWT, so RLS applies to its
queries. The admin (`service_role`) client must be a **separate instance** — never
attach a user session to it, and never let a user session silently override the
`service_role` apikey on a shared client.

```ts
// Good (SSR): two distinct clients, two distinct trust levels
const userClient = createServerClient(url, anonKey, { cookies });   // RLS applies
const adminClient = createClient(url, serviceRoleKey, {             // RLS bypassed
  auth: { autoRefreshToken: false, persistSession: false },
});

// Never: one shared client mutated between user and admin work — the session
// and the service_role key fight over the same instance.
```

Use the admin client only for trusted server tasks (webhooks, backfills, cross-user
reads) and prefer a user-session client everywhere RLS *should* apply.
