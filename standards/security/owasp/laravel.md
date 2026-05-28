---
description: Laravel-specific security controls — SQLi, XSS, CSRF, mass assignment, file uploads, and more
alwaysApply: false
---

# Laravel Security

## NEVER
- Set `APP_DEBUG=true` in production
- Use `$request->all()` / `forceFill()` for model binding — allows mass assignment
- Use raw SQL string concatenation; always use Eloquent bindings or parameterized queries
- Use `{!! ... !!}` (unescaped Blade output) with untrusted data
- Call `unserialize()`, `eval()`, or `extract()` on user input
- Pass user-controlled filenames to storage without `basename()` sanitization
- Call `exec()` / shell functions with raw user input; use `escapeshellarg` / `escapeshellcmd`

## ALWAYS
- Generate a fresh application key: `php artisan key:generate`
- Enable `EncryptCookies` and `VerifyCsrfToken` middleware in the `web` group
- Use `$request->only()` or `$request->validated()` for model input
- Validate column names before dynamic `orderBy` / query clauses
- Validate file uploads for type and size (`file|size:100|mimes:jpg,bmp,png`)
- Apply rate limiting (`throttle` middleware) to sensitive routes
- Run Enlightn Security Checker and keep dependencies updated

## Key Patterns

| Concern | Vulnerable | Safe |
|---|---|---|
| SQL | `whereRaw('email = "'.$input.'"')` | `whereRaw('email = ?', [$input])` |
| XSS | `{!! $input !!}` | `{{ $input }}` |
| File path | `storeAs($id, $input)` | `storeAs($id, basename($input))` |
| Mass assign | `forceFill($request->all())` | `fill($request->only([...]))` |

## Configuration
- Set file permissions: dirs `775`, files `664`, executables `775`
- Session config (`config/session.php`): `http_only: true`, `same_site: lax`, `secure: true`, `lifetime: 15`

## Checklist
- [ ] `APP_DEBUG=false` in production; application key generated
- [ ] CSRF and cookie encryption middleware active on `web` group
- [ ] All model writes use `only()`/`validated()`, not `all()`/`forceFill()`
- [ ] No raw SQL string concatenation; parameterized bindings used throughout
- [ ] Blade templates use `{{ }}` for all untrusted output
- [ ] File uploads validated (type + size); filenames sanitized with `basename()`
- [ ] Shell commands escape args; `eval`/`unserialize`/`extract` not used on user input
- [ ] Rate limiting applied to auth and sensitive routes
