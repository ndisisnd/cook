# Keys & Client Boundary

Supabase ships public and elevated API keys with opposite trust levels. Mixing
them up is the most common cause of a Supabase data breach.

| Key | Respects RLS? | Where it may live |
| --- | --- | --- |
| `sb_publishable_...` | **Yes** — maps to `anon` / `authenticated` roles | Browser, mobile, source code, public clients (only safe if RLS is on every exposed table) |
| `anon` | **Yes** — fully RLS-gated | Legacy compatibility form of publishable keys |
| `sb_secret_...` | **No** — uses `service_role`, bypasses RLS | Backend / Edge Functions / trusted server only |
| `service_role` | **No** — bypasses RLS entirely | Legacy compatibility form of secret keys |

JWT verification, OAuth/PKCE, session and refresh-token handling as *auth flows* are
owned by [`global/refs/auth.md`](../../global/refs/auth.md) — this ref covers only the
key boundary and client construction.

## Publishable keys are public but RLS-gated

Use `sb_publishable_...` keys for browsers, mobile apps, CLIs, and other public
components. Legacy `anon` keys still work, but treat them as the older form of the
same public-client boundary. Their safety depends entirely on RLS being enabled on
every table they can reach.

```ts
// Good: public key in a browser client, with RLS doing the authorization
const supabase = createClient(url, process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!);

// Legacy-compatible, but prefer sb_publishable_... for new work
const legacyClient = createClient(url, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!);
```

An `sb_publishable_...` / `anon` client against an RLS-disabled table is still a
full data leak. See [`rls.md`](rls.md).

## Secret keys and service_role bypass RLS — backend only

A leaked `sb_secret_...` or legacy `service_role` key is root on the database: it
reads and writes every row regardless of policy. It must never reach a browser or
mobile bundle, never sit in a client-public env var, never appear in a URL/query
param, and never be logged unsafely.

```ts
// Never: elevated keys behind client-public prefixes — shipped to every browser
const leakedClient = createClient(url, process.env.NEXT_PUBLIC_SUPABASE_SECRET_KEY!);
// Same trap with EXPO_PUBLIC_* / VITE_* — all are bundled into the client.
// Legacy service_role has the same problem:
createClient(url, process.env.NEXT_PUBLIC_SUPABASE_SERVICE_ROLE_KEY!);

// Good: elevated key only in server-side code, from a non-public env var
const admin = createClient(url, process.env.SUPABASE_SECRET_KEY!, {
  auth: { autoRefreshToken: false, persistSession: false },
});
```

cook cannot mechanically scan a built bundle for a leaked key — this stays a
keyword/review-mode signal. In review, flag any `sb_secret`,
`SUPABASE_SECRET_KEYS`, `service_role`, or `SUPABASE_SERVICE_ROLE_KEY` reference
in client-bundled code, a `NEXT_PUBLIC_*` / `EXPO_PUBLIC_*` / `VITE_*` env var, a
URL/query param, or logs.

## Keep the user-session client and the admin client separate

A client carrying a user session sends that user's JWT, so RLS applies to its
queries. The admin (`sb_secret_...` / legacy `service_role`) client must be a
**separate instance** — never attach a user session to it, and never let a user
session silently override the admin API key on a shared client.

```ts
// Good (SSR): two distinct clients, two distinct trust levels
const userClient = createServerClient(url, publishableKey, { cookies }); // RLS applies
const adminClient = createClient(url, secretKey, {                       // RLS bypassed
  auth: { autoRefreshToken: false, persistSession: false },
});

// Never: one shared client mutated between user and admin work — the session
// and the elevated key fight over the same instance.
```

Use the admin client only for trusted server tasks (webhooks, backfills, cross-user
reads) and prefer a user-session client everywhere RLS *should* apply.
