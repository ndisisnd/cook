---
description: Prevent IDOR — enforce access control on every object lookup, avoid enumerable IDs in URLs
alwaysApply: false
---

# Insecure Direct Object Reference (IDOR) Prevention

## NEVER
- Assume that knowledge of an object ID implies authorisation to access it
- Expose numeric primary keys directly in URLs or POST bodies when avoidable
- Encrypt identifiers as a substitute for access control — encryption is not access control
- Perform direct object lookups on unrestricted datasets (e.g., `Project.find(id)` across all records)

## ALWAYS
- Check the authenticated user's permission on every object access attempt
- Scope database lookups to objects the current user is authorised to access
- Derive the acting user from session data, not from client-supplied parameters
- Pass object identifiers through the session in multi-step flows to prevent parameter tampering
- Implement access control structurally using your framework's recommended approach

## Secure Lookup Pattern

```ruby
# Vulnerable — searches all projects
@project = Project.find(params[:id])

# Secure — scoped to current user's authorised records
@project = @current_user.projects.find(params[:id])
```

## Defense-in-Depth: Complex Identifiers
- Replace enumerable numeric IDs with UUIDs or random strings in URLs as an additional layer — not a substitute for access control
- Add a random-string column to the DB table and use it in URLs instead of the primary key
- Even with complex IDs, always verify authorisation — obtained URLs must still be blocked if unauthorised

## Checklist
- [ ] Every object lookup verifies the requesting user's authorisation
- [ ] DB queries scoped to records the user owns or has access to
- [ ] Acting user identity comes from session, not request parameters
- [ ] Multi-step flows pass IDs through session, not hidden fields
- [ ] Enumerable numeric IDs replaced with UUIDs/random strings in URLs
- [ ] Access denied response returned when ID is valid but user is unauthorised
