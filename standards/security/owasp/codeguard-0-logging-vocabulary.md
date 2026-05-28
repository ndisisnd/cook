---
description: Standardized security event logging vocabulary — event names, severity levels, and required fields
alwaysApply: false
---

# Security Event Logging Vocabulary

## NEVER
- Log passwords, session tokens, access tokens, API keys, encryption keys, or private keys
- Log PII, bank/payment card data, database connection strings, or commercially-sensitive data
- Log source code or secret/certificate material

## ALWAYS
- Use ISO 8601 format with UTC offset for all timestamps (`2021-01-01T01:01:01-0700`)
- Include `appid`, `event`, `level`, `source_ip`, and `datetime` in every security event
- Apply consistent severity levels: INFO, WARN, CRITICAL
- Log all authentication, authorization, session, and privileged-user events
- Consider data privacy regulations when including user information

## Event Vocabulary

**Authentication [AUTHN]**

| Event | Level |
|---|---|
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

**Authorization [AUTHZ]** · `authz_fail[:userid,resource]` CRITICAL · `authz_change[:userid,from,to]` WARN · `authz_admin[:userid,event]` WARN

**Session [SESSION]** · `session_created` INFO · `session_renewed` INFO · `session_expired[:userid,reason]` INFO · `session_use_after_expire[:userid]` CRITICAL

**Malicious [MALICIOUS]** · `malicious_excess_404` WARN · `malicious_extraneous` CRITICAL · `malicious_attack_tool` CRITICAL · `malicious_cors` CRITICAL · `malicious_direct_reference` CRITICAL

**Other categories** · `crypt_decrypt_fail` / `crypt_encrypt_fail` WARN · `excess_rate_limit_exceeded` WARN · `upload_complete` / `upload_stored` / `upload_delete` INFO · `upload_validation` INFO|CRITICAL · `input_validation_fail` WARN · `privilege_permissions_changed` WARN · `sensitive_create/read/update/delete` WARN · `sequence_fail[:userid]` CRITICAL · `sys_startup/shutdown/restart/crash` WARN · `sys_monitor_disabled/enabled` WARN · `user_created/updated/archived/deleted` WARN

## Checklist
- [ ] All timestamps in ISO 8601 with UTC offset
- [ ] Every event includes `appid`, `event`, `level`, `source_ip`, `datetime`
- [ ] Authentication and authorization events logged at correct severity
- [ ] CRITICAL events (token reuse, authz fail, impossible travel) generate alerts
- [ ] No secrets, tokens, PII, or payment data in log output
- [ ] Structured format (JSON) used; context fields (hostname, region) appended
