# Auth

Cross-cutting concern: authentication, token storage, session, CSRF, RBAC,
service-to-service auth, and credential hashing. Loads alongside whatever domain also
matched. For injection,
CORS, SSRF, XSS, secret-scanning, and the OWASP detection tables, see
[security.md](security.md). Maps to OWASP A01/A02/A04/A07/A08 and API2/API4/API5/API6
— referenced, not restated.

Each rule below carries a detection signal so review mode can flag it. P0 unless
tagged `P1 (design)`.

## OAuth & Token Flows

- **PKCE on every OAuth2 authorization-code flow; never implicit or password grant.**
  Signal: `response_type=token`, an implicit-flow config, or `grant_type=password`.
- **Access tokens are short-lived and carry `exp`; no long-lived JWT without a
  revocation path.** (OWASP A07 / API2)
  Signal: a JWT signed with no `exp`, or a `maxAge` measured in days.
- **Verify the JWT signature with a pinned algorithm and the expected key; never trust
  `decode` output for authorization, and reject `alg:none`. Validate `aud` and `iss`.**
  (OWASP A08 / API2)
  Signal: `jwt.decode(` feeding an authz decision, `verify` with no `algorithms`
  allowlist, or no `audience`/`issuer` check.
- **Every authorization-code flow sends a `state` value verified on callback and
  validates `redirect_uri` against an exact-match allowlist.** (OWASP A01 / API2)
  Signal: an OAuth callback with no `state` comparison, or a `redirect_uri`/return URL
  taken from the request without an allowlist.
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

## Brute-Force & Abuse Protection

- **Rate-limit and back off repeated auth failures — login, token, OTP, and
  password-reset endpoints; lock or throttle after a threshold.** (OWASP A04 / API4)
  Signal: a login/verify/reset handler with no rate-limit middleware, attempt counter,
  or backoff.

## Authorization (RBAC)

- **RBAC is deny-by-default and additive — start from zero, grant up.**
  (OWASP A01 / API5)
  Signal: a default-allow guard, or a route with no guard.
- **P1 (design):** support MFA and require step-up re-authentication for sensitive
  actions — password/email change, payment, privilege grant. P1 because presence is
  rarely confirmable from a single diff.

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
  (OWASP A02)
  Signal: `md5(` or `sha1(` applied to a password field.
- **Never log tokens, passwords, or session IDs.**
  Signal: a logger call whose arguments include a token, password, or session
  field. See the PII-in-logs scan in [security.md](security.md) — referenced, not
  duplicated.
- **Password-reset and recovery tokens are single-use, high-entropy, and short-expiry;
  invalidate active sessions on a completed reset.** (OWASP API6)
  Signal: a reset token with no expiry or `used` flag, or a reset path that leaves
  existing sessions valid.
- **Auth responses must not reveal whether an account exists — uniform message, status,
  and timing across login, registration, and reset.**
  Signal: distinct "user not found" vs "wrong password" branches on a login or reset
  path.
- **Compare secrets, tokens, and hashes in constant time.**
  Signal: `==`/`===` on a token, signature, or reset code instead of
  `crypto.timingSafeEqual` / a constant-time compare.
- **P1 (design):** enforce a password policy on input — a length floor per NIST 800-63B
  and a breached-password (k-anonymity) check. P1 because it spans registration, reset,
  and change flows. Complements the hashing rule above.

## Secure Patterns

### Token Storage

```typescript
// httpOnly + Secure + SameSite — not readable by JS, sent only over TLS
res.cookie('session', token, { httpOnly: true, secure: true, sameSite: 'strict' });
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
auth with no CSRF defense · JWT without `exp` · unverified / `alg:none` JWT · missing
OAuth `state` or open `redirect_uri` · default-allow authorization · MD5/SHA1 password
hashing · no rate limiting on login · account enumeration via distinct errors ·
non-constant-time secret comparison · replayable or long-lived password-reset tokens ·
static API keys shared across services · trusting network reachability instead of caller
identity · no session rotation on login or logout · logging credentials.
