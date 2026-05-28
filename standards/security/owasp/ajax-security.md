---
description: AJAX security — prevent injection, XSS, CSRF, and client-side secret leakage
alwaysApply: false
---

# AJAX Security

## NEVER
- Call `eval()`, `new Function()`, `setTimeout(str)`, or `setInterval(str)` with dynamic/untrusted strings
- Assign untrusted input to `.innerHTML` without a sanitization library
- Perform encryption or handle secrets on the client side
- Build JSON/XML via string concatenation with user-supplied data
- Rely on client-side validation as the only security check
- Expose authentication tokens without `HttpOnly` + `Secure` cookie flags

## ALWAYS
- Use anonymous functions for `setTimeout`/`setInterval` callbacks
- Use `.textContent` for plain text; sanitize with a trusted library before `.innerHTML`
- Move all encryption and secret operations to the server
- Serialize data with `JSON.stringify()` or trusted XML serializer APIs
- Re-validate all input server-side — AJAX endpoints are directly callable by attackers
- Include anti-CSRF tokens on every state-changing AJAX request
- Return JSON responses with an outer object `{}` (not a bare array) to prevent JSON hijacking
- Validate AJAX request/response payloads against a JSON or XML schema

## Checklist
- [ ] No `eval()` / `new Function()` / string-arg timer calls in client code
- [ ] `.innerHTML` never receives unvalidated user data
- [ ] All secrets and crypto operations are server-side only
- [ ] JSON built via `JSON.stringify()`, not string concatenation
- [ ] Anti-CSRF token present on every mutating AJAX call
- [ ] Session/auth cookies have `HttpOnly` and `Secure` flags
- [ ] Server validates all AJAX inputs independently of client validation
