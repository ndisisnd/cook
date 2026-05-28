---
description: Automate authorization tests driven by a formal matrix to catch access-control regressions
alwaysApply: false
---

# Authorization Testing Automation

## NEVER
- Test authorization manually only — automated matrix-driven tests are required
- Store the authorization matrix without encryption at rest and restricted write access
- Use production tokens or production environments for authorization tests
- Leave the authorization matrix stale after access-control changes

## ALWAYS
- Define a formal authorization matrix (XML or YAML) listing every endpoint, role, data filter, expected HTTP status, and optional test payload
- Store the matrix encrypted at rest; version-control it with write access restricted to authorized personnel
- Automate integration tests that load the matrix, generate role-based tokens (e.g., JWT), and call each endpoint as each role
- Validate actual HTTP responses against expected allowed/denied codes; report discrepancies with role, endpoint, and unexpected status
- Handle full token lifecycle in tests: refresh, expiration, and revocation scenarios
- Use environment-specific matrix configs and token settings for dev, test, and production
- Isolate test environments; use dedicated test accounts that cannot reach production resources
- Centralize token creation, service calls, and response validation logic; keep role POVs isolated for clear failure attribution
- Update the matrix as a living document alongside every authorization change
- Provide an auditable view of the matrix (e.g., HTML via XSLT) for developer and auditor review

## Matrix structure
| Field | Purpose |
|---|---|
| Feature/endpoint | Scope of the permission check |
| Logical roles | All roles that may or may not access it |
| Data filters | Row/column-level restrictions per role |
| Expected HTTP status | Allowed (2xx) and denied (403/404) per role |
| Test payload | Optional request body for richer coverage |

## Checklist
- [ ] Formal authorization matrix exists for all endpoints and roles
- [ ] Matrix encrypted at rest; write access restricted; version-controlled
- [ ] Automated tests load matrix and exercise each role/endpoint pair
- [ ] Token lifecycle (refresh, expiry, revocation) covered in tests
- [ ] Environment-specific configs used; test tokens cannot reach production
- [ ] Matrix updated with every authorization change
- [ ] Auditable matrix view available for reviewer inspection
