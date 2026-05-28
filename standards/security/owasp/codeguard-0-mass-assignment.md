---
description: Mass assignment prevention — block attackers from overwriting sensitive model fields via HTTP parameters
alwaysApply: false
---

# Mass Assignment Prevention

Mass assignment lets attackers inject parameters (e.g., `isAdmin=true`) that bind to sensitive model fields when frameworks auto-map request bodies to objects.

## NEVER
- Bind HTTP request bodies directly to domain objects that contain privilege or sensitive fields
- Use automatic binding without an explicit allowlist or blocklist
- Prefer blocklisting over allowlisting — a missed field is a vulnerability

## ALWAYS
- Use DTOs that expose only safe, editable fields (sensitive fields simply absent)
- Apply framework allowlisting to permit only known-safe fields
- Regularly audit model/entity definitions for sensitive attributes
- Use allowlisting over blocklisting when both are available

## Framework Implementations

**Spring MVC — allowlist**
```java
@InitBinder
public void initBinder(WebDataBinder binder, WebRequest request) {
    binder.setAllowedFields(["userid","password","email"]);
}
```

**NodeJS + Mongoose — allowlist**
```javascript
var user = new User(_.pick(req.body, ['userid', 'password', 'email']));
```

**PHP Laravel / Eloquent — allowlist (`$fillable`) vs blocklist (`$guarded`)**
```php
protected $fillable = ['userid','password','email']; // prefer this
protected $guarded  = ['isAdmin'];                   // fallback only
```

## Exploitability Conditions
Mass assignment is exploitable when the attacker can guess sensitive field names, has source code access, or the target object has an empty constructor.

## Checklist
- [ ] No controller directly binds `request.body` / `$request->all()` to domain objects
- [ ] DTOs used or framework allowlist configured for every model-binding endpoint
- [ ] No sensitive fields (`isAdmin`, `role`, `balance`, etc.) reachable via mass binding
- [ ] Allowlist preferred over blocklist; blocklist entries audited for completeness
- [ ] Model definitions reviewed for newly added sensitive attributes
