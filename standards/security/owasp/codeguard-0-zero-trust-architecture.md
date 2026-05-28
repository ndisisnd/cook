---
description: Implement Zero Trust Architecture — never trust implicitly, verify identity and device on every request
alwaysApply: false
---

# Zero Trust Architecture

"Never trust, always verify." Assume threats exist inside and outside the network; grant no implicit trust based on network location or asset ownership.

## NEVER
- Grant access based on network location alone
- Issue long-lived tokens without a revocation mechanism
- Allow any service-to-service or client-to-service call without authentication and authorization
- Skip device compliance checks in authorization decisions
- Permit lateral movement by leaving internal segments open by default

## ALWAYS
- Use strong authentication (FIDO2/WebAuthn) for all identities
- Enforce least-privilege access; scope tokens to minimum required permissions
- Verify identity, device health, and risk score on every access request
- Issue short-lived tokens (≤15 min); store metadata for revocation
- Use TLS 1.3 for all service communications
- Apply microsegmentation — default-deny between network/application segments
- Log every access attempt with user, resource, device, IP, risk score, and outcome
- Rate-limit all API endpoints

## Authentication & Authorization

Context-aware authorization must check all of:
1. Identity verified
2. Device compliant
3. Risk score within threshold
4. Permission granted for the specific resource + action

Short-lived token payload must include: `sub`, `device_id`, `permissions`, `exp` (≤15 min), `iat`, `jti` (unique ID for revocation).

## API Security

| Control | Requirement |
|---------|-------------|
| Transport | TLS 1.3 only |
| Auth header | Bearer token; reject missing or revoked tokens with 401 |
| Payload size | Cap (e.g., 100 KB); validate schema on every request |
| Rate limiting | Per-IP window (e.g., 100 req / 15 min) |
| Security headers | Set via `helmet` or equivalent |

## Network Microsegmentation

- Default-deny ingress and egress between segments
- Allow only explicit, named pod/service selectors (e.g., Kubernetes NetworkPolicy)
- Restrict egress to only required destinations (databases, telemetry)
- Review and audit policies on every infrastructure change

## Monitoring & Logging

Log every security event with: `EventType`, `Timestamp`, `UserId`, `ResourceId`, `IpAddress`, `DeviceId`, `DeviceHealth`, `Location`, `RequestedPermissions`, `RiskScore`. Alert on denied access patterns and anomalies.

## Checklist
- [ ] All requests require authentication; no implicit trust from network location
- [ ] Authorization checks identity, device compliance, risk score, and permission
- [ ] Tokens short-lived (≤15 min) with revocation support
- [ ] TLS 1.3 enforced on all internal and external communications
- [ ] Microsegmentation in place; default-deny between segments
- [ ] All access attempts logged with full context (user, device, resource, risk)
- [ ] API rate limiting and payload size caps enforced
