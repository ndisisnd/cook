---
description: Microservices security — authorization patterns, identity propagation, service-to-service auth, and logging
alwaysApply: false
---

# Microservices Security

## NEVER
- Push all authorization decisions to the API gateway alone (single point of decision violates defense-in-depth)
- Reuse external access tokens internally — token leakage risk
- Expose internal entity representation structures outside the trusted boundary
- Hardcode access control rules in service source code
- Write log messages directly to the central logging system from within a microservice
- Log sensitive data (PII, passwords, API keys) in log messages

## ALWAYS
- Implement authorization at both edge level (coarse-grained) and service level (fine-grained)
- Use a centralized policy language/engine (PAP/PDP/PEP/PIP) with embedded PDP per service or sidecar
- After edge authentication, generate a signed/encrypted internal identity structure; propagate it — not the external token
- Use a single data structure to represent external entity identity internally; make it extensible
- Authenticate service-to-service traffic with mTLS or signed tokens
- Generate a unique correlation ID for every call chain; include it in all log messages
- Filter/sanitize log messages to exclude sensitive data before publishing
- Maintain documented service inventory, data classification, and service-to-service communication map

## Service-to-Service Authentication

| Method | Use when | Tradeoff |
|---|---|---|
| mTLS | Default; prefer for most traffic | Key provisioning overhead; strong identity + confidentiality |
| Signed token (online validation) | Critical requests needing revocation check | Higher latency |
| Signed token (offline validation) | Non-critical; low-latency paths | May not detect revoked tokens |

## Logging Architecture
- Each microservice writes to local file / stdout only
- Dedicated logging agent on same host pulls logs and publishes to message broker via mutual TLS
- Central logging service subscribes to message broker
- Message broker enforces least-privilege access control
- Publish in structured format (JSON/CSV); append hostname, container name, class/filename context

## Architecture Documentation (required)
Document for threat modeling and least-privilege enforcement:
- All services with unique IDs, business function, API definitions (scopes, auth schemes), team ownership
- All data assets with classification (PII, confidential, public) and golden-source vs cache designation
- Service-to-service communication (sync HTTP/gRPC, async messaging) with data exchanged
- Graphical service call graph or data flow diagram showing trust boundaries

## Checklist
- [ ] Authorization enforced at gateway (coarse) AND each service (fine-grained)
- [ ] External tokens never forwarded internally; signed internal identity structure used
- [ ] Service-to-service traffic authenticated via mTLS or validated signed tokens
- [ ] Access control policy expressed in policy language, not hardcoded
- [ ] Correlation IDs generated per call chain; present in all log entries
- [ ] Log pipeline: local file → agent → message broker (mTLS) → central service; no sensitive data logged
- [ ] Service inventory, data classification, and architecture diagram maintained and current
