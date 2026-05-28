---
description: Logging and monitoring — structured telemetry, redaction, integrity, detection and alerting
alwaysApply: false
---

# Logging & Monitoring

## NEVER
- Log credentials, raw tokens, session IDs, recovery codes, or other secrets
- Log PII without classification, retention, and deletion controls
- Accept untrusted input into log records without sanitization (CR/LF stripping) — log injection risk
- Use free-form text for security-relevant signals — they must be structured and parseable
- Allow write or delete access to log storage from the application identity

## ALWAYS
- Emit structured (JSON) logs with stable field names
- Include correlation/request ID, non-PII user/session ID, source IP, user agent, and UTC RFC3339 timestamp
- Redact or tokenize secrets and sensitive fields before write
- Use append-only or WORM storage; centralize and apply access controls + retention policies
- Synchronize clocks (NTP); transmit logs over authenticated, encrypted channels

## What to log
- Authn/authz events (success and failure), admin actions, config changes
- Sensitive-data access, input-validation failures, security errors
- Privilege changes, MFA enrollment/verification, password/account recovery flows

## Detection & alerting
- Alerts for: credential-stuffing patterns, impossible travel, excessive auth failures, privilege escalation, SSRF indicators, data-exfiltration patterns
- Tune thresholds with runbooks; ensure on-call coverage; test alert flows end-to-end

## Privacy & compliance
- Maintain data inventory and classification; minimize personal data in logs
- Provide a mechanism to locate and delete user-linked log data when policy requires

## Checklist
- [ ] JSON logging with stable fields; log injection sanitized
- [ ] Redaction filters cover credentials, tokens, PII
- [ ] Correlation IDs on every request
- [ ] Isolated, tamper-evident storage; retention configured
- [ ] Security alerts defined, tuned, and tested
- [ ] Periodic audits for secret/PII leakage
