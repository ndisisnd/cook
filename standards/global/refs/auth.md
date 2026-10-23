---
last_reviewed: 2026-10-23
---

# Auth

Cross-cutting concern: authentication, token storage, session, CSRF, RBAC,
service-to-service auth, and credential hashing. Loads alongside whatever domain also
matched. For injection,
CORS, SSRF, XSS, secret-scanning, and the OWASP detection tables, see
[security.md](security.md). Maps to OWASP Top 10 2025 A01/A04/A06/A07/A08 and
API2/API4/API5/API6 — referenced, not restated.

Each rule below carries a detection signal so review mode can flag it. P0 unless
tagged `P1 (design)`.

## OAuth & Token Flows

- **PKCE on every OAuth2 authorization-code flow; never implicit or password grant.**
  Signal: `response_type=token`, an implicit-flow config, or `grant_type=password`.
- **Access tokens are short-lived and carry `exp`; no long-lived JWT without a
  revocation path.** (OWASP A07:2025 / API2)
  Signal: a JWT signed with no `exp`, or a `maxAge` measured in days.
- **Verify the JWT signature with a pinned algorithm and the expected key; never trust
  `decode` output for authorization, and reject `alg:none`. Validate `aud` and `iss`.**
  (OWASP A08:2025 / API2)
  Signal: `jwt.decode(` feeding an authz decision, `verify` with no `algorithms`
  allowlist, or no `audience`/`issuer` check.
- **Every authorization-code flow sends a `state` value verified on callback and
  validates `redirect_uri` against an exact-match allowlist.** (OWASP A01:2025 / API2)
  Signal: an OAuth callback with no `state` comparison, or a `redirect_uri`/return URL
  taken from the request without an allowlist.
- **PKCE uses `S256`, never `plain`. Reject a `code_verifier` when the auth request had
  no `code_challenge` (downgrade). Redirect URIs are `https`; `http` only for native
  loopback. Send `nonce` for OIDC; add `iss` checks when several auth servers exist
  (mix-up).**
  Signal: `code_challenge_method=plain`, or a token endpoint that accepts a verifier it
  never bound.
- **P1 (design):** refresh tokens are one-time-use and rotated, revocable
  server-side; minimize OAuth scopes to least privilege; sender-constrain high-value
  tokens with DPoP or mTLS. P1 because an agent often cannot confirm these from a diff.

## Token & Session Storage

- **Web: store tokens in `httpOnly` + `Secure` cookies with `SameSite=Lax` by default
  (`Strict` for high-risk cookies such as admin or step-up sessions); never
  `localStorage`/`sessionStorage`. Native: Keychain / Android Keystore / platform
  secure storage.**
  Signal: `localStorage.setItem('…token…')`, `sessionStorage` holding a token, or a
  token in plain app preferences.
- **Cookie-based auth requires CSRF defense** — a synchronizer token or signed
  double-submit token (the token cookie is not `HttpOnly`; the session cookie is), or
  `SameSite` plus an `Origin` check. `SameSite=Lax` alone does not cover
  state-changing `GET`s.
  Signal: a state-changing `POST` under cookie auth with no CSRF token and no
  `SameSite`, or a `GET` handler that mutates state.
- **Regenerate the session on privilege change and invalidate it on logout.**
  (session fixation)
  Signal: a login path with no session rotation, or a logout that does not
  clear/expire the session.

## Session Lifecycle

- **Session IDs come from a CSPRNG with at least 64 bits of entropy (prefer 128), are
  opaque, and carry no PII, role, or state. Accept only IDs the server issued.** Keep
  all session data server-side.
  Signal: a session ID built from user ID/time, or a role or user object in the cookie.
- **Prefer the `__Host-` cookie prefix (`Secure`, `Path=/`, no `Domain`). Session cookies
  omit `Max-Age`/`Expires`. Send `Cache-Control: no-store` on responses that carry
  session IDs or sensitive data.**
- **Enforce idle and absolute timeouts server-side: idle 2-5 min for high-value flows,
  15-30 min otherwise; absolute 4-8 h.** Logout destroys the server-side session, not
  only the cookie.
  Signal: a timeout enforced only in client JS or cookie expiry.
