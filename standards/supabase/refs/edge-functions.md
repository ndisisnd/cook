# Edge Functions (Deno)

Supabase Edge Functions are Deno TypeScript, deployed to a global runtime, and
**publicly invokable by default**. Treat every function as an internet-facing
endpoint.

## Verify the caller

A function touching user data must authenticate the request. Edge Functions have
two auth layers: the platform-level `verify_jwt` check before your code runs, then
the authorization checks inside your handler. Match `verify_jwt` to the credential
the caller actually sends:

- Keep `verify_jwt = true` for user calls that send a Supabase Auth JWT in the
  `Authorization` header.
- Use `verify_jwt = false` for webhooks or service-to-service calls that do not
  send a user JWT, then verify the provider signature or `apikey` header in code.
- Never send `sb_publishable_...` or `sb_secret_...` as
  `Authorization: Bearer ...`; they are API keys, not JWTs.

```toml
# supabase/config.toml — public webhook receivers may set this false on purpose,
# but user-JWT functions should keep it true (the default).
[functions.notify]
verify_jwt = true
```

```ts
// Good: derive the user from the request JWT and let RLS apply
import { createClient } from "jsr:@supabase/supabase-js@2";

const publishableKeys = JSON.parse(Deno.env.get("SUPABASE_PUBLISHABLE_KEYS")!);

Deno.serve(async (req) => {
  const authHeader = req.headers.get("Authorization");
  if (!authHeader) return new Response("Unauthorized", { status: 401 });
  const supabase = createClient(
    Deno.env.get("SUPABASE_URL")!,
    publishableKeys.default,
    { global: { headers: { Authorization: authHeader } } },
  );
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return new Response("Unauthorized", { status: 401 });
  // ...RLS now scopes queries to this user
});
```

```toml
# Service-to-service API-key callers do not send a user JWT.
[functions.run-automations]
verify_jwt = false
```

```ts
// Good: verify the apikey header yourself before privileged work
import { createClient } from "jsr:@supabase/supabase-js@2";

const secretKeys = JSON.parse(Deno.env.get("SUPABASE_SECRET_KEYS")!);

Deno.serve(async (req) => {
  const apikey = req.headers.get("apikey");
  if (!apikey || apikey !== secretKeys.automations) {
    return new Response("Unauthorized", { status: 401 });
  }
  const admin = createClient(
    Deno.env.get("SUPABASE_URL")!,
    secretKeys.automations,
  );
  // ...trusted automation work
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

If a function must bypass RLS (a trusted backend task), read an `sb_secret_...` key
from project secrets (for example `SUPABASE_SECRET_KEYS`). A legacy
`SUPABASE_SERVICE_ROLE_KEY` is still server-only compatibility, but new work should
prefer secret keys (see [`keys-and-clients.md`](keys-and-clients.md)).

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
