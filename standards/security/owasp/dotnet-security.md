---
description: Secure .NET/ASP.NET Core — auth, crypto, injection prevention, CSRF, headers, serialization
alwaysApply: false
---

# .NET Security

## NEVER
- Write custom cryptographic functions
- Use `BinaryFormatter` for untrusted data
- Concatenate user input into SQL or OS commands
- Use default passwords or credentials
- Log passwords, tokens, or sensitive data
- Deserialize untrusted data without validation and digital signature check
- Use `TypeNameHandling != None` in JSON.NET on untrusted data

## ALWAYS
- Apply `[Authorize]` on all externally facing controllers/actions; validate permissions server-side
- Use ASP.NET Core Identity with account lockout and secure password policies
- Set cookies `HttpOnly = true`, `requireSSL = true`; reduce session timeout; disable sliding expiration
- Throttle login, registration, and password reset against brute force
- Use SHA-512 for general hashing; PBKDF2 for passwords; AES-GCM for encryption; enforce TLS 1.2+
- Use DPAPI for secure local storage
- Use parameterized queries or Entity Framework exclusively; use `IPAddress.TryParse` for allowlist validation
- Add `[ValidateAntiForgeryToken]` on POST/PUT; use `@Html.AntiForgeryToken()` in forms; remove CSRF cookie on logout
- Force HTTPS with `app.UseHttpsRedirection()`; set HSTS header
- Set `X-Frame-Options`, `X-Content-Type-Options`, `Content-Security-Policy`, `Strict-Transport-Security`; remove `X-Powered-By`
- Disable debug/tracing in production via web.config transforms
- Use `System.Text.Json`, `XmlSerializer`, or `DataContractSerializer`; validate signatures before deserialization
- Log auth failures and access control violations via `ILogger`; include user context
- Keep .NET and NuGet packages updated; run SCA in CI/CD

## Secure Headers (web.config)
```xml
<add name="Content-Security-Policy" value="default-src 'none'; style-src 'self'; img-src 'self'" />
<add name="X-Content-Type-Options" value="NOSNIFF" />
<add name="X-Frame-Options" value="DENY" />
<add name="X-XSS-Protection" value="0" />
<remove name="X-Powered-By" />
```

## Checklist
- [ ] All endpoints have `[Authorize]`; permissions validated server-side
- [ ] Parameterized queries/EF used; no string-concatenated SQL
- [ ] `BinaryFormatter` absent; deserializers validate types and signatures
- [ ] CSRF tokens on all state-changing forms; removed on logout
- [ ] HTTPS enforced; HSTS and security headers configured
- [ ] Passwords hashed with PBKDF2; SHA-512 for other hashing; no custom crypto
- [ ] Debug/trace disabled in production; no sensitive data in logs
