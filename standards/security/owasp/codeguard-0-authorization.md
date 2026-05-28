---
description: Authorization — deny-by-default, least privilege, IDOR prevention, and server-side enforcement
alwaysApply: false
---

# Authorization

## NEVER
- Rely on client-side checks for access control — they are trivially bypassed
- Default to allow; always default to deny and grant explicitly
- Return data based on a user-supplied ID without verifying the requester owns/can access that object (IDOR)
- Expose detailed error messages on authorization failure — use 403 or 404 only
- Apply authorization checks inconsistently across AJAX, API, and direct request paths

## ALWAYS
- Enforce all authorization decisions server-side on every request
- Default to deny; grant access only via explicit allow rules
- Use centralized middleware/decorators to apply authorization consistently across all endpoints
- Check that the authenticated user has permission for the specific object being accessed (prevent IDOR)
- Prefer ABAC or ReBAC over flat RBAC for fine-grained permissions
- Apply least privilege — grant the minimum permissions required
- Invalidate sessions and revoke tokens immediately when permissions change or on logout
- Return generic 403 Forbidden (or 404 if resource existence is sensitive) — never leak permission details
- Log all authorization failures with user ID, resource, action, and timestamp
- Write unit and integration tests covering both allow and deny cases
- Apply authorization to static files, cloud storage, and all resource types — not just API endpoints

## Deny-by-default pattern
```javascript
function canView(req, res, next) {
  if (project.ownerId === req.user.id) return next();
  if (req.user.isAdmin) return next();
  if (project.isPublic && req.user.isVerified) return next();
  return res.status(403).json({ error: 'Access denied' }); // deny by default
}
```

## Checklist
- [ ] All authorization enforced server-side; no client-side-only checks
- [ ] Default deny; explicit grants only
- [ ] Every object access verifies the requester's permission for that specific object
- [ ] Centralized middleware applies authorization uniformly to all request types
- [ ] 403/404 returned on denial; no detail leakage
- [ ] Auth failures logged with user, resource, action, and timestamp
- [ ] Tests cover both positive (allowed) and negative (denied) paths
