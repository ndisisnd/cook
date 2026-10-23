---
last_reviewed: 2026-10-23
---

# React Security

Browser and DOM rules for React clients. Generic rules: `global/refs/security.md`, `global/refs/auth.md`. CSP and headers: `global/refs/security.md`; Next.js wiring: `nextjs/refs/security.md`.

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

Prefer safe DOM sinks such as normal JSX interpolation, text content, `setAttribute` with validated values, and typed URL builders. Dangerous sinks include `dangerouslySetInnerHTML`, direct `innerHTML`, dynamic script/style injection, and URL attributes that accept executable protocols. Sanitized HTML must not be mutated afterward; post-sanitization mutation can void the sanitizer's guarantees.

For apps that render untrusted HTML, consider Trusted Types (Baseline since Feb 2026) in report-only first, then enforce once all dangerous sinks are covered by a reviewed policy.

Never pass user input to `location.href`, `location.assign`, or `window.open` without `isSafeHref`. In DOMPurify configs set `ALLOW_DATA_ATTR: false`; for user HTML rendered in-page also keep `SANITIZE_NAMED_PROPS: true` and `FORBID_ATTR: ['id', 'name']`. A user-controlled `id`/`name` clobbers `window.x`/`document.x` (DOM clobbering), so never read config or flags from `window`/`document` globals.

Never execute dynamic strings with `eval()` or `new Function(string)`. Never pass a string to `setTimeout`/`setInterval`, or call `document.write`, with user data. Treat remote or user-provided code as remote code execution, not as data.

## Cross-Window & Third-Party Content

- `postMessage`: pass an exact `targetOrigin`, never `'*'`. In the receiver, compare `event.origin` with `===` against an allowlist. Never use `includes`/`endsWith`/`startsWith` (subdomain takeover). Treat `event.data` as untrusted.
- External `<script>`/`<link>`: add `integrity="sha384-…"` with `crossOrigin="anonymous"` (also on `next/script`). Re-hash on every vendor version change.
- Untrusted iframes: `sandbox` with the fewest tokens. Never combine `allow-scripts` and `allow-same-origin` for content served from your own origin, because it can remove its own sandbox.
- Third-party tags read only a first-party, sanitized data layer. They get no DOM or URL-param access.

## Authentication — Client Side

Never store session tokens in `localStorage` or `sessionStorage`: any XSS reads them. Keep them in `HttpOnly` cookies set by the server (cookie flags, CSRF design: `global/refs/auth.md`). Cookie-authenticated `POST`/`PUT`/`PATCH`/`DELETE` calls send the CSRF token, for example from a `<meta>` tag, in a header.

The client auth context reads the user from an authenticated endpoint and never holds the token:

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
    .replace(/ /g, '\\u2028')
    .replace(/ /g, '\\u2029');
}

<script dangerouslySetInnerHTML={{ __html: `window.__DATA__ = ${escapeJson(data)}` }} />
```

Prefer a proven serializer when possible. For large or purely data payloads, prefer `<script type="application/json">` plus text extraction over executable inline JavaScript.

## Client-Side Permission Checks

Never enforce authorization in the client. Hiding a button or route is UX only. Client-side validation and debounce are UX only too. The server must validate role, ownership, scope, schema, and rate limits on every request, and the UI must handle a `403` response.
