---
description: Secure Django configuration — settings, auth, cookies, CSRF, XSS, HTTPS, admin
alwaysApply: false
---

# Django Security

## NEVER
- Set `DEBUG = True` in production
- Hardcode `SECRET_KEY` in source; generate with `get_random_secret_key()` (≥50 chars)
- Use `safe` filter or `mark_safe()` on untrusted input
- Leave the admin at the default `/admin/` URL

## ALWAYS
- Load `SECRET_KEY` from environment; rotate immediately on exposure
- Include `SecurityMiddleware` and `XFrameOptionsMiddleware` in `MIDDLEWARE`
- Include `CsrfViewMiddleware` in `MIDDLEWARE`; add `{% csrf_token %}` to every form
- Set `SESSION_COOKIE_SECURE = True` and `CSRF_COOKIE_SECURE = True`
- Set `SECURE_SSL_REDIRECT = True`; configure `SECURE_PROXY_SSL_HEADER` behind proxies
- Set `SECURE_CONTENT_TYPE_NOSNIFF = True`, `X_FRAME_OPTIONS = 'DENY'`, `SECURE_HSTS_SECONDS` > 0
- Protect views with `@login_required`; configure `AUTH_PASSWORD_VALIDATORS`
- Use `make_password()` / `check_password()` for password operations
- Use `json_script` template filter to pass data to JavaScript safely
- Use rate limiting (`django_ratelimit` or `django-axes`) against brute force
- Keep Django and all dependencies up to date

## Settings Reference

| Setting | Required value |
|---------|---------------|
| `DEBUG` | `False` |
| `SESSION_COOKIE_SECURE` | `True` |
| `CSRF_COOKIE_SECURE` | `True` |
| `SECURE_SSL_REDIRECT` | `True` |
| `SECURE_CONTENT_TYPE_NOSNIFF` | `True` |
| `X_FRAME_OPTIONS` | `'DENY'` or `'SAMEORIGIN'` |
| `SECURE_HSTS_SECONDS` | positive integer |

## Checklist
- [ ] `DEBUG = False` in production; `SECRET_KEY` from environment
- [ ] `SecurityMiddleware`, `XFrameOptionsMiddleware`, `CsrfViewMiddleware` in `MIDDLEWARE`
- [ ] `SESSION_COOKIE_SECURE` and `CSRF_COOKIE_SECURE` both `True`
- [ ] `SECURE_SSL_REDIRECT = True`; HSTS configured
- [ ] `{% csrf_token %}` in all POST forms
- [ ] No `safe`/`mark_safe` on untrusted data; `json_script` used for JS data injection
- [ ] Admin URL changed from default `/admin/`
