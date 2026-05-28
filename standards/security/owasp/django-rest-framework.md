---
description: Secure Django REST Framework APIs — auth, serializers, throttling, injection prevention
alwaysApply: false
---

# Django REST Framework Security

## NEVER
- Leave `DEFAULT_PERMISSION_CLASSES` as `AllowAny` on non-public endpoints
- Use `Meta.exclude` or `Meta.fields = "__all__"` in serializers or ModelForms
- Use raw SQL with user input: `raw()`, `extra()`, `cursor.execute()` with unsanitized values
- Use `eval()`, `exec()`, or `yaml.load()` on untrusted input
- Hardcode `SECRET_KEY`, API keys, or passwords in source code
- Set `DEBUG = True` or `DEBUG_PROPAGATE_EXCEPTIONS = True` in production
- Log passwords, tokens, or PII

## ALWAYS
- Set explicit `fields = [...]` allowlists in all DRF serializers
- Call `self.check_object_permissions(request, obj)` when overriding `get_object()`
- Set `DEFAULT_AUTHENTICATION_CLASSES` for all non-public endpoints
- Enable CSRF protection with `SessionAuthentication`
- Configure `DEFAULT_THROTTLE_CLASSES` for DoS defence; prefer gateway/WAF enforcement
- Inject secrets via environment variables or a secrets manager
- Validate and sanitize all incoming data with Django forms or DRF serializer validators
- Set security headers: `SECURE_CONTENT_TYPE_NOSNIFF`, `X_FRAME_OPTIONS = 'DENY'`, `SECURE_BROWSER_XSS_FILTER`
- Implement CSP via django-csp middleware
- Disable unused HTTP methods at the API level
- Log auth failures and authorization denials with sufficient context (no sensitive data)

## Injection Prevention

| Dangerous | Safe alternative |
|-----------|-----------------|
| `raw(user_input)` | ORM queryset with params |
| `extra(where=[user_input])` | parameterized `.filter()` |
| `yaml.load(data)` | `yaml.safe_load(data)` |
| `eval(user_input)` | validate + whitelist logic |

## Checklist
- [ ] `DEFAULT_PERMISSION_CLASSES` restricts access; `AllowAny` only on explicitly public views
- [ ] All serializers use explicit `fields` allowlist, not `exclude` or `"__all__"`
- [ ] `check_object_permissions()` called on every `get_object()` override
- [ ] `DEBUG` and `DEBUG_PROPAGATE_EXCEPTIONS` are `False` in production
- [ ] No raw SQL or dynamic code execution on user input
- [ ] Secrets injected from environment; none hardcoded
- [ ] Throttling and security headers configured
