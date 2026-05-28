---
description: No hardcoded credentials — secrets must never appear in source code
alwaysApply: true
---

# No Hardcoded Credentials

Treat the codebase as public — any credential in source is compromised.

## NEVER
- Passwords (database, user, admin, service account)
- API keys, secret keys, access tokens, refresh tokens, webhook secrets
- OAuth client secrets, signing keys, encryption keys
- Private keys / certificates (any `-----BEGIN ... PRIVATE KEY-----` block)
- Connection strings containing credentials (`mongodb://user:pass@host`, JDBC URLs with passwords, etc.)

## ALWAYS
- Load secrets from a secret manager (KMS, Vault, AWS Secrets Manager, etc.) or environment variables sourced from one
- Validate required secrets at boot — fail fast if missing
- Use `.env*` only for local dev, gitignored; commit `.env.example` with placeholders
- Rotate any secret that has ever touched the repo, even after deletion (git history retains it)
- Enable secret-scanning (gitleaks/trufflehog) in CI

## Recognition patterns — flag on sight

| Provider | Format |
| -------- | ------ |
| AWS | `AKIA…`, `AGPA…`, `AIDA…`, `AROA…`, `AIPA…`, `ANPA…`, `ANVA…`, `ASIA…` |
| Stripe | `sk_live_…`, `pk_live_…`, `sk_test_…`, `pk_test_…` |
| Google API | `AIza` + 35 chars |
| GitHub | `ghp_…`, `gho_…`, `ghu_…`, `ghs_…`, `ghr_…` |
| JWT | `eyJ…` + two more base64 segments |
| Private key | text between `-----BEGIN` and `-----END PRIVATE KEY-----` |

Also flag: variables named `password`/`secret`/`key`/`token`/`auth` assigned a string literal; base64 blobs near auth code; any long random-looking string of unclear origin.

## Checklist
- [ ] No credential literals in source, configs, or tests
- [ ] Secrets sourced from env/secret manager, validated at startup
- [ ] `.env*` gitignored; `.env.example` committed with placeholders
- [ ] CI secret-scanning (gitleaks/trufflehog) enabled
- [ ] Any leaked secret rotated, not just deleted
