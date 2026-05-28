---
description: Client-side web security — XSS/DOM XSS, CSP, CSRF, clickjacking, XS-Leaks, third-party JS, CORS, storage
alwaysApply: false
---

# Client-side Web Security

## NEVER
- Insert untrusted strings via `innerHTML`, `outerHTML`, or `document.write`
- Use `eval`, `new Function`, or string-based `setTimeout`/`setInterval`
- Build JavaScript code from untrusted strings
- Use user input directly in `location` or `window.open` URLs
- Build JSON via string concatenation — use `JSON.stringify`
- Use `Access-Control-Allow-Origin: *` for authenticated endpoints
- Rely on CORS for authorization
- Store session tokens or secrets in `localStorage` / `sessionStorage`
- Use GET for state-changing requests
- Allow inline event handlers (`onclick=`) when CSP can disable them

## ALWAYS
- Encode/sanitize per context (HTML, attribute, JavaScript, URL, CSS) — never one universal encoder
- Use `textContent` for HTML; if HTML is required, sanitize with DOMPurify and a strict allow-list
- Adopt Trusted Types and a strict, nonce/hash-based CSP
- Use framework-native CSRF tokens on all state-changing requests; validate Origin/Referer
- Set cookies: `Secure; HttpOnly; SameSite=Lax` or `Strict`; use `__Host-` where possible
- For external `target="_blank"` links: `rel="noopener noreferrer"`
- Subresource Integrity (`integrity="sha384-..."`) for all third-party scripts
- Always specify exact `targetOrigin` in `postMessage`; verify `event.origin` on receive
- Use `wss://` for WebSockets; check origin; require auth; cap message size

## CSP
- Prefer nonce or hash; avoid host allow-lists
- Roll out via `Content-Security-Policy-Report-Only` first; monitor; then enforce
- Block DOM-XSS sinks with `require-trusted-types-for 'script'`
- Baseline: `default-src 'self'; style-src 'self' 'unsafe-inline'; frame-ancestors 'self'; form-action 'self'; object-src 'none'; base-uri 'none'; require-trusted-types-for 'script'; upgrade-insecure-requests`

## CSRF
- Fix XSS first — without it, CSRF tokens are recoverable
- Synchronizer tokens or `__Host-`-prefixed double-submit cookies on POST/PUT/DELETE/PATCH
- Validate Origin/Referer; require a custom header for SPA mutations
- Never validate CSRF tokens on GET

## Clickjacking
- Primary: `Content-Security-Policy: frame-ancestors 'none'` (or narrow allow-list)
- Fallback for legacy browsers: `X-Frame-Options: DENY` or `SAMEORIGIN`
- Add UX confirmation for sensitive actions when framing is required

## XS-Leaks
- Use `SameSite` cookies (`Strict` for sensitive actions)
- Adopt Fetch Metadata (`Sec-Fetch-Site`/`-Mode`/`-Dest`) to block suspicious cross-site requests
- Isolate contexts with COOP/COEP/CORP
- Add per-user tokens to sensitive responses; `Cache-Control: no-store`

## Third-party JavaScript
- Minimize and isolate — prefer sandboxed iframes with `sandbox` + postMessage origin checks
- Subresource Integrity on every external `<script>`/`<link>`: `<script src="…" integrity="sha384-…" crossorigin="anonymous">`
- Provide a first-party sanitized data layer; deny direct DOM access from third-party tags

## Sanitization (DOMPurify)

```javascript
const clean = DOMPurify.sanitize(userHtml, {
  ALLOWED_TAGS: ['b','i','p','a','ul','li'],
  ALLOWED_ATTR: ['href','target','rel'],
  ALLOW_DATA_ATTR: false
});
```

## Client storage
- No secrets in `localStorage`/`sessionStorage` — XSS-reachable
- Prefer `HttpOnly` cookies for session transport
- If client-side storage is unavoidable for non-session secrets, isolate via Web Workers

## Security headers (client impact)
- HSTS to enforce HTTPS
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy` + `Permissions-Policy` to restrict sensitive signals/capabilities

## Checklist
- [ ] Contextual encoding/sanitization at every sink
- [ ] Strict CSP with nonces; Trusted Types enforced; violations monitored
- [ ] CSRF tokens on every state-change; cookies hardened
- [ ] Frame protections set; XS-Leak mitigations (Fetch Metadata, COOP/COEP/CORP)
- [ ] Third-party JS isolated with SRI and sandbox; vetted data layer only
- [ ] HTML5/CORS/WebSocket usage hardened; no secrets in web storage
- [ ] Security headers (HSTS, nosniff, Referrer/Permissions Policy) enabled
