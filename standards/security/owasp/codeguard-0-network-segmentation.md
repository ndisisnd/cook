---
description: Network segmentation — three-tier zone architecture and firewall policy to limit lateral movement
alwaysApply: false
---

# Network Segmentation

## NEVER
- Allow direct frontend-to-backend communication (bypass middleware)
- Allow cross-system communication between different applications at the same layer
- Allow middleware to access backend segments of foreign services
- Permit broad network rules instead of explicit allow-only firewall policies
- Allow log storage on the same system as the application

## ALWAYS
- Enforce three distinct layers: Frontend, Middleware, Backend
- Restrict external traffic to frontend only; frontend communicates only with middleware
- Define explicit allow-rules in firewall policy — deny all else
- Maintain written policy with network diagrams accessible to admins, security, auditors, developers
- Ship logs to a separate syslog server (append-only — prevents modification)
- Define network access rules for CI/CD, monitoring, and alerting systems

## Three-Layer Architecture

| Layer | Contents | Accepts traffic from |
|-------|----------|----------------------|
| Frontend | Load balancers, WAF, web servers, caches | Internet (inbound DMZ) |
| Middleware | App logic, auth services, queues, analytics | Frontend only |
| Backend | Databases, LDAP/DCs, key stores, file servers | Middleware only |

- Frontend DMZ-Inbound: internet-accessible services protected by WAF
- Frontend DMZ-Outbound: services needing outbound internet access only (no inbound)

## Multi-App / Shared Network
- Deploy a load balancer per segment; open only one port per segment to that LB
- Route traffic at application layer (OSI L7) when dedicated segments per app are not feasible

## Checklist
- [ ] Three-tier zones enforced with firewall rules
- [ ] No direct frontend-backend paths exist
- [ ] Firewall allows explicit ports/hosts only, no broad rules
- [ ] Inter-application lateral paths blocked at network layer
- [ ] Logs forwarded to isolated syslog server
- [ ] Network diagram in security policy and kept current
