# Auth

Cross-cutting concern: authentication, token storage, session, CSRF, RBAC, and
credential hashing. Loads alongside whatever domain also matched. For injection,
CORS, SSRF, XSS, secret-scanning, and the OWASP detection tables, see
[security.md](security.md). Maps to OWASP A02/A07 and API1/API2/API5 — referenced,
not restated.

Each rule below carries a detection signal so review mode can flag it. P0 unless
tagged `P1 (design)`.

## OAuth & Token Flows

- **PKCE on every OAuth2 authorization-code flow; never implicit or password grant.**
  Signal: `response_type=token`, an implicit-flow config, or `grant_type=password`.
- **Access tokens are short-lived and carry `exp`; no long-lived JWT without a
  revocation path.** (OWASP A07 / API2)
  Signal: a JWT signed with no `exp`, or a `maxAge` measured in days.
- **P1 (design):** refresh tokens are one-time-use and rotated, revocable
  server-side; minimize OAuth scopes to least privilege. P1 because an agent often
  cannot confirm these from a diff.

## Token & Session Storage

- **Store tokens in `httpOnly` + `Secure` + `SameSite` cookies; never
  `localStorage`/`sessionStorage`.**
  Signal: `localStorage.setItem('…token…')`, or `sessionStorage` holding a token.
- **Cookie-based auth requires CSRF defense** — a double-submit token, or
  `SameSite=Strict` plus an origin check.
  Signal: a state-changing `POST` under cookie auth with no CSRF token and no
  `SameSite`.
- **Regenerate the session on privilege change and invalidate it on logout.**
  (session fixation)
  Signal: a login path with no session rotation, or a logout that does not
  clear/expire the session.

## Authorization (RBAC)

- **RBAC is deny-by-default and additive — start from zero, grant up.**
  (OWASP A01 / API5)
  Signal: a default-allow guard, or a route with no guard.

## Credential Handling

- **Hash credentials with argon2id / bcrypt / scrypt; never MD5/SHA1/plaintext.**
  (OWASP A02)
  Signal: `md5(` or `sha1(` applied to a password field.
- **Never log tokens, passwords, or session IDs.**
  Signal: a logger call whose arguments include a token, password, or session
  field. See the PII-in-logs scan in [security.md](security.md) — referenced, not
  duplicated.

## Anti-Patterns

Implicit/password OAuth grants · tokens in `localStorage`/`sessionStorage` · cookie
auth with no CSRF defense · JWT without `exp` · default-allow authorization ·
MD5/SHA1 password hashing · no session rotation on login or logout · logging
credentials.
