---
description: Configure Content Security Policy headers to mitigate XSS, clickjacking, and injection
alwaysApply: false
---

# Content Security Policy (CSP)

CSP complements — but does not replace — input validation, output encoding, and other secure coding practices.

## NEVER
- Use `<meta http-equiv="Content-Security-Policy">` when HTTP headers are available — it lacks full directive support
- Use `'unsafe-eval'` or `'unsafe-inline'` in `script-src` without compensating nonce/hash controls
- Skip `object-src 'none'` — plugins (Flash, Java applets) are an injection vector
- Skip `base-uri 'none'` — base tag injection enables phishing redirects

## ALWAYS
- Deliver CSP via HTTP response header (`Content-Security-Policy`)
- Start with `Content-Security-Policy-Report-Only` to monitor before enforcing
- Use nonce-based or hash-based `script-src` over domain allowlisting
- Generate nonces per-request using CSPRNG (≥128 bits, base64-encoded)
- Set `frame-ancestors` to control framing (supersedes `X-Frame-Options`)
- Set a `report-uri` or `report-to` endpoint to collect violations

## Key Directives

| Directive | Recommended Value | Purpose |
|-----------|-------------------|---------|
| `default-src` | `'self'` | Fallback for unlisted fetch directives |
| `script-src` | `'nonce-{random}' 'strict-dynamic'` | JS sources; prefer nonce/hash |
| `style-src` | `'self'` (add `'unsafe-inline'` only if needed) | CSS sources |
| `object-src` | `'none'` | Block Flash/plugins |
| `base-uri` | `'none'` | Prevent base tag injection |
| `frame-ancestors` | `'none'` or `'self'` | Anti-clickjacking |
| `form-action` | `'self'` | Restrict form submission targets |
| `upgrade-insecure-requests` | (flag) | Auto-upgrade HTTP → HTTPS |

## Nonce-Based Script Policy

```http
Content-Security-Policy: script-src 'nonce-RANDOM_BASE64' 'strict-dynamic'; object-src 'none'; base-uri 'none';
```

```html
<script nonce="RANDOM_BASE64">/* inline script */</script>
```

Server-side nonce generation:
```javascript
// Node.js
const nonce = crypto.randomBytes(16).toString('base64');
```

## Refactoring for CSP Compatibility
- Move inline `onclick="..."` handlers to external `.js` files with `addEventListener`
- Move inline `style="..."` attributes to CSS classes in external stylesheets

## Checklist
- [ ] CSP delivered via HTTP header (not meta tag)
- [ ] `object-src 'none'` and `base-uri 'none'` set
- [ ] `script-src` uses nonce or hash — no bare `'unsafe-inline'`
- [ ] Nonces are cryptographically random and unique per page load
- [ ] `frame-ancestors` directive configured
- [ ] Reporting endpoint active and violations monitored
- [ ] Policy graduated from Report-Only to enforcing
