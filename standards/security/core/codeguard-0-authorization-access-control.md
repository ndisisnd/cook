---
description: Authorization and access control — deny-by-default, RBAC/ABAC/ReBAC, IDOR, mass assignment, step-up
alwaysApply: false
---

# Authorization & Access Control

## NEVER
- Trust client-supplied identifiers (object IDs, role claims, tenant IDs) without server-side verification
- Bind request bodies directly to domain objects containing sensitive fields (mass assignment)
- Use `exclude` or "all fields" patterns in serializers — explicit allow-list only
- Rely on obscurity (UUIDs alone) for access control
- Leak resource existence via differing 403 vs 404 responses
- Allow client-side downgrade of the chosen authorization method (e.g., MFA bypass)

## ALWAYS
- Deny by default — return 403 unless an explicit allow rule matches
- Apply least privilege; audit permissions regularly
- Check authorization on every request, regardless of source (HTML form, AJAX, API)
- Enforce centrally via middleware/policies/filters at service boundaries
- Prefer ABAC or ReBAC for fine-grained decisions; use RBAC only for coarse role checks
- Scope data queries to the requesting principal (e.g., `currentUser.projects.find(id)`)
- Use DTOs with explicit allow-listed fields for create/update operations
- Log all denials with actor, action, resource ID (non-PII), and rationale code

## IDOR prevention
- Resolve resources via user-scoped queries or server-side lookups — never raw `Model.find(client_id)`
- Use non-enumerable identifiers (UUIDs/random) as defense-in-depth, not as the primary control

## Step-up / transaction authorization
- Require a second factor for sensitive actions (wire transfers, privilege elevation, data export)
- Apply WYSIWYS: display critical fields for explicit confirmation before signing
- Use unique, time-limited authorization credentials per transaction; reject if data changes mid-flow
- Enforce method selection server-side; throttle failures; restart the whole flow on failure (no partial replay)

## Testing
- Maintain an authorization matrix (YAML/JSON) listing endpoint × role/attribute × expected outcome
- Automated tests iterate the matrix, mint role tokens, and assert allow/deny — including expiry and revocation
- Negative tests: swapped IDs, downgraded roles, missing scopes, bypass attempts

## Checklist
- [ ] Middleware enforces deny-by-default on every endpoint
- [ ] Query scoping ensures users only see permitted rows/objects
- [ ] DTOs + allow-lists prevent mass assignment
- [ ] Step-up auth in place for sensitive operations with unique short-lived credentials
- [ ] Authorization matrix drives CI tests; failures block merges
- [ ] Denials logged with actor, action, resource, rationale
