# React Security

## XSS Prevention

Never use `dangerouslySetInnerHTML` with unsanitized input. Run all user-provided HTML through DOMPurify before rendering:

```tsx
import DOMPurify from 'dompurify';

function SafeHtml({ html }: { html: string }) {
  const clean = DOMPurify.sanitize(html, { ALLOWED_TAGS: ['b', 'i', 'a', 'p', 'ul', 'li'] });
  return <div dangerouslySetInnerHTML={{ __html: clean }} />;
}
```

Never allow `javascript:` URIs in `href` or `src`. Validate URL protocols before rendering:

```tsx
function isSafeHref(href: string) {
  try {
    const base = typeof window === 'undefined' ? 'https://example.com' : window.location.origin;
    const url = new URL(href, base);
    return ['https:', 'http:'].includes(url.protocol);
  } catch {
    return false;
  }
}

function SafeLink({ href, children }: { href: string; children: ReactNode }) {
  if (!isSafeHref(href)) return <span>{children}</span>;
  return <a href={href}>{children}</a>;
}
```

Treat `data:` URLs as unsafe by default. Allow them only for narrow, non-executable cases such as vetted image previews, and never for navigational links, SVG, HTML, or script-capable content.

Prefer safe DOM sinks such as normal JSX interpolation, text content, `setAttribute` with validated values, and typed URL builders. Dangerous sinks include `dangerouslySetInnerHTML`, direct `innerHTML`, dynamic script/style injection, URL attributes that accept executable protocols, `eval`, and `new Function`. Sanitized HTML must not be mutated afterward; post-sanitization mutation can void the sanitizer's guarantees.

For Chromium-backed apps that render untrusted HTML, consider Trusted Types in report-only first, then enforce once all dangerous sinks are covered by a reviewed policy.

Never execute dynamic strings with `eval()` or `new Function(string)`. Treat remote or user-provided code as remote code execution, not as data.

## Authentication — Token Storage

Store session tokens in `HttpOnly; Secure; SameSite=Strict` or `Lax` cookies based on the identity flow — not in `localStorage` or `sessionStorage`. Tokens in JavaScript-accessible storage are stolen by any XSS. Use CSRF tokens for cookie-authenticated state-changing requests, especially when `SameSite=Lax` is needed for OAuth or cross-site identity redirects.

```ts
// Server — set token in cookie, never return it in JSON body
res.cookie('session', token, {
  httpOnly: true,
  secure: true,
  sameSite: 'lax', // use 'strict' when the flow does not require cross-site redirects
  maxAge: 15 * 60 * 1000, // 15 minutes
});
```

Client auth context reads the user from an `httpOnly` cookie via an authenticated endpoint — it never holds the token directly:

```tsx
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    fetch('/api/auth/me', { credentials: 'include' })
      .then((r) => (r.ok ? r.json() : null))
      .then(setUser);
  }, []);

  const logout = useCallback(
    () => fetch('/api/auth/logout', { method: 'POST', credentials: 'include' }).then(() => setUser(null)),
    [],
  );

  const value = useMemo(() => ({ user, logout }), [user, logout]);

  return <AuthCtx.Provider value={value}>{children}</AuthCtx.Provider>;
}
```

## CSRF Protection

For cookie-authenticated state-changing requests (POST, PUT, PATCH, DELETE), include a CSRF token from a `<meta>` tag or a dedicated endpoint:

```tsx
function getCsrfToken() {
  return document.querySelector<HTMLMetaElement>('meta[name="csrf-token"]')?.content ?? '';
}

async function apiPost(url: string, body: unknown) {
  return fetch(url, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': getCsrfToken() },
    body: JSON.stringify(body),
  });
}
```

## Input Validation Boundary

Client-side validation is for UX only. Validate authorization, ownership, schema, length, type, and allowed values on the server for every request. Sanitize user-provided HTML before storage or rendering; escaping/sanitizing in React does not replace backend validation.

## Content Security Policy

Configure CSP and security headers on the server (or via Next.js middleware) to block inline scripts, restrict script sources, and reduce browser attack surface:

```ts
// Next.js middleware.ts
import { NextResponse } from 'next/server';

const CSP = [
  "default-src 'self'",
  "script-src 'self'",
  "style-src 'self'", // prefer nonces/hashes; justify any 'unsafe-inline' fallback
  "img-src 'self' blob: data: https:",
  "font-src 'self'",
  "object-src 'none'",
  "base-uri 'self'",
  "frame-ancestors 'none'",
  "upgrade-insecure-requests",
].join('; ');

export function middleware(req: Request) {
  const res = NextResponse.next();
  res.headers.set('Content-Security-Policy', CSP);
  res.headers.set('X-Frame-Options', 'DENY');
  res.headers.set('X-Content-Type-Options', 'nosniff');
  res.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');
  return res;
}
```

## SSR — Escape Serialized State

When injecting server-side data into the HTML document, escape it to prevent XSS via the serialized payload:

```tsx
// Never do this — an attacker can close the script tag via the data
<script>window.__DATA__ = {JSON.stringify(data)}</script>

// Do this — escape HTML-significant chars and JS line separators
function escapeJson(data: unknown) {
  return JSON.stringify(data)
    .replace(/</g, '\\u003c')
    .replace(/>/g, '\\u003e')
    .replace(/&/g, '\\u0026')
    .replace(/\u2028/g, '\\u2028')
    .replace(/\u2029/g, '\\u2029');
}

<script dangerouslySetInnerHTML={{ __html: `window.__DATA__ = ${escapeJson(data)}` }} />
```

Prefer a proven serializer when possible. For large or purely data payloads, prefer `<script type="application/json">` plus text extraction over executable inline JavaScript.

## Client Rate Limiting

Client-side debounce/throttle can improve UX, but it is not a security control. Backend rate limits and abuse detection are mandatory because client code is bypassable.

## Client-Side Permission Checks

Never enforce authorization in the client. Hiding a button or route is UX only — a determined caller can bypass it.

```tsx
// Bad — hides UI but does not prevent the API call
if (user.role === 'admin') <DeleteButton />;

// Good — UI matches what the API will allow; the API rejects unauthorized calls regardless
function DeleteButton() {
  async function handleDelete() {
    const res = await fetch(`/api/resource/${id}`, { method: 'DELETE', credentials: 'include' });
    if (res.status === 403) showError('Not authorized');
  }
  return <button onClick={handleDelete}>Delete</button>;
}
```

The server must validate role, ownership, and scope on every state-changing request.

## Dependency Hygiene

Run `npm audit` or `pnpm audit` in CI. Pin direct dependency versions in `package.json`. Review `npm-check-updates` output before major upgrades.
