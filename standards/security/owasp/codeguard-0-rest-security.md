---
description: Security requirements for REST APIs — HTTPS, auth, input validation, headers, CORS, and error handling
alwaysApply: false
---

# REST API Security

## NEVER
- Expose REST endpoints over plain HTTP
- Allow unsecured JWTs (`{"alg":"none"}`)
- Verify JWT integrity from JWT header information — use local config only
- Copy `Accept` header directly to `Content-Type` response header
- Include sensitive data (passwords, tokens, API keys) in URL query parameters
- Reveal call stacks, internal hints, or system info in error responses
- Use wildcard origins in production CORS configuration
- Pass client state to backend (REST is stateless — state belongs on resources)

## ALWAYS
- HTTPS-only endpoints; consider mutual TLS for highly privileged services
- Perform access control at each endpoint independently
- Validate JWT claims: `iss`, `aud`, `exp`, `nbf`; maintain denylist for revoked tokens
- Require API keys on every request to protected public endpoints; return `429` on rate limit breach
- Apply HTTP method allowlist; return `405` for unauthorized methods
- Validate all input: length, range, format, type; return `413` for oversized requests
- Reject unexpected/missing `Content-Type`; return `406` or `415`
- Send `Cache-Control: no-store` and all required security headers on every response
- Write audit logs before and after security-relevant events; sanitize log data
- Restrict management endpoints to internal network; require MFA if Internet-accessible

## Security Headers (required on all responses)

| Header | Value |
| ------ | ----- |
| `Cache-Control` | `no-store` |
| `Content-Security-Policy` | `frame-ancestors 'none'` |
| `Content-Type` | correct type matching body |
| `Strict-Transport-Security` | enforce HTTPS |
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |

## HTTP Status Codes

| Code | Use |
| ---- | --- |
| 201 | Created (include `Location` header) |
| 400 | Malformed request |
| 401 | Authentication required |
| 403 | Authorization failed |
| 405 | Method not allowed |
| 406 | Unsupported Accept header |
| 413 | Request too large |
| 415 | Unsupported Content-Type |
| 429 | Rate limit exceeded |
| 500 | Generic server error — no details |

## Checklist
- [ ] All endpoints HTTPS-only; no HTTP fallback
- [ ] JWTs integrity-checked via local config; `alg:none` rejected; denylist implemented
- [ ] Per-endpoint access control enforced
- [ ] HTTP method allowlist active; `405` returned for violations
- [ ] All input validated; oversized requests return `413`
- [ ] Security headers present on every response
- [ ] Sensitive data absent from URLs
- [ ] CORS restricted to specific origins; disabled if cross-domain not required
- [ ] Error responses generic; no stack traces leaked
- [ ] Audit logs written and sanitized
