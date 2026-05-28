---
description: Prevent CSRF attacks on state-changing requests using tokens, SameSite cookies, and origin validation
alwaysApply: false
---

# Cross-Site Request Forgery (CSRF) Prevention

XSS vulnerabilities can defeat all CSRF mitigations — fix XSS first.

## NEVER
- Use GET requests for state-changing operations
- Disable CSRF protection in framework defaults
- Store CSRF tokens in `HttpOnly` cookies — JavaScript must be able to read them
- Transmit CSRF tokens over HTTP (non-TLS)
- Skip login-form CSRF protection (login CSRF is a real attack)

## ALWAYS
- Use framework-native CSRF protection with correct configuration
- Generate unique, unpredictable CSRF tokens per session (HMAC over session ID + secret)
- Validate CSRF tokens on every unsafe HTTP method (POST, PUT, DELETE, PATCH)
- Enforce HTTPS for all CSRF token transmission
- Set session cookies with `Secure; HttpOnly; SameSite=Lax` (use `Strict` for high-security apps)
- Use `__Host-` cookie prefix to prevent subdomain injection
- Validate `Origin`/`Referer` headers as a defense-in-depth layer
- Protect login forms with pre-session tokens; destroy and regenerate session after login

## Framework Configuration

| Framework | Key Setting |
|-----------|-------------|
| Angular | `withXsrfConfiguration({ cookieName: 'XSRF-TOKEN', headerName: 'X-XSRF-TOKEN' })` |
| Next.js | `csrf` middleware on API routes |
| Spring Security | `http.csrf(Customizer.withDefaults())` — enabled by default |
| Django | `CsrfViewMiddleware` in `MIDDLEWARE`; `{% csrf_token %}` in forms |

## Token Patterns

Form submission — hidden field:
```html
<input type="hidden" name="_csrf" value="{{csrfToken}}">
```

AJAX — custom header:
```javascript
headers: { 'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').content }
```

SPA / token-based auth — require custom header on unsafe methods:
```javascript
if (['POST','PUT','DELETE','PATCH'].includes(req.method) && !req.headers['x-requested-with'])
  return res.status(403).json({ error: 'Missing required header' });
```

## Cookie Attributes

| Attribute | Requirement |
|-----------|-------------|
| `Secure` | Mandatory — blocks HTTP transmission |
| `SameSite=Lax` | Minimum; use `Strict` for high-security |
| `__Host-` prefix | Prevents subdomain cookie injection |
| `HttpOnly` | Session cookies only — NOT CSRF token cookies |

## Checklist
- [ ] XSS vulnerabilities addressed before relying on CSRF controls
- [ ] Framework CSRF protection enabled and correctly configured
- [ ] CSRF token validated on all POST/PUT/DELETE/PATCH endpoints
- [ ] GET endpoints perform no state changes
- [ ] Session cookies use `Secure; HttpOnly; SameSite=Lax; __Host-` prefix
- [ ] Origin/Referer header validation in place as secondary layer
- [ ] Login form protected with pre-session token; session regenerated post-login
