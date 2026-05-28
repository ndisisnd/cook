---
description: Security questions are weak — prefer MFA/email recovery; strict safeguards required if used
alwaysApply: false
---

# Security Questions

Security questions are not a strong authentication factor. Prefer MFA, one-time recovery codes, or email-based recovery links.

## NEVER
- Use security questions as the sole recovery mechanism for new systems
- Allow free-form user-created questions — use a curated predefined list only
- Store answers in plaintext or with weak/fast hashing
- Rotate to a different question after a failed answer — keep the same question to block answer enumeration
- Present security questions before verifying ownership of the recovery email address
- Allow unlimited answer attempts without rate limiting
- Use answers that are easily discoverable via social media or public records

## ALWAYS
- Prefer: TOTP/push MFA, hardware security keys, one-time recovery codes, or time-limited email recovery links
- If questions are required: use a curated list of memorable, stable, confidential, and specific questions
- Hash answers with Argon2id or bcrypt, unique per-answer salt, system-wide pepper; store data encrypted at rest (AES-256)
- Normalize answers before comparison: lowercase, trim spaces, strip punctuation
- Enforce minimum answer length; block weak answers ("password", "123456", username, email)
- Require multiple questions together for increased security
- Verify the recovery email address before presenting any security questions
- Rate-limit answer attempts: max 5/hour, progressive delays, CAPTCHA after 3 failures, account lockout on abuse
- Require re-authentication (password or MFA) before allowing changes to questions or answers
- Use HTTPS/TLS 1.3+ on all recovery endpoints

## Answer quality criteria
| Criterion | Requirement |
|---|---|
| Memorable | User can recall it consistently over years |
| Stable | Answer does not change over lifetime |
| Confidential | Not findable via social media or public records |
| Specific | Single precise answer, not many valid options |

## Checklist
- [ ] MFA or email recovery offered as primary alternative to security questions
- [ ] Answers hashed with Argon2id/bcrypt + per-answer salt + pepper; encrypted at rest
- [ ] Answers normalized (lowercase, trim, strip punctuation) before compare
- [ ] Weak answers blocked via denylist
- [ ] Rate limiting + CAPTCHA + lockout on recovery attempts
- [ ] Recovery email verified before security questions are shown
- [ ] Re-authentication required to change questions/answers