- **Theft detection fingerprints the session server-side (IP range, `User-Agent`,
  `Accept-Language`) and compares on sensitive requests. Never act on one header change
  alone: re-authenticate on a high-risk mismatch, step up on several, log on one.**
  Rotate the session ID on suspected hijack.

## Brute-Force & Abuse Protection

- **Rate-limit and back off repeated auth failures — login, token, OTP, and
  password-reset endpoints; lock or throttle after a threshold.** (OWASP A06:2025 / API4)
  Signal: a login/verify/reset handler with no rate-limit middleware, attempt counter,
  or backoff.
- **Limit per IP, per account, and globally. Never lock an account permanently (it
  becomes a denial-of-service lever) and never lock on password-reset requests; use
  expiring throttles and alerts.** Use CAPTCHA only as a late escalation.
- **Notify the user of a login from a new device; trigger step-up on new device,
  impossible travel, or a breached credential.**

## Authorization (RBAC)

- **RBAC is deny-by-default and additive — start from zero, grant up.**
  (OWASP A01:2025 / API5)
  Signal: a default-allow guard, or a route with no guard.
- **Bind requests to an explicit DTO or allowlist; never bind `req.body` to a model that
  holds `role`, `isAdmin`, `tenantId`, or `balance` (mass assignment). Use allowlists,
  not serializer `exclude`/blocklists.**
  Signal: `new User(req.body)`, `Model.update(req.body)`, `$request->all()`, or
  Laravel `$guarded` as the only defense.
- **Return the same `404` for "missing" and "not yours"; a `403` leaks existence. Never
  let the client choose a weaker auth method. Random UUIDs are defense in depth, not
  access control.**
- **P1 (design):** support MFA and require step-up re-authentication for sensitive
  actions — password/email change, payment, privilege grant. Prefer passkeys
  (WebAuthn/FIDO2) — phishing-resistant — over SMS or TOTP. P1 because presence is
  rarely confirmable from a single diff.
- **Email OTP is not an authenticator (NIST 800-63B-4); SMS/voice is restricted and
  phishable. Do not use them, or security questions, as MFA for PII or financial data.
  Issue single-use recovery codes at enrollment; recovery must not
  bypass identity checks. Verify MFA state server-side on every protected endpoint.
  No "remember this device" on highly sensitive apps.** Security questions are never
  the sole recovery path; if kept, hash the answers like passwords.

## Service-to-Service Auth

- **Machine-to-machine auth uses mTLS or short-lived signed tokens (OAuth2
  client-credentials / workload identity); never a long-lived static API key shared
  across services.** (OWASP API2)
  Signal: a hardcoded or shared-config API key/bearer used for an inter-service call, or
  a service token minted with no `exp`.
- **The receiving service verifies caller identity — mTLS client cert, or token `aud`
  + `iss` — never network reachability alone.** (zero-trust)
  Signal: an internal endpoint that authorizes by source IP / VPC membership with no
  certificate or token check.
- **P1 (design):** scope service credentials to least privilege, rotate them, and source
  them from a secret manager — never commit them. P1 because rotation and scoping rarely
  surface in a single diff.

## Credential Handling

- **Hash credentials with argon2id / bcrypt / scrypt; never MD5/SHA1/plaintext.**
  (OWASP A04:2025)
  Signal: `md5(` or `sha1(` applied to a password field.
- **Minimum parameters: argon2id `m=19456` (19 MiB), `t=2`, `p=1`; scrypt `N=2^17`,
  `r=8`, `p=1`; bcrypt cost >= 10 (72-byte input limit, legacy only);
  PBKDF2-HMAC-SHA256 600,000 iterations (FIPS only).** Tune so one hash takes under
  1 s on production hardware. Store the PHC string, so parameters travel with the hash.
  Signal: a hash cost below these floors, or a hand-rolled salt next to a modern library.
- **Never pre-hash for bcrypt with `bcrypt(sha512(pw))` (password shucking). Accept full
  Unicode and null bytes; never truncate. A pepper, if used, lives in a vault or HSM,
  never in the password database.** Upgrade legacy hashes by wrapping
  (`argon2id(old_hash)`), then replace with a direct hash at next login.
