---
description: Certificate and public key pinning — when to pin, what to pin, and operational requirements
alwaysApply: false
---

# Certificate and Public Key Pinning

Pinning associates a host with an expected certificate or public key to detect MITM via rogue CAs.

## NEVER
- Pin without backup pins — causes app outage on certificate rotation
- Allow users to bypass pin validation failures
- Implement custom TLS or pinning logic from scratch — use platform/library solutions
- Pin root CAs (trusts every intermediate CA that root issued)
- Add corporate interception proxy keys to pinsets without explicit risk acceptance approval
- Use Trust On First Use (TOFU) — pins must be preloaded at build time

## ALWAYS
- Preload pins at development time (out-of-band) to prevent attacker tainting
- Include backup pins (intermediate CA or alternate cert) alongside leaf pins
- Plan and test pin rotation before certificate expiry
- Log pin failures client-side; terminate the connection on mismatch — never proceed
- Use platform-native solutions or well-established libraries (OkHttp, TrustKit, etc.)
- Coordinate certificate rotation schedule with backend teams
- Perform explicit risk acceptance before adding any interception proxy to pinset

## When to Pin

| Criterion | Required for pinning |
|-----------|---------------------|
| Control both client and server | Yes |
| Can update pinset without app redeployment | Yes |
| Certificate key pairs predictable before service | Yes |
| Threat model requires CA-compromise protection | Yes |

If any criterion is not met, rely on standard certificate validation instead.

## What to Pin

| Type | Pros | Cons |
|------|------|------|
| `subjectPublicKeyInfo` (recommended) | Survives cert renewal with same key; includes key params | Slightly more complex |
| Whole certificate | Simple | Breaks on every renewal |
| Hash | Fixed-length, convenient | No contextual info |

## Platform Guidance

| Platform | Approach |
|----------|----------|
| Android | Network Security Configuration `<pin-set>`; or OkHTTP |
| iOS | `Info.plist` ATS settings; TrustKit library |
| .NET | `ServicePointManager` certificate validation callback |
| OpenSSL | `verify_callback`; check `SSL_get_verify_result == X509_V_OK` AND `SSL_get_peer_certificate != NULL` |
| Electron | `electron-ssl-pinning` or `ses.setCertificateVerifyProc` |

## Checklist
- [ ] Decision to pin documented and justified against the four criteria
- [ ] Backup pins (intermediate CA or alt cert) included
- [ ] Pins preloaded at build time, not TOFU
- [ ] Pin rotation procedure tested end-to-end before deployment
- [ ] Pin failures terminate connection; no user bypass allowed
- [ ] Platform library used — no custom TLS implementation
- [ ] Any corporate proxy addition has explicit risk acceptance on record
