---
description: Multifactor authentication implementation — factor selection, trigger points, recovery, and controls
alwaysApply: false
---

# Multifactor Authentication

True MFA requires at least two factors from **different** categories — two instances of the same factor (password + PIN) does not qualify.

## NEVER
- Accept SMS or email-only as MFA for applications handling PII or financial data
- Use security questions as an MFA factor (no longer acceptable per NIST SP 800-63)
- Allow MFA bypass via recovery flows that skip identity verification
- Skip MFA enforcement at privileged-action or admin-session elevation endpoints
- Use "remember this device" on highly sensitive applications

## ALWAYS
- Require MFA at: login, password changes, email address changes, MFA disable, admin session elevation, all API and mobile auth flows
- Rate-limit authentication attempts; lock accounts after repeated MFA failures
- Verify MFA state in every authenticated endpoint
- Log and monitor all MFA-related events
- Notify users of failed MFA attempts (time, location, device) on next successful login
- Provide single-use recovery codes at MFA enrollment; require users to set up multiple MFA types

## Factor Tiers

| Tier | Methods |
|---|---|
| Recommended | Passkeys/FIDO2, hardware U2F tokens, hardware OTP tokens, digital certificates |
| Acceptable with caution | Software TOTP, smart cards (with PIN + PKI) |
| Avoid for sensitive apps | SMS, phone call (SIM-swap risk), email OTP, security questions |

## Factor Categories
1. Something You Know — passwords, PINs
2. Something You Have — hardware tokens, software OTP, U2F, certificates, smart cards
3. Something You Are — biometrics (fingerprint, face, iris)
4. Somewhere You Are — source IP, geolocation, geofencing
5. Something You Do — behavioral/keystroke dynamics

## Risk-Based Authentication
Increase MFA friction on: new device, unusual location, off-hours access, known-compromised credentials, anomalous IP reputation. Use geolocation, device fingerprinting, and behavioral signals as inputs.

## Recovery
- Single-use recovery codes issued at enrollment
- Multiple MFA types required per account
- Physical mail of recovery codes as fallback
- Rigorous identity verification through support team for account recovery
- Trusted-user vouching for corporate environments

## Checklist
- [ ] MFA required at login, password/email change, MFA disable, and admin elevation
- [ ] SMS/email OTP not used alone for PII or financial data
- [ ] Security questions absent from all MFA flows
- [ ] Rate limiting and account lockout on repeated MFA failures
- [ ] Recovery codes issued at enrollment; identity verified before reset
- [ ] Failed MFA attempts logged and user notified on next login
- [ ] MFA state verified server-side on every authenticated endpoint
