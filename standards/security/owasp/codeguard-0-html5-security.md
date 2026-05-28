---
description: Secure HTML5 development — postMessage, CORS, WebSocket, storage, DOM, CSRF, cookies
alwaysApply: false
---

# HTML5 Security

## NEVER
- Use `"*"` as target origin in `postMessage` calls
- Use `"*"` in `Access-Control-Allow-Origin`
- Use `eval()` or `Function()` on message data from `postMessage`
- Store passwords, tokens, API keys, or PII in `localStorage` or `sessionStorage`
- Use unencrypted `ws://` in production — only `wss://`
- Create Web Workers from user-supplied URLs or content
- Set `innerHTML` with unvalidated user-supplied content
- Open external links with `target="_blank"` without `rel="noopener noreferrer"`

## ALWAYS
- Verify `event.origin` against a full-domain allowlist in every message handler
- Validate and sanitize all data received via `postMessage` before processing
- Use `textContent` (not `innerHTML`) when rendering received message content
- Implement server-side CSRF tokens on all state-changing forms and AJAX requests
- Set cookies with `HttpOnly`, `Secure`, and `SameSite=Strict` (or `Lax`)
- Require explicit user permission before accessing Geolocation API
- Transmit location data over HTTPS only
- Use HTTPS for all manifest files and cached offline resources

## Web Messaging & CORS
- Validate the full domain in `event.origin` — partial matching enables subdomain takeover
- Reject mixed content (HTTP requests from HTTPS origins)
- Do not rely on `Origin` header alone for server-side access control — it can be spoofed outside browsers
- CORS does not prevent CSRF — implement CSRF tokens independently

## WebSocket Security
- Verify `Origin` header against allowlist during handshake
- Implement application-level authentication (JWT or equivalent) for each connection
- Enforce connection limits and message size caps to prevent DoS
- Implement token revocation and denylist mechanisms

## Client-Side Storage
- Prefer `sessionStorage` over `localStorage` when cross-session persistence is not required
- Encrypt sensitive data if client-side storage is unavoidable
- Validate and sanitize all data retrieved from storage before use
- Avoid hosting multiple apps on the same origin to prevent storage access conflicts

## DOM & Link Security
- Set `window.opener = null` when using `window.open()` for external URLs
- Use `iframe sandbox` with minimal permissions for untrusted content
- Pair `sandbox` with `X-Frame-Options` for defense-in-depth
- When `innerHTML` is unavoidable, sanitize with DOMPurify

## Input Fields & Cookies
- `autocomplete="off"` on sensitive fields (passwords, credit cards, SSN)
- `spellcheck="false" autocorrect="off" autocapitalize="off"` on credential inputs
- Use `__Secure-` or `__Host-` cookie prefixes for additional hardening
- Validate CSRF tokens server-side for all POST, PUT, DELETE requests

## Checklist
- [ ] `postMessage` target origin is always a specific domain, never `"*"`
- [ ] CORS `Allow-Origin` restricted to explicit allowlist
- [ ] WebSockets use `wss://` with per-connection auth
- [ ] No sensitive data in `localStorage`/`sessionStorage`
- [ ] All external `_blank` links have `rel="noopener noreferrer"`
- [ ] Session cookies set `HttpOnly; Secure; SameSite=Strict`
- [ ] CSRF tokens validated server-side on all state-changing requests
