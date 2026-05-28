---
description: Authentication and MFA — passwords, MFA, OAuth/OIDC, SAML, recovery, tokens
alwaysApply: false
---

# Authentication & MFA

## NEVER
- Use predictable or publicly-known user identifiers as the primary internal key
- Return different errors for "user not found" vs "wrong password" — single generic message only
- Vary response time by branch (account exists vs not) — keeps timing oracle closed
- Block paste or disable `<input type="password">` for password managers
- Encrypt passwords (use slow, memory-hard hashing) or use fast/unsalted hashes (MD5, SHA-1, SHA-256-unsalted)
- Permanently lock accounts on failed attempts — use throttling + alerts
- Accept JWTs with `alg: none`; accept tokens without `iss`/`aud`/`exp`/`nbf` validation
- Build custom auth protocols — use OAuth 2.0/OIDC/SAML
- Use OAuth Implicit flow or Resource-Owner Password Credentials (ROPC)
- Rely on SMS, voice, email codes, or security questions for high-risk accounts
- Auto-login after a password reset

## ALWAYS
- Use random, non-public internal user IDs; allow login via verified email or username
- Return a uniform error and keep timing consistent across all auth failure paths
- Enforce TLS for all auth endpoints; enable HSTS
- Apply rate limits per IP, per account, and globally; use progressive backoff (CAPTCHA only as last resort)
- Hash passwords with: Argon2id (preferred), scrypt, bcrypt, or PBKDF2 — per-user salt, constant-time compare
- Check new passwords against breach corpora (k-anonymity API); reject breached/common passwords
- Require MFA for: login, password/email changes, MFA disable, privilege elevation, high-value transactions, new device/location
- Prefer phishing-resistant MFA (passkeys/WebAuthn, FIDO2 hardware) for sensitive accounts; TOTP/smart-card with PIN acceptable
- Require re-authentication after password reset; rotate sessions; do not auto-login

## Password storage parameters (tune to your hardware; target <1s/verify)
- **Argon2id:** m=19–46 MiB, t=2–1, p=1
- **scrypt:** N=2^17, r=8, p=1
- **bcrypt** (legacy only): cost ≥10, 72-byte input limit
- **PBKDF2** (FIPS): PBKDF2-HMAC-SHA-256 ≥600k, or SHA-1 ≥1.3M
- Optional pepper stored outside DB in KMS/HSM; apply via HMAC or pre-hash; plan for user resets on rotation
- Support Unicode and null bytes end-to-end

## OAuth 2.0 / OIDC
- Authorization Code + PKCE for public/native apps
- Avoid Implicit and ROPC
- Validate `state` and `nonce`; exact redirect-URI matching; prevent open redirects
- Constrain tokens to audience/scope; sender-constrain via DPoP or mTLS where possible
- Rotate refresh tokens; revoke on logout or risk signal

## SAML
- TLS 1.2+; sign responses and assertions; encrypt sensitive assertions
- Validate `Issuer`, `InResponseTo`, `NotBefore`/`NotOnOrAfter`, `Recipient`; verify against trusted keys
- Prevent XML signature wrapping with strict schema validation and hardened XPath
- Short response lifetimes; SP-initiated flows preferred; validate `RelayState`; implement replay detection

## Tokens
- **Prefer opaque server-managed tokens** for revocation simplicity
- **JWTs (if used):** pin algorithm explicitly; reject `none`; validate `iss`/`aud`/`exp`/`iat`/`nbf`; short lifetimes + rotation; KMS/HSM-stored keys; never hardcoded
- Consider binding tokens to client context (fingerprint hash in cookie) to reduce replay
- Implement denylist/allowlist revocation on logout and critical events

## Recovery & reset
- Same response for existing and non-existing accounts; normalized timing
- CSPRNG tokens ≥32 bytes, single-use, stored as hashes, short expiry
- HTTPS reset links to pinned trusted domains; `Referrer-Policy: no-referrer` on UI
- Post-reset: require re-authentication, rotate sessions, do not auto-login
- Never lock on reset attempts — rate limit and monitor

## Risk signals & monitoring
- New device, geo-velocity, IP reputation, unusual time, breached credentials → trigger step-up
- MFA recovery: single-use backup codes; encourage multiple factors; strong identity verification for resets
- Notify users of new-device logins and MFA failures
- Log auth events with stable fields and correlation IDs; never log secrets or raw tokens
- Detect credential stuffing (high failure rate, many IPs/agents, impossible travel)

## Admin & internal accounts
- Separate admin login from public forms; stronger MFA; device-posture checks; IP allow-lists; step-up required
- Distinct session contexts and stricter timeouts

## Checklist
- [ ] Argon2id (or documented alternative) with per-user salt; constant-time verify
- [ ] Breached-password check on set/change
- [ ] WebAuthn/passkeys or hardware tokens for high-risk; TOTP fallback; backup codes
- [ ] OAuth: Authorization Code + PKCE; strict redirect URI; audience/scope enforced; refresh rotation
- [ ] SAML: signed/encrypted assertions; replay detection; hardened XPath
- [ ] Tokens: short-lived; sender-constrained where possible; revocation works
- [ ] Recovery: single-use hashed tokens; uniform responses; re-auth required after reset
- [ ] Rate limits + throttling + anomaly detection on auth endpoints
- [ ] Admin flows isolated with stricter policies
