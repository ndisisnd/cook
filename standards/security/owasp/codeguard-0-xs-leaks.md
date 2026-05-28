---
description: Prevent Cross-Site Leaks (XS-Leaks) via cookies, framing, isolation headers, and cache controls
alwaysApply: false
---

# XS-Leaks Prevention

XS-Leaks exploit browser side-channels (error messages, frame counting, timing, cache probing, response size) to extract cross-origin user state.

## NEVER
- Omit `SameSite` from session cookies — never rely on browser defaults
- Use `SameSite=None` without `Secure`
- Send `postMessage` to `'*'` with sensitive data
- Accept `postMessage` without verifying `event.origin`

## ALWAYS
- Set `SameSite=Strict` on cookies used for sensitive actions
- Set `SameSite=Lax` on cookies needed for normal top-level navigation
- Use `SameSite=None; Secure` only when third-party access is unavoidable
- Emit `Cache-Control: no-store` on all sensitive/user-specific API responses
- Set `Cross-Origin-Resource-Policy: same-origin` on sensitive resources
- Set `Cross-Origin-Opener-Policy: same-origin` to isolate browsing context
- Set `frame-ancestors 'self'` via CSP and `X-Frame-Options: SAMEORIGIN` as fallback
- Scope `postMessage` to exact trusted origins; verify origin on receive

## Response Headers

| Header | Value | Purpose |
|--------|-------|---------|
| `Content-Security-Policy` | `frame-ancestors 'self'` | Framing protection |
| `X-Frame-Options` | `SAMEORIGIN` | Legacy framing fallback |
| `Cross-Origin-Resource-Policy` | `same-origin` | Resource isolation |
| `Cross-Origin-Opener-Policy` | `same-origin` | Browsing context isolation |
| `Cross-Origin-Embedder-Policy` | `require-corp` | Maximum isolation (pair with COOP) |
| `Cache-Control` | `no-store` | Prevent cache probing on sensitive endpoints |

## Fetch Metadata Defence

Inspect `Sec-Fetch-Site`, `Sec-Fetch-Mode`, `Sec-Fetch-Dest` on sensitive endpoints; reject `cross-site` requests that have no legitimate cross-origin use case.

## Cache Leak Prevention

- Add user-specific tokens to URLs of sensitive resources to prevent cache-probing
- Disable caching (`no-store`) for all user-state-revealing responses
- Do not allow shared caches to store authenticated responses

## Checklist
- [ ] All session cookies carry explicit `SameSite` attribute
- [ ] Sensitive cookies use `SameSite=Strict`; `Secure` and `HttpOnly` set
- [ ] `Cache-Control: no-store` on all user-specific API endpoints
- [ ] COOP + CORP headers set (`same-origin`)
- [ ] CSP `frame-ancestors` + `X-Frame-Options` both present
- [ ] `postMessage` targets exact origin; receivers verify `event.origin`
- [ ] Fetch Metadata middleware blocks unexpected cross-site requests
