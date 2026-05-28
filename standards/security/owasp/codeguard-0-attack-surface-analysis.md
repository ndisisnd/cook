---
description: Attack surface analysis — catalog, reduce, and monitor all application entry/exit points
alwaysApply: false
---

# Attack Surface Analysis

## NEVER
- Leave undocumented or deprecated endpoints active without explicit security controls
- Allow unlimited request rates to authentication or critical API endpoints
- Add third-party dependencies without auditing their transitive attack surface
- Skip security review when new endpoints or integrations are introduced
- Trust data formats (JSON, XML, serialized objects) without schema validation

## ALWAYS
- Catalog all entry/exit points: UIs, REST/GraphQL APIs, file uploads, DB connections, message queues, webhooks
- Document data flows — what enters, how it's processed, how it exits, and what formats are used
- Run automated endpoint discovery and OpenAPI spec validation in CI to flag new or changed surfaces
- Classify each entry point by exposure (public vs. internal) and data sensitivity
- Enforce auth (OAuth2/JWT), input validation, and rate limiting on every API endpoint
- Apply principle of least privilege — remove or disable any feature, endpoint, or dependency not actively needed
- Regularly audit third-party libraries; remove unused dependencies
- Deploy WAF rules targeting common attack patterns (SQLi, XSS) plus application-specific vectors
- Implement rate limiting per endpoint and DDoS protection at the infrastructure level
- Monitor for anomalous traffic patterns, failed auth attempts, and unexpected data access; alert on deviations
- Use network segmentation (firewalls, IaC-enforced rules) to restrict inter-component communication
- Conduct threat modelling as part of design — identify attack vectors before code is written

## Surface inventory
| Component | Document |
|---|---|
| Entry points | All URLs, API paths, upload endpoints, queue consumers |
| Auth/Authz | Which roles access which resources; deprecated endpoint status |
| Data formats | JSON/XML schemas, serialized object types |
| Dependencies | Third-party libs, external credentials/permissions |
| IaC rules | Firewall / network segmentation config files |

## Checklist
- [ ] All entry/exit points catalogued and owners assigned
- [ ] CI/CD flags new endpoints for security review
- [ ] Rate limiting and auth enforced on every public endpoint
- [ ] Unused endpoints, features, and dependencies removed
- [ ] WAF and anomaly detection active; alerts configured
- [ ] Threat model updated with each significant architecture change
- [ ] Security logs reviewed regularly; attack surface reassessed quarterly
