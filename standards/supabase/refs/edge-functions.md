# Edge Functions (Deno)

Supabase Edge Functions are Deno TypeScript, deployed to a global runtime, and
**publicly invokable by default**. Treat every function as an internet-facing
endpoint.

## Verify the caller

A function touching user data must authenticate the request. Keep `verify_jwt` on
(the platform then rejects an unauthenticated call before your code runs), or verify
the JWT / authorization header in code. Do not assume auth is handled upstream.

```toml
# supabase/config.toml — public webhook receivers may set this false on purpose,
# but anything reading user data must keep it true (the default).
[functions.notify]
verify_jwt = true
```

```ts
// Good: derive the user from the request JWT and let RLS apply
import { createClient } from "jsr:@supabase/supabase-js@2";

Deno.serve(async (req) => {
  const authHeader = req.headers.get("Authorization");
  if (!authHeader) return new Response("Unauthorized", { status: 401 });
  const supabase = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_ANON_KEY")!,
    { global: { headers: { Authorization: authHeader } } },
  );
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return new Response("Unauthorized", { status: 401 });
  // ...RLS now scopes queries to this user
});
```

## Read secrets from the environment, never hardcode

Secrets come from Supabase project secrets / `Deno.env`. A literal key in function
source is committed to git and shipped on deploy.

```ts
// Good
const key = Deno.env.get("STRIPE_SECRET_KEY")!;
// Never: literal secret in source
const key = "sk_live_51H...";
```

If a function must bypass RLS (a trusted backend task), read
`SUPABASE_SERVICE_ROLE_KEY` from the env — it lives server-side here, which is exactly
where `service_role` belongs (see [`keys-and-clients.md`](keys-and-clients.md)).

## Treat Postgres as a pooled remote

Edge Functions are serverless and may run many concurrent invocations. Opening a
fresh direct connection per request exhausts Postgres connection slots. Use the
Supabase client (which goes through PostgREST) or the connection pooler / a
serverless-friendly driver — never a new direct `Pool` per invocation.

```ts
// Never: a fresh direct connection on every request
Deno.serve(async () => {
  const pool = new Pool({ connectionString: DIRECT_DB_URL }, 1);  // leaks slots
  // ...
});
```
