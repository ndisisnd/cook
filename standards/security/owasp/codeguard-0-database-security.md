---
description: Secure database configuration — isolation, TLS, authentication, least privilege, and hardening
alwaysApply: false
---

# Database Security

## NEVER
- Allow direct connections from thick clients to backend databases
- Store credentials in application source code or version control
- Grant application accounts administrative or database-owner rights
- Use built-in root/sa/SYS accounts for application connections
- Share database accounts across Development, UAT, and Production environments
- Disable authentication for local connections
- Allow unencrypted database connections

## ALWAYS
- Isolate database servers; bind to localhost or restrict to specific hosts via firewall
- Disable TCP/network access where possible — use local socket files or named pipes
- Place database in a separate DMZ isolated from the application server
- Enforce encrypted connections (TLSv1.2+ with AES-GCM or ChaCha20 ciphers)
- Verify digital certificate validity in all client applications
- Require authentication for every connection including local server connections
- Apply principle of least privilege — grant only SELECT/UPDATE/DELETE as actually needed
- Use one dedicated account per application or service
- Store credentials in environment variables or a secrets manager, outside the web root
- Set restrictive file permissions on credential config files
- Remove or disable accounts when applications are decommissioned
- Rotate passwords when staff leave or compromise is suspected
- Run database service under a low-privileged OS user account
- Remove default accounts, sample databases, and unnecessary stored procedures
- Install security patches regularly
- Store transaction logs on a separate disk from main database files
- Maintain regular encrypted backups with proper access controls
- Implement database activity monitoring and alerting

## Platform-Specific Hardening

| Platform | Key Actions |
|----------|-------------|
| SQL Server | Disable `xp_cmdshell`, CLR execution, SQL Browser service, Mixed Mode Auth (unless required) |
| MySQL/MariaDB | Run `mysql_secure_installation`; disable `FILE` privilege for application users |
| PostgreSQL | Follow official PostgreSQL security documentation |
| MongoDB | Implement MongoDB security checklist |
| Redis | Follow Redis security guide |

## Permission Model
- Implement table-level, column-level, and row-level permissions where sensitive data requires it
- Avoid making accounts database owners — prevents privilege escalation
- Review all accounts and permissions regularly

## Checklist
- [ ] Database not reachable from public network; firewall restricts to allowed hosts only
- [ ] All connections use TLSv1.2+ with modern ciphers; certificates validated
- [ ] Application uses dedicated least-privilege account (no root/sa/SYS)
- [ ] Credentials stored in secrets manager or env vars — not in source code
- [ ] Credential files outside web root with restrictive permissions, not in VCS
- [ ] Separate accounts and databases for Dev/UAT/Prod
- [ ] Default accounts, sample DBs, and unnecessary features removed
- [ ] Activity monitoring and alerting configured