- **Never log tokens, passwords, or session IDs.**
  Signal: a logger call whose arguments include a token, password, or session
  field. See the PII-in-logs scan in [security.md](security.md) — referenced, not
  duplicated.
- **Password-reset and recovery tokens are single-use, high-entropy, and short-expiry;
  invalidate active sessions on a completed reset.** (OWASP API6)
  Signal: a reset token with no expiry or `used` flag, or a reset path that leaves
  existing sessions valid.
- **Reset tokens: 32+ bytes from a CSPRNG, stored hashed, never logged. Build the reset
  URL from a hardcoded or allowlisted domain, never the `Host` header; serve it over
  HTTPS with `Referrer-Policy: no-referrer`. Never auto-login after reset; enforce the
  password policy and CSRF protection on the reset form.**
  Signal: a reset link built from `req.headers.host`, or a session issued by the reset
  handler.
- **Auth responses must not reveal whether an account exists — uniform message, status,
  and timing across login, registration, and reset.**
  Signal: distinct "user not found" vs "wrong password" branches on a login or reset
  path.
- **Approve a payment or other high-risk action against the exact data shown (amount,
  payee): single-use, short-lived, and the flow restarts if the data changes. Verify
  server-side.** (OWASP Transaction Authorization)
  Signal: an approval token not bound to the transaction payload.
- **Compare secrets, tokens, and hashes in constant time.**
  Signal: `==`/`===` on a token, signature, or reset code instead of
  `crypto.timingSafeEqual` / a constant-time compare.
- **Password policy per NIST SP 800-63B-4: minimum 15 characters when the password
  is the only factor, 8 when it is part of MFA; allow at least 64; no composition
  rules (forced mixed case/digits/symbols); no scheduled rotation (force a change
  only on evidence of compromise); check against a breached-password blocklist.**
  Signal: a `minLength` below the floor, a regex requiring character classes, or a
  password-expiry job.
  Check breached passwords through a k-anonymity API (HaveIBeenPwned range query), not
  by sending the full password or hash. Allow paste and password managers.

## Secure Patterns

### Token Storage

```typescript
// httpOnly + Secure + SameSite — not readable by JS, sent only over TLS
res.cookie('session', token, { httpOnly: true, secure: true, sameSite: 'lax' });
// Never: localStorage.setItem('token', token)   // readable by any XSS
```

### Password Hashing

```typescript
import argon2 from 'argon2';
const hash = await argon2.hash(password, { type: argon2.argon2id });
const ok = await argon2.verify(hash, password);
// Never: crypto.createHash('md5').update(password)   // fast, unsalted, reversible
```

### JWT Verification

```typescript
// Pin the algorithm and check aud/iss — rejects alg:none and key confusion
const claims = jwt.verify(token, publicKey, {
  algorithms: ['RS256'],
  audience: 'api://orders',
  issuer: 'https://auth.example.com',
});
// Never: jwt.decode(token)   // no signature check — forgeable
```

### Constant-Time Comparison

```typescript
import { timingSafeEqual } from 'crypto';
const a = Buffer.from(reqToken), b = Buffer.from(expected);
const ok = a.length === b.length && timingSafeEqual(a, b);
// Never: reqToken === expected   // match time leaks the secret
```

### Service-to-Service (client-credentials)

```typescript
// Short-lived token scoped to one audience; verified by the callee (aud + iss + alg)
const { access_token } = await fetchToken({ grantType: 'client_credentials',
  scope: 'orders:read', audience: 'api://orders' });
// Never: headers['x-api-key'] = STATIC_SHARED_KEY   // long-lived, shared, unrotatable
```

## Anti-Patterns

Implicit/password OAuth grants · tokens in `localStorage`/`sessionStorage` · cookie
auth with no CSRF defense · composition rules or forced rotation on passwords · JWT without `exp` · unverified / `alg:none` JWT · missing
OAuth `state` or open `redirect_uri` · default-allow authorization · MD5/SHA1 password
hashing · no rate limiting on login · account enumeration via distinct errors ·
non-constant-time secret comparison · replayable or long-lived password-reset tokens ·
static API keys shared across services · trusting network reachability instead of caller
identity · no session rotation on login or logout · logging credentials.
