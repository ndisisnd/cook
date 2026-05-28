---
description: Authentication security — passwords, MFA, sessions, recovery, and federated auth
alwaysApply: false
---

# Authentication

## NEVER
- Expose different error messages for "user not found" vs "wrong password"
- Use fast/unsalted hashes (MD5, SHA-1, SHA-256-plain) for password storage
- Skip constant-time comparison when checking password hashes
- Use public or predictable values as internal user identifiers
- Disable paste or interfere with `<input type="password">` (breaks password managers)
- Allow composition rules that restrict character sets — enforce length only
- Build custom auth or federated protocols — use OAuth 2.0/OIDC/SAML
- Expose admin/internal login forms on public interfaces

## ALWAYS
- Return generic error messages (e.g., "Invalid username or password") on all auth failures
- Hash passwords with Argon2id (preferred) or bcrypt; use a unique per-user salt
- Check new passwords against breach corpora (HaveIBeenPwned k-anonymity API); reject common/breached passwords
- Enforce minimum 8-char and maximum 64+-char password limits; allow all Unicode/whitespace
- Include a password strength meter in the UI
- Use TLS for all endpoints transmitting credentials, session tokens, or sensitive data
- Rate-limit login attempts; implement account lockout/throttling + CAPTCHA against brute force
- Require MFA (TOTP or WebAuthn) for sensitive accounts
- Issue session cookies with `HttpOnly` + `Secure` flags; rotate session ID after login; set timeouts
- Require re-authentication before password changes, email updates, or financial transactions
- Send password-reset responses identically whether the account exists or not
- Log all auth failures, successful logins, lockouts, and password changes

## Password strength parameters
- Minimum: 8 chars; maximum: 64+ to support passphrases
- Allow all characters including Unicode and whitespace
- No composition rules (no forced uppercase/number/symbol requirements)
- Block: breach corpora hits, "password", "123456", and username/email matches

## Session management
- `HttpOnly` + `Secure` flags on session cookies
- Rotate session ID immediately after login
- Enforce idle and absolute session timeouts appropriate to sensitivity

## Checklist
- [ ] Generic error messages on all auth failure paths; uniform response timing
- [ ] Argon2id or bcrypt with per-user salt; constant-time hash compare
- [ ] Breached-password check on account creation and password change
- [ ] MFA (TOTP/WebAuthn) available and enforced for sensitive operations
- [ ] Session cookies: `HttpOnly`, `Secure`, rotated on login, with timeouts
- [ ] Re-authentication required before sensitive changes
- [ ] OAuth 2.0/OIDC/SAML used for federated auth — no custom protocol
