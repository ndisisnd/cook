# Security And Authentication

Use this ref when implementing auth, cookies, middleware, RBAC, Server Action validation, CSP, CSRF, taint APIs, or data-leak prevention.

## Token Storage

Use `HttpOnly`, `Secure` cookies with `SameSite: 'Lax'` or `'Strict'` and reasonable `maxAge`. Never store access tokens in `localStorage` or `sessionStorage`; they are XSS-vulnerable and cause hydration problems in Server Component flows.

```ts
// app/api/login/route.ts
import { cookies } from 'next/headers';

export async function POST(request: Request) {
  const { email, password } = await request.json();
  const token = await authenticate(email, password);

  (await cookies()).set('session-token', token, {
    httpOnly: true,
    secure: true,
    sameSite: 'lax',
    maxAge: 86400,
    path: '/',
  });

  return Response.json({ success: true });
}
```

```ts
'use server';
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

export async function login(formData: FormData) {
  const result = { accessToken: 'fake_enc_token' };

  (await cookies()).set('session', result.accessToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    maxAge: 60 * 60 * 24 * 7,
    path: '/',
    sameSite: 'lax',
  });

  redirect('/dashboard');
}

export async function logout() {
  (await cookies()).delete('session');
  redirect('/login');
}
```

## Reading Sessions

Read sessions in server-only helpers or DAL functions.

```ts
// lib/auth.ts
import 'server-only';
import { cookies } from 'next/headers';

export async function getSession() {
  const cookieStore = await cookies();
  const session = cookieStore.get('session')?.value;
  if (!session) return null;
  return { user: 'simulated' };
}
```

## Auth Library Selection

Prefer Auth.js (`next-auth`) or Clerk for social login, session management, and provider-heavy authentication flows. Use a custom cookie/session helper only when the project already owns that auth stack or has requirements the library cannot satisfy.

## Middleware Auth And RBAC

Use `middleware.ts` for edge-side redirection, role checks, and security headers. Middleware is not a substitute for auth inside DAL functions, Route Handlers, or Server Actions.

```ts
// middleware.ts
import { NextRequest, NextResponse } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('session-token')?.value;
  if (!token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/settings/:path*'],
};
```

```ts
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const currentUser = request.cookies.get('session')?.value;
  const isLoginPage = request.nextUrl.pathname.startsWith('/login');

  if (!currentUser && !isLoginPage) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  if (currentUser && isLoginPage) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
```

## Server Action Validation

Validate every Server Action input, run auth inside the action, and revalidate affected cache keys. See `refs/server-actions.md` for form state and mutation workflow.

```ts
// app/actions.ts
import { z } from 'zod';

const schema = z.object({
  email: z.string().email(),
});

export async function submit(formData: FormData) {
  const result = schema.safeParse(Object.fromEntries(formData));
  if (!result.success) return { error: 'Invalid' };
  // secure logic
}
```

```ts
// app/posts/actions.ts
'use server';
import { auth } from '@/lib/auth';
import { z } from 'zod';

const CreatePostSchema = z.object({ title: z.string().min(1).max(200) });

export async function createPost(formData: FormData) {
  const session = await auth();
  if (!session) throw new Error('Unauthorized');
  const { title } = CreatePostSchema.parse({ title: formData.get('title') });
  await db.post.create({ data: { title, authorId: session.user.id } });
  revalidateTag('posts');
}
```

## Route Handlers And CSRF

- Verify `Origin` and `Referer` headers for state-changing Route Handlers and Server Actions where CSRF applies.
- Rate limit login, signup, password reset, search, and write-heavy handlers.
- Validate JSON body shape with Zod or equivalent.
- Standardize errors without leaking internal details.

## Data Boundary And Tainting

Return DTOs to components; never pass raw models with secret fields.

```tsx
// app/profile/page.tsx
const user = await db.getUser();

// Good: pass only needed fields.
return <Profile user={{ name: user.name }} />;

// Bad: leaks passwordHash and internal fields.
return <Profile user={user} />;
```

Use experimental taint APIs such as `taintObjectReference` or `taintUniqueValue` where available to block sensitive server objects from reaching Client Components.

## Security Headers And Content

- Set `Content-Security-Policy`, `Strict-Transport-Security`, `X-Frame-Options`, and related headers in middleware or platform config.
- `X-XSS-Protection` is legacy source guidance; modern browsers ignore or deprecate it, so do not rely on it instead of CSP and output escaping.
- Escape user-provided content rendered in components.
- Never use `dangerouslySetInnerHTML` without a sanitizer such as DOMPurify.
- Do not expose server secrets via `process.env` in client bundles; only `NEXT_PUBLIC_*` values are intentionally public.

## Anti-Patterns

- Tokens in `localStorage` or `sessionStorage`.
- Raw tokens in Client Components.
- Unprotected Server Actions or Route Handlers.
- Auth checks only in shared layouts.
- Raw model objects passed to clients.
- `process.env` values in client bundles unless intentionally `NEXT_PUBLIC_*`.
- Unvalidated action inputs.
- `dangerouslySetInnerHTML` without sanitization.
