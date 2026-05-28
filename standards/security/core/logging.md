---
description: Logging, monitoring and security event vocabulary — structured telemetry, redaction, event names, severity levels, detection and alerting
alwaysApply: false
---

# Logging & Monitoring

## NEVER
- Log credentials, raw tokens, session IDs, recovery codes, or other secrets
- Log PII without classification, retention, and deletion controls
- Accept untrusted input into log records without sanitization (CR/LF stripping) — log injection risk
- Use free-form text for security-relevant signals — they must be structured and parseable
- Allow write or delete access to log storage from the application identity
- Log passwords, session tokens, access tokens, API keys, encryption keys, or private keys
- Log bank/payment card data, database connection strings, source code, or certificate material

## ALWAYS
- Emit structured (JSON) logs with stable field names
- Include `appid`, `event`, `level`, `source_ip`, and `datetime` (ISO 8601 with UTC offset) in every security event
- Include correlation/request ID, non-PII user/session ID, and user agent on every request
- Redact or tokenize secrets and sensitive fields before write
- Use append-only or WORM storage; centralize and apply access controls + retention policies
- Synchronize clocks (NTP); transmit logs over authenticated, encrypted channels
- Apply consistent severity levels: INFO, WARN, CRITICAL

## What to log
- Authn/authz events (success and failure), admin actions, config changes
- Sensitive-data access, input-validation failures, security errors
- Privilege changes, MFA enrollment/verification, password/account recovery flows

## Detection & alerting
- Alerts for: credential-stuffing patterns, impossible travel, excessive auth failures, privilege escalation, SSRF indicators, data-exfiltration patterns
- CRITICAL events (token reuse, authz failure, impossible travel, session use after expiry) must generate alerts
- Tune thresholds with runbooks; ensure on-call coverage; test alert flows end-to-end

## Privacy & compliance
- Maintain data inventory and classification; minimize personal data in logs
- Consider data privacy regulations when including user information
- Provide a mechanism to locate and delete user-linked log data when policy requires

## Event Vocabulary

Use consistent event names to enable SIEM correlation and alerting. Format: `category_action[:param,...]`.

**Authentication [AUTHN]**

| Event | Level |
| ----- | ----- |
| `authn_login_success[:userid]` | INFO |
| `authn_login_successafterfail[:userid,retries]` | INFO |
| `authn_login_fail[:userid]` | WARN |
| `authn_login_fail_max[:userid,maxlimit]` | WARN |
| `authn_login_lock[:userid,reason]` | WARN |
| `authn_password_change[:userid]` | INFO |
| `authn_password_change_fail[:userid]` | CRITICAL |
| `authn_impossible_travel[:userid,region1,region2]` | CRITICAL |
| `authn_token_created[:userid,entitlements]` | INFO |
| `authn_token_revoked[:userid,tokenid]` | INFO |
| `authn_token_reuse[:userid,tokenid]` | CRITICAL |
| `authn_token_delete[:appid]` | WARN |

**Authorization [AUTHZ]**
- `authz_fail[:userid,resource]` — CRITICAL
- `authz_change[:userid,from,to]` — WARN
- `authz_admin[:userid,event]` — WARN

**Session [SESSION]**
- `session_created` — INFO
- `session_renewed` — INFO
- `session_expired[:userid,reason]` — INFO
- `session_use_after_expire[:userid]` — CRITICAL

**Malicious activity [MALICIOUS]**
- `malicious_excess_404` — WARN
- `malicious_extraneous` — CRITICAL
- `malicious_attack_tool` — CRITICAL
- `malicious_cors` — CRITICAL
- `malicious_direct_reference` — CRITICAL

**Other categories**
- `crypt_decrypt_fail` / `crypt_encrypt_fail` — WARN
- `excess_rate_limit_exceeded` — WARN
- `upload_complete` / `upload_stored` / `upload_delete` — INFO
- `upload_validation` — INFO | CRITICAL
- `input_validation_fail` — WARN
- `privilege_permissions_changed` — WARN
- `sensitive_create` / `sensitive_read` / `sensitive_update` / `sensitive_delete` — WARN
- `sequence_fail[:userid]` — CRITICAL
- `sys_startup` / `sys_shutdown` / `sys_restart` / `sys_crash` — WARN
- `sys_monitor_disabled` / `sys_monitor_enabled` — WARN
- `user_created` / `user_updated` / `user_archived` / `user_deleted` — WARN

## Checklist
- [ ] JSON logging with stable fields; log injection sanitized
- [ ] Every security event includes `appid`, `event`, `level`, `source_ip`, `datetime` (ISO 8601 UTC)
- [ ] Redaction filters cover credentials, tokens, PII, payment data
- [ ] Correlation IDs on every request
- [ ] Authentication and authorization events logged at correct severity
- [ ] CRITICAL events (token reuse, authz fail, impossible travel) generate alerts
- [ ] Isolated, tamper-evident storage; retention configured
- [ ] Security alerts defined, tuned, and tested
- [ ] Periodic audits for secret/PII leakage
