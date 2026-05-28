---
description: Protect user privacy through strong cryptography, HTTPS enforcement, and minimal data exposure
alwaysApply: false
---

# User Privacy Protection

## NEVER
- Use weak or outdated cryptographic algorithms for data in transit or at rest
- Expose account existence via distinct error messages (e.g., "incorrect password" vs. "user not found")
- Store passwords without a memory-hard hash function and unique per-user salt
- Use client-side session storage for session state

## ALWAYS
- Use strong, up-to-date cryptographic algorithms for all data in transit and at rest
- Hash passwords with Argon2 or bcrypt using unique salts per user
- Enforce HTTPS exclusively; implement HTTP Strict Transport Security (HSTS)
- Implement certificate pinning to prevent MITM attacks even if a CA is compromised
- Return `"Invalid username or password"` for all auth failures to prevent account enumeration
- Store sessions server-side with cryptographically random IDs
- Minimize IP address leakage by blocking third-party external content loading where feasible
- Implement privacy-focused audit trails and access logging
- Inform users transparently about privacy limitations and data handling policies

## Checklist
- [ ] Strong, current cryptographic algorithms used for data in transit and at rest
- [ ] Passwords hashed with Argon2 or bcrypt; unique salt per user
- [ ] HTTPS enforced site-wide with HSTS header
- [ ] Certificate pinning implemented to guard against compromised CAs
- [ ] Auth failures return a single generic message — no account enumeration
- [ ] Sessions stored server-side with cryptographically random IDs
- [ ] Third-party content loading minimized to reduce IP leakage
