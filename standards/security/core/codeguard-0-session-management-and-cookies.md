---
description: Session management and secure cookies — rotation, fixation, timeouts, theft detection
alwaysApply: false
---

# Session Management & Cookies

## NEVER
- Accept an incoming session ID that was not issued by the server (session fixation)
- Embed PII, role, privilege, or business state in the cookie value
- Store session tokens in `localStorage` or `sessionStorage` (XSS-reachable)
- Use GET for state-changing requests (CSRF-prone)
- Mix HTTP and HTTPS within a session
- Send `Strict-Transport-Security` over HTTP
- Use a single session ID across authentication and privilege-elevation boundaries

## ALWAYS
- Generate session IDs with a CSPRNG, ≥64 bits of entropy (prefer 128+), opaque and meaningless
- Use a generic cookie name (e.g., `id`) rather than the framework default
- Store all session data server-side; encrypt the store at rest if it holds sensitive data
- Set cookies: `Secure; HttpOnly; SameSite=Strict` (or `Lax` if flow requires); narrow `Path` and `Domain`; prefer no `Max-Age`/`Expires`
- Use the `__Host-` prefix where the deployment allows
- Enforce HTTPS site-wide; enable HSTS
- Send `Cache-Control: no-store` on responses containing session IDs or sensitive data
- Regenerate session ID on authentication, password change, and any privilege elevation; invalidate the prior ID

## Lifecycle & timeouts
- Idle timeout: 2–5 min for high-value flows; 15–30 min for lower-risk; enforce server-side
- Absolute timeout: 4–8 hours; enforce server-side
- Provide a visible logout that invalidates the server session and clears the client cookie

## Theft detection
- Capture a server-side fingerprint at session establishment (IP, User-Agent, Accept-Language, `sec-ch-ua` where available)
- Allow benign drift (subnet change, UA minor update); flag larger deviations
- Risk-based response:
  - High risk → require re-authentication; rotate session ID
  - Medium risk → step-up challenge; rotate session ID
  - Low risk → log
- Always regenerate session ID when potential hijacking is detected

## Telemetry
- Log lifecycle events (creation, rotation, termination) using a salted hash of the session ID — never the raw value
- Monitor for session-ID brute force and anomalous concurrent usage

## Example header

```
Set-Cookie: __Host-id=<opaque>; Secure; HttpOnly; SameSite=Strict; Path=/
```

## Checklist
- [ ] CSPRNG session IDs, ≥64 bits entropy, opaque, server-issued only
- [ ] `Secure; HttpOnly; SameSite` set; tight Path/Domain; `__Host-` where possible
- [ ] HTTPS-only with HSTS; no mixed content
- [ ] Regenerate ID on auth and privilege changes; invalidate old IDs
- [ ] Idle + absolute timeouts enforced server-side; full logout implemented
- [ ] `Cache-Control: no-store` on sensitive responses
- [ ] Server-side fingerprint with risk-based response
- [ ] No session tokens in web storage; framework defaults hardened
