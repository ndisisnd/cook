---
description: Required and prohibited HTTP response headers, and HSTS configuration — XSS, clickjacking, MIME, transport, CORS, phased HSTS rollout and preload
alwaysApply: false
---

# HTTP Security Headers

## NEVER
- Emit `X-Powered-By`, `X-AspNet-Version`, or `X-AspNetMvc-Version` headers
- Use a `Server` header that reveals software name or version
- Set `Access-Control-Allow-Origin: *` on credentialed or sensitive endpoints
- Rely solely on `X-XSS-Protection` for XSS defence — use CSP instead
- Send the `Strict-Transport-Security` header over plain HTTP — it is ignored and wasted
- Add `includeSubDomains` before confirming all subdomains serve HTTPS
- Add `preload` before reaching a stable 1-year production HSTS config
- Remove or reduce `max-age` after going live — browsers cache the policy

## ALWAYS
- Set `Content-Security-Policy` with at least `default-src`, `script-src`, and `frame-ancestors`
- Set `Strict-Transport-Security: max-age=31536000; includeSubDomains` (min 1-year max-age)
- Set `X-Content-Type-Options: nosniff`
- Set `Cache-Control: no-store, max-age=0` on sensitive responses
- Set `Cross-Origin-Embedder-Policy`, `Cross-Origin-Resource-Policy`, and `Cross-Origin-Opener-Policy`
- Set session/sensitive cookies with `Secure; HttpOnly; SameSite=Strict`
- Restrict `Access-Control-Allow-Origin` to an explicit origin allowlist
- Phased HSTS rollout: start with short `max-age` (600–86400 s), promote to 1 year, then add `preload`
- Audit all internal links and redirects for HTTP references before enabling HSTS

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

## HSTS Configuration

HSTS instructs browsers to reject HTTP entirely for a domain and is only honoured over HTTPS.

### Configuration by Phase

| Phase | Header value | Notes |
| ----- | ------------ | ----- |
| Testing | `max-age=86400; includeSubDomains` | Short TTL; monitor for breakage |
| Production | `max-age=31536000; includeSubDomains` | Minimum for live sites |
| Preload | `max-age=31536000; includeSubDomains; preload` | Submit to hstspreload.org after stable |

### Threats Addressed by HSTS
- MITM when users bookmark or type `http://example.com`
- Applications inadvertently serving HTTP links or mixed content
- MITM attackers relying on users accepting invalid certificates (HSTS blocks bypass prompts)

### Preload Warnings
- Preload is effectively permanent — removal takes months to propagate
- Affects every subdomain regardless of future changes
- Only submit to hstspreload.org after the 1-year policy is stable

## Checklist
- [ ] CSP present with `default-src`, `script-src`, and `frame-ancestors`
- [ ] HSTS set with `max-age ≥ 31536000` on all HTTPS responses (never on plain HTTP)
- [ ] `includeSubDomains` enabled only after subdomain HTTPS audit; no HTTP-only subdomains exist
- [ ] `X-Content-Type-Options: nosniff` present
- [ ] `Cross-Origin-*` isolation headers set
- [ ] Server/version-revealing headers stripped
- [ ] `Access-Control-Allow-Origin` is not `*` on credentialed endpoints
- [ ] Session cookies have `Secure; HttpOnly; SameSite=Strict`
- [ ] Mixed-content warnings absent from browser console
- [ ] `preload` added only after stable production rollout; validated with Mozilla Observatory or securityheaders.com
