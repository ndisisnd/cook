---
description: Defend authentication endpoints against credential stuffing, password spraying, and brute force
alwaysApply: false
---

# Credential Stuffing Prevention

## NEVER
- Expose authentication endpoints without rate limiting
- Accept passwords found in known breach databases
- Use email addresses as the sole username form (predictable, enumerable)
- Skip MFA for administrative functions and sensitive operations

## ALWAYS
- Implement MFA — it blocks ~99.9% of credential-based attacks
- Trigger risk-based MFA on: new device/location, proxy/VPN IP, recent failed attempts, high-risk actions
- Rate-limit login per-IP (3–15 attempts by reputation), per-user (5 attempts), and globally
- Apply CAPTCHA after ≥3 failed attempts, proxy/VPN IPs, bot UAs, or high-velocity traffic
- Check new passwords against breach databases (HaveIBeenPwned API) and reject matches
- Notify users of successful logins from new devices; provide session management dashboards

## Attack Types

| Attack | Description |
|--------|-------------|
| Brute Force | Multiple passwords tested against one account |
| Credential Stuffing | Username/password pairs from external breaches |
| Password Spraying | One weak password tested across many accounts |

## Layered Controls

- **Device fingerprinting:** track UA, language, screen resolution, TLS fingerprints to detect anomalous patterns
- **Multi-step login:** require JavaScript token or CSRF token generation to raise the bar for automation
- **Unpredictable usernames:** use generated, non-sequential identifiers instead of email addresses
- **Temporary blocks:** implement automatic expiration on rate-limit lockouts

## Monitoring and Alerting
- Alert on: >100 failed logins/min, >50 unique attacking IPs/min, CAPTCHA solve rate >95%
- Detect impossible travel: logins from locations unreachable within elapsed time
- Integrate with HaveIBeenPwned to detect newly compromised credentials in use

## Checklist
- [ ] MFA enabled and required for admin/sensitive operations
- [ ] Per-IP, per-user, and global rate limits configured
- [ ] CAPTCHA triggered on threshold failures and suspicious signals
- [ ] New passwords checked against breach database; compromised passwords rejected
- [ ] New-device login notification sent to user
- [ ] Impossible travel detection alerting active
- [ ] Distributed attack monitoring (hosting-provider IPs, CAPTCHA solve rate) in place
