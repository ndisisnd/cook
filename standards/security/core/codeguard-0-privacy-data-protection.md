---
description: Privacy and data protection — encryption, anonymity, transparency, anti-enumeration
alwaysApply: false
---

# Privacy & Data Protection

## NEVER
- Use weak/outdated cryptographic primitives for data at rest or in transit (see `codeguard-1-crypto-algorithms`)
- Reveal whether an account exists ("user not found" vs "invalid password") — use one generic message
- Store passwords as plaintext, MD5, SHA-1, or any unsalted/fast hash
- Embed third-party content that leaks user IP to external trackers without disclosure

## ALWAYS
- Enforce HTTPS site-wide with HSTS; redirect HTTP → HTTPS
- Hash passwords with Argon2id (or scrypt/bcrypt as documented in `codeguard-0-authentication-mfa`) using a per-user salt
- Store sessions server-side with CSPRNG-generated identifiers; never embed PII or privileges in the cookie value
- Use certificate pinning for controlled clients (mobile) where both ends are owned — never browser HPKP
- Return uniform "Invalid username or password" for failed authentication regardless of cause

## Transparency & rights
- Publish privacy notices covering data handled, retention, third parties, and user rights
- Provide privacy-focused audit trails and access logging (see `codeguard-0-logging`)
- Honor data-subject access, correction, and deletion requests per applicable regulation (GDPR, CCPA, etc.)
- Minimize IP-address leakage by blocking unnecessary third-party external content loading

## Checklist
- [ ] HTTPS+HSTS site-wide; no mixed content
- [ ] Generic auth error messages; no enumeration oracle
- [ ] Passwords hashed with Argon2id/scrypt/bcrypt + per-user salt
- [ ] Server-side sessions with CSPRNG IDs; no PII in cookies
- [ ] Privacy notice published; deletion/access workflows in place
- [ ] Pinning used only where justified, with backup pins and update plan
