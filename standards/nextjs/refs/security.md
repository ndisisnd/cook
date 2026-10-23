---
last_reviewed: 2026-10-23
---

# Security And Authentication

Next.js-specific security: `proxy.ts`, session cookies, Server Action and Route Handler protection, CSRF origin checks, taint APIs, and the server/client data boundary.

Generic rules: `global/refs/security.md`, `global/refs/auth.md`. Client rules (token storage, XSS/DOMPurify, URL validation, client-side permission checks): `react/refs/security.md`.

## Session Cookies

Set session cookies only on the server, from a Server Action or Route Handler. `cookies()` is async in Next.js 16: `await` it. Cookie flag policy: `global/refs/auth.md`.

```ts
// app/(auth)/actions.ts
'use server';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { z } from 'zod';

const LoginSchema = z.object({ email: z.email(), password: z.string().min(1) });

export async function login(formData: FormData) {
  const parsed = LoginSchema.safeParse(Object.fromEntries(formData));
  if (!parsed.success) return { error: 'Invalid credentials' };

  const session = await createSession(parsed.data); // server-only helper
  (await cookies()).set('session', session.token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 7,
    path: '/',
  });
  redirect('/dashboard');
}
```

Read sessions in a `server-only` helper (`lib/auth.ts`) that DAL functions call. Prefer Auth.js or Clerk for provider-heavy flows; keep custom session code only when the project already owns it.

## Proxy (`proxy.ts`)

Next.js 16 renamed `middleware.ts` to `proxy.ts` and the export to `proxy`. Proxy runs on the Node.js runtime only; the `runtime` option throws an error there. Keep an existing `middleware.ts` only when it must stay on the Edge runtime. Rename with `npx @next/codemod@canary middleware-to-proxy .`. Flags renamed too (for example `skipMiddlewareUrlNormalize` -> `skipProxyUrlNormalize`).

Use proxy for optimistic checks (cookie present -> continue, else redirect) and headers. It is not an authorization layer: re-check auth in DAL functions, Server Actions, and Route Handlers.

A Server Action call is a `POST` to the route that uses it. A `matcher` that excludes that path skips proxy for the action, and moving an action to another route can drop proxy coverage unnoticed.

```ts
// proxy.ts
import { NextResponse, type NextRequest } from 'next/server';

export function proxy(request: NextRequest) {
  const hasSession = request.cookies.has('session');
  const isLogin = request.nextUrl.pathname.startsWith('/login');

  if (!hasSession && !isLogin) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
  if (hasSession && isLogin) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
```

## Server Actions

Every exported Server Action is reachable by direct POST, even if no UI imports it. A page-level auth check does not protect the actions on that page.

```ts
// app/posts/actions.ts
'use server';
import { updateTag } from 'next/cache';
import { z } from 'zod';
import { auth } from '@/lib/auth';

const CreatePostSchema = z.object({ title: z.string().min(1).max(200) });

export async function createPost(formData: FormData) {
  const session = await auth();
  if (!session?.user) throw new Error('Unauthorized');

  const parsed = CreatePostSchema.safeParse({ title: formData.get('title') });
  if (!parsed.success) return { errors: z.flattenError(parsed.error).fieldErrors };

  await db.post.create({ data: { title: parsed.data.title, authorId: session.user.id } });
  updateTag('posts');
  return { success: true };
}
```

- Check ownership of the specific resource inside the action, not only login state (IDOR).
- Return only what the UI needs; return values are serialized to the client.
- Keep secrets out of inline action closures. Next.js encrypts closed-over values, but do not rely on that alone.
- Multi-instance self-hosting: set `NEXT_SERVER_ACTIONS_ENCRYPTION_KEY` (base64 AES key of 16, 24, or 32 bytes) so all instances share one key.

## CSRF

- Server Actions are POST-only. Next.js compares the `Origin` host with `Host` / `X-Forwarded-Host` and aborts a mismatch. A request with no `Origin` header is allowed with a warning.
- When the proxy forwards its own host instead of the public one, list the public hosts in `experimental.serverActions.allowedOrigins`. Entries are `host[:port]` and `*.` wildcards; a bare `example.com` does not match its subdomains.
- Route Handlers have no built-in check. Verify `Origin` on state-changing handlers, and authenticate, authorize, and validate every `route.ts` handler.

## Data Boundary And Tainting

- Pass DTOs to Client Components, never raw models.
- Enable `experimental.taint: true` to use `experimental_taintObjectReference` and `experimental_taintUniqueValue` as an extra guard. Taint tracks the object reference or the exact value only: a copy or a derived string is untainted. It does not replace DTO filtering.
- Only `NEXT_PUBLIC_*` variables are bundled for the client. Read secrets only in `server-only` modules (`import 'server-only'`).
- Cache Components: a `use cache` entry is shared by every request with the same arguments. Read `cookies()`/`headers()` outside the cached scope and pass only the needed value (for example the user ID) as an argument. Never cache per-user data under a key without the user.

## Security Headers And CSP

- Set headers in `proxy.ts` or through `headers()` in `next.config.ts`. Header values and CSP policy: `global/refs/security.md`.
- Nonce-based CSP requires dynamic rendering and is incompatible with Partial Prerendering. Generate the nonce in `proxy.ts`, pass it in a request header (`x-nonce`) and the CSP header, and read it with `headers()` in a Server Component. Without nonces, set the CSP in `next.config.ts` `headers()`.

## Anti-Patterns

- New `middleware.ts` / `export function middleware` code on Next.js 16.
- Treating proxy or layout checks as authorization.
- Server Actions without `'use server'`, input validation, or an in-action auth check.
- Server Actions that return full DB records.
- State-changing Route Handlers without auth or an `Origin` check.
- `process.env` secrets referenced from Client Components.
