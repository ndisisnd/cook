---
description: Database security — isolation, TLS, least privilege, RLS/CLS, backups, auditing
alwaysApply: false
---

# Database Security

## NEVER
- Allow database servers to accept direct connections from end-user clients (thick or thin)
- Bind to `0.0.0.0` when localhost or a private interface will do
- Allow unencrypted database connections in production
- Use built-in `root`/`sa`/`SYS`/`postgres` accounts for application access
- Grant administrative rights to application accounts (database owner, GRANT ALL, etc.)
- Store credentials in application source, repository, or unencrypted config in webroot
- Share a single database account across applications or environments
- Leave default accounts, sample databases, or test data enabled in production

## ALWAYS
- Isolate the database in a separate network segment / DMZ; restrict ports to specific hosts via firewall
- Disable TCP and use local sockets / named pipes where supported
- Require TLS 1.2+ with modern ciphers (AES-GCM, ChaCha20-Poly1305) and a trusted certificate; clients verify certs
- Require authentication for all connections, including local
- Use a dedicated, least-privilege account per app/service
- Grant only the operations needed (SELECT/INSERT/UPDATE/DELETE as required); restrict by host where supported
- Use separate accounts and databases across Dev / UAT / Prod
- Source credentials from a secrets manager or env vars sourced from one (see `hardcoded-credentials`)
- Apply table-level, column-level, and row-level permissions where the data model warrants it
- Run the database service under a low-privilege OS account; apply security patches on schedule
- Remove default accounts, sample databases, and unused stored procedures

## Backups & operations
- Encrypted backups; restricted access; restoration tested on schedule
- Store transaction logs on a separate disk from data files
- Enable database activity monitoring and alerting for privileged operations

## Platform-specific hardening
- **SQL Server:** disable `xp_cmdshell`, CLR execution, and SQL Browser; require Windows auth unless Mixed Mode is needed
- **MySQL/MariaDB:** run `mysql_secure_installation`; revoke `FILE` privilege from app users
- **PostgreSQL:** follow the upstream security checklist; use `SCRAM-SHA-256` auth
- **MongoDB:** follow the official security checklist; bind to localhost or private network
- **Redis:** require AUTH; bind to localhost or private network; rename dangerous commands

## Checklist
- [ ] DB on private network; no direct internet exposure
- [ ] TLS required; certs verified by clients
- [ ] App accounts least-privilege; no root/sa/owner used by apps
- [ ] Credentials from secrets manager; not in source or webroot config
- [ ] Separate accounts/DBs per environment
- [ ] Default accounts and sample data removed; patches current
- [ ] Backups encrypted; restoration tested
- [ ] Activity monitoring and alerting active for privileged ops
