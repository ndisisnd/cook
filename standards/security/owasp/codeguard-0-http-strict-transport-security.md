---
description: HSTS configuration — force HTTPS, prevent MITM, configure max-age and preload correctly
alwaysApply: false
---

# HTTP Strict Transport Security (HSTS)

HSTS instructs browsers to reject HTTP entirely for a domain; it is only honoured over HTTPS — never send it over HTTP.

## NEVER
- Send the `Strict-Transport-Security` header over plain HTTP (it is ignored and wasted)
- Add `includeSubDomains` before confirming all subdomains serve HTTPS
- Add `preload` before reaching a stable 1-year production config
- Remove or reduce `max-age` after going live (browsers cache the policy)

## ALWAYS
- Use `max-age=31536000` (1 year) minimum in production
- Include `includeSubDomains` once all subdomains support HTTPS
- Phased rollout: start with a short `max-age` (600–86400 s), then promote to 1 year
- Audit all internal links and redirects for HTTP references before enabling HSTS
- Verify HSTS header presence in every HTTPS response after deployment

## Configuration by Phase

| Phase | Header value | Notes |
| ----- | ------------ | ----- |
| Testing | `max-age=86400; includeSubDomains` | Short TTL; monitor for breakage |
| Production | `max-age=31536000; includeSubDomains` | Minimum for live sites |
| Preload | `max-age=31536000; includeSubDomains; preload` | Submit to hstspreload.org after stable |

## Threats Addressed
- MITM when users bookmark or type `http://example.com`
- Applications inadvertently serving HTTP links or mixed content
- MITM attackers relying on users accepting invalid certificates (HSTS blocks bypass prompts)

## Preload Warnings
- Preload is effectively permanent — removal takes months to propagate
- Affects every subdomain regardless of future changes
- Only submit to hstspreload.org after the 1-year policy is stable

## Checklist
- [ ] HSTS header present on all HTTPS responses
- [ ] `max-age ≥ 31536000` in production
- [ ] `includeSubDomains` enabled only after subdomain HTTPS audit
- [ ] No HTTP-only subdomains exist when `includeSubDomains` is set
- [ ] Mixed-content warnings absent from browser console
- [ ] `preload` added only after stable production rollout
- [ ] Validated with Mozilla Observatory or securityheaders.com
