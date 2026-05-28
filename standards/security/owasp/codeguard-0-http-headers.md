---
description: Required and prohibited HTTP response headers — XSS, clickjacking, MIME, transport, CORS
alwaysApply: false
---

# HTTP Security Headers

## NEVER
- Emit `X-Powered-By`, `X-AspNet-Version`, or `X-AspNetMvc-Version` headers
- Use a `Server` header that reveals software name or version
- Set `Access-Control-Allow-Origin: *` on credentialed or sensitive endpoints
- Rely solely on `X-XSS-Protection` for XSS defence — use CSP instead

## ALWAYS
- Set `Content-Security-Policy` with at least `default-src`, `script-src`, and `frame-ancestors`
- Set `Strict-Transport-Security: max-age=31536000; includeSubDomains` (min 1-year max-age)
- Set `X-Content-Type-Options: nosniff`
- Set `Cache-Control: no-store, max-age=0` on sensitive responses
- Set `Cross-Origin-Embedder-Policy`, `Cross-Origin-Resource-Policy`, and `Cross-Origin-Opener-Policy`
- Set session/sensitive cookies with `Secure; HttpOnly; SameSite=Strict`
- Restrict `Access-Control-Allow-Origin` to an explicit origin allowlist

## Required Headers

| Header | Required value / guidance |
| ------ | ------------------------- |
| `Content-Security-Policy` | `default-src 'self'; script-src 'self'; frame-ancestors 'none'` (harden per app) |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` |
| `X-Content-Type-Options` | `nosniff` |
| `Cache-Control` (sensitive) | `no-store, max-age=0` |
| `Cross-Origin-Embedder-Policy` | `require-corp` |
| `Cross-Origin-Resource-Policy` | `same-origin` |
| `Cross-Origin-Opener-Policy` | `same-origin` |

## Clickjacking & XSS Protection
- Use `CSP: frame-ancestors 'none'` **or** `X-Frame-Options: DENY` — both preferred
- CSP `script-src` must restrict inline/eval; do not use `unsafe-inline` or `unsafe-eval` without hash/nonce

## Prohibited Headers — Remove Before Response
- `X-Powered-By`
- `Server` (or set to a non-revealing static value)
- `X-AspNet-Version`
- `X-AspNetMvc-Version`

## Checklist
- [ ] CSP present with `default-src`, `script-src`, and `frame-ancestors`
- [ ] HSTS set with `max-age ≥ 31536000`
- [ ] `X-Content-Type-Options: nosniff` present
- [ ] `Cross-Origin-*` isolation headers set
- [ ] Server/version-revealing headers stripped
- [ ] `Access-Control-Allow-Origin` is not `*` on credentialed endpoints
- [ ] Session cookies have `Secure; HttpOnly; SameSite=Strict`
