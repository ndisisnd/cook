---
description: Secure password reset — prevent enumeration, token abuse, and unauthorized access
alwaysApply: false
---

# Forgot Password Security

## NEVER
- Return different responses for existing vs non-existent accounts (user enumeration)
- Generate reset tokens with non-cryptographic random sources
- Store reset tokens in plaintext — hash them (same standard as passwords)
- Allow tokens to be reused after successful reset
- Automatically log users in after password reset
- Lock accounts in response to password reset requests
- Log tokens, passwords, or PII in application logs
- Build reset URLs from user-supplied `Host` headers

## ALWAYS
- Return identical messages and response times for existing and non-existent accounts (use async dispatch or identical code paths)
- Generate tokens with a cryptographically secure RNG; minimum 32 bytes of entropy
- Link tokens to a specific user with a server-stored expiry; invalidate on use
- Invalidate all existing sessions after a successful password reset
- Enforce the application's password policy during reset
- Require the new password to be entered twice
- Send reset confirmation emails without including the actual password
- Use hardcoded or allowlist-validated domains for reset URLs; enforce HTTPS; add `Referrer-Policy: no-referrer`
- Rate-limit reset requests per account and per IP
- Apply CSRF tokens to reset forms and endpoints
- Use security questions only as an additional layer, never sole mechanism; validate answers with secure comparison
- Log reset attempts with IP, user agent, and timestamp — never log tokens

## PIN vs URL Token

| Mechanism | Requirements |
|-----------|-------------|
| URL token | ≥32 bytes entropy; HTTPS; no-referrer policy; short expiry |
| PIN | 6–12 digits; CSPRNG; single-use; limited session for reset only; spaces for readability |

## Checklist
- [ ] Identical response messages and timing for all accounts
- [ ] Tokens generated with CSPRNG; ≥32 bytes; stored hashed; single-use
- [ ] All sessions invalidated after successful reset
- [ ] Rate limiting per account and IP; CSRF protection on forms
- [ ] Reset URL uses trusted/hardcoded domain over HTTPS with `no-referrer`
- [ ] No automatic login post-reset; password policy enforced
- [ ] No tokens or passwords in logs
