---
description: Framework and language security guides — Django/DRF, Laravel/Symfony/Rails, .NET, Java/JAAS, Node.js, PHP
alwaysApply: false
---

# Framework & Language Guides

Apply secure-by-default per platform. Lean on framework built-ins; avoid common pitfalls.

## NEVER (universal across frameworks)
- Ship with debug/development mode enabled in production (Django `DEBUG`, Laravel `APP_DEBUG`, Symfony `APP_ENV=dev`)
- Use `exclude` / `__all__` / `$request->all()` style "all fields" serialization for incoming data
- Use `mark_safe`, Blade `{!! ... !!}`, Twig `|raw`, Rails `raw`/`html_safe`, Razor `Html.Raw` on untrusted data
- Concatenate user input into SQL — always parameterize (ORM, PreparedStatement, Eloquent, Doctrine, ActiveRecord)
- Call `eval`, `exec`, `system`, `shell_exec`, `backticks`, `child_process.exec`, `Process.exec`, `Runtime.exec` with untrusted input
- Disable CSRF middleware on state-changing endpoints
- Hardcode secrets in source or commit them to repos

## ALWAYS (universal)
- Enable HTTPS redirects + HSTS + secure cookie flags
- Use the framework's built-in CSRF, XSS escaping, and session protections
- Parameterize all data access; allow-list dynamic identifiers
- Centralize secret management; source from env/secret manager validated at boot
- Run SCA and static analysis on every change; keep dependencies updated

## Django
- Enable `SecurityMiddleware`, clickjacking middleware, MIME-sniffing protection
- `SECURE_SSL_REDIRECT = True`; configure HSTS; `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`
- `CsrfViewMiddleware` + `{% csrf_token %}`; rely on template auto-escape; `json_script` for embedded JS data
- Use `django.contrib.auth` + `AUTH_PASSWORD_VALIDATORS`; generate secret via `get_random_secret_key`

## Django REST Framework
- Set `DEFAULT_AUTHENTICATION_CLASSES` and a restrictive `DEFAULT_PERMISSION_CLASSES` — never leave `AllowAny`
- Call `self.check_object_permissions(request, obj)` for object-level authz
- Serializers: explicit `fields=[...]`; never `exclude` or `__all__`
- Enable throttling; disable unsafe HTTP methods where not needed

## Laravel
- Production: `APP_DEBUG=false`; `php artisan key:generate`; correct file permissions
- Enable cookie encryption middleware; cookies `http_only`, `same_site`, `secure`; short session lifetimes
- Mass assignment: use `$request->only()` / `$request->validated()` — never `$request->all()`
- Eloquent parameter binding; validate dynamic identifiers
- Blade auto-escape; avoid `{!! !!}` on untrusted data
- File uploads: validate `file`, size, and `mimes`; sanitize filenames with `basename`
- Ensure CSRF middleware + `@csrf` in forms

## Symfony
- Twig auto-escape; avoid `|raw`
- `csrf_token()` + `isCsrfTokenValid()` for manual flows; Forms include tokens by default
- Doctrine parameterized queries — never concatenate
- Avoid `exec`/`shell_exec`; use the Filesystem component
- Uploads: `#[File(...)]` validation; store outside public; unique filenames
- Validate paths via `realpath`/`basename`; enforce allowed roots
- Configure secure cookies, firewalls, authenticators

## Ruby on Rails
- Avoid `eval`/`system`/backticks/`exec`/`spawn`/`IO.popen`/`Process.exec` on untrusted input
- Parameterize queries; use `sanitize_sql_like` for LIKE patterns
- Default auto-escape; avoid `raw`/`html_safe` on untrusted data; use `sanitize` with allow-list
- DB-backed session store; `config.force_ssl = true`; Devise or proven auth lib
- `protect_from_forgery` on state-changing actions; validate redirect targets against an allow-list
- Configure `rack-cors` with explicit origins — never `*` for credentialed routes

## .NET (ASP.NET Core)
- Keep runtime + NuGet packages updated; SCA in CI
- `[Authorize]` attributes + server-side checks; prevent IDOR via owner scoping
- ASP.NET Identity with lockouts; cookies `HttpOnly`/`Secure`; short timeouts
- PBKDF2 (or equivalent) for password hashing; AES-GCM for encryption; DPAPI for local secrets; TLS 1.2+
- Parameterize SQL/LDAP; allow-list validation
- Enforce HTTPS redirects; remove version headers; set CSP/HSTS/`X-Content-Type-Options`
- Anti-forgery tokens on state-changing actions

## Java & JAAS
- `PreparedStatement` / named JPA parameters — never concatenate
- Validate with allow-list; sanitize output with reputable libs; encode per context
- Parameterized logging (SLF4J `{}`) to prevent log injection
- AES-GCM with secure random nonces; KMS/HSM-stored keys
- JAAS: configure `LoginModule` stanzas; implement `initialize/login/commit/abort/logout`; segregate public/private credentials; manage subject principals properly

## Node.js
- Limit request size; validate input; encode/escape output
- Never `eval` or `child_process.exec` with user input — use `execFile` with array args
- `helmet` for security headers; `hpp` for HTTP Parameter Pollution
- Rate-limit auth endpoints; monitor event-loop lag; handle `uncaughtException`/`unhandledRejection` cleanly
- Cookies: `secure`, `httpOnly`, `sameSite`
- `NODE_ENV=production`; `npm audit` in CI; security linters; ReDoS testing

## PHP configuration
- `php.ini`: `expose_php=Off`; log errors (don't display); restrict `allow_url_fopen`/`allow_url_include`; set `open_basedir`
- Disable dangerous functions via `disable_functions`; consider Snuffleupagus for additional hardening
- Session cookies `Secure; HttpOnly; SameSite=Strict`; strict-session mode on
- Cap upload size/count and memory/post-size/execution-time limits

## Checklist
- [ ] Debug/dev mode off in production; built-in CSRF/XSS/session protections enabled
- [ ] All data access parameterized; no dangerous exec with untrusted input
- [ ] HTTPS + HSTS + secure headers + secure cookie flags configured
- [ ] Secrets centralized, never hardcoded; redirects/identifiers allow-listed
- [ ] Dependencies current; SCA + static analysis in CI
