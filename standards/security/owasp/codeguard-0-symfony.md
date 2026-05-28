---
description: Symfony-specific security controls covering XSS, CSRF, SQLi, command injection, and session config
alwaysApply: false
---

# Symfony Security

## NEVER
- Use `|raw` Twig filter on untrusted/user-supplied content
- Concatenate user input into Doctrine DQL/SQL strings
- Pass user input to `exec()`, `shell_exec()`, or `system()`
- Disable CSRF protection on state-changing forms
- Serve the app with `APP_ENV=dev` or debug mode in production
- Allow wildcard CORS origins (`*`) in production

## ALWAYS
- Use Twig `{{ }}` default escaping for all output
- Use Doctrine parameterized queries (ORM `setParameter` / QueryBuilder)
- Use Symfony Filesystem component or native PHP functions instead of shell commands
- Validate file uploads with Symfony Validator constraints; store outside public dir with unique names
- Validate file paths with `realpath()` + `str_starts_with($realPath, $realBase)` to prevent traversal
- Set session cookies: `httponly: true`, `secure: auto`, `samesite: lax`
- Set `APP_ENV=prod` and disable debug in production
- Run `symfony check:security` and `composer update` regularly
- Use Symfony secrets for sensitive configuration values
- Implement HSTS, CSP, and X-Frame-Options security headers; enforce HTTPS

## Doctrine Parameterized Query
```php
$query = $em->createQuery("SELECT p FROM App\Entity\Post p WHERE p.id = :id");
$query->setParameter('id', $id);
```

## File Path Traversal Guard
```php
$realBase = realpath($storagePath);
$realPath = realpath($filePath);
if ($realPath === false || !str_starts_with($realPath, $realBase)) {
    // Directory Traversal blocked
}
```

## Session Config (security.yaml)
```yaml
framework:
    session:
        cookie_httponly: true
        cookie_samesite: lax
        cookie_secure: auto
```

## Checklist
- [ ] All Twig output uses `{{ }}` escaping; `|raw` only on verified-safe content
- [ ] Doctrine queries use `setParameter` — no string concatenation
- [ ] No `exec`/`shell_exec`/`system` calls with user input
- [ ] File uploads validated by type/size; stored outside webroot
- [ ] File paths validated with `realpath` traversal check
- [ ] Session cookies configured httponly, secure, samesite
- [ ] `APP_ENV=prod`, debug disabled, `check:security` in CI
