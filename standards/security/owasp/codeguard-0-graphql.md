---
description: Secure GraphQL API development — prevent injection, DoS, IDOR, and information leakage
alwaysApply: false
---

# GraphQL Security

## NEVER
- Accept unbounded query depth or complexity without limits
- Enable GraphQL introspection or GraphiQL in production
- Expose stack traces or debug info in error responses
- Allow batching for sensitive operations (credentials, tokens, OTPs)
- Use string concatenation to build queries in resolvers
- Return unauthorized objects based on guessed/enumerated IDs
- Rely on client-supplied pagination values without server-side caps

## ALWAYS
- Validate all inputs using specific GraphQL scalars, enums, or custom validators
- Apply parameterized queries / safe ORM APIs in every resolver
- Enforce object-level and field-level authorization on every query and mutation
- Require authentication for all endpoints unless explicitly public
- Apply CSRF protection for mutations using cookie-based auth
- Rate-limit per IP or user; limit batch query count at code level
- Use server-side batching/caching (e.g., DataLoader) to avoid N+1 abuse
- Mask errors — never reveal internal API details on invalid input

## DoS Controls

| Control | Library (JS) | Library (Java) |
| ------- | ------------ | -------------- |
| Depth limit | `graphql-depth-limit` | `MaxQueryDepthInstrumentation` |
| Complexity limit | `graphql-cost-analysis` | `MaxQueryComplexityInstrumentation` |
| Amount limit | `graphql-input-number` | custom |
| Pagination cap | server-side max | server-side max |
| Query timeout | custom instrumentation | custom instrumentation |

## Access Control
- Validate authorization on both edges and nodes in the schema
- Use Interfaces/Unions to return permission-scoped object shapes
- Add RBAC middleware in Query and Mutation resolvers
- Audit `node`/`nodes` fields — they allow direct object access by ID

## Secure Configuration
- Disable introspection: `NoIntrospectionGraphqlFieldVisibility` (Java) or `NoIntrospection` validation rule (JS)
- Disable field suggestion hints alongside introspection
- Set `NODE_ENV=production` or `debug: false` in Apollo Server
- `graphiql: process.env.NODE_ENV === 'development'` — never `true` in prod

## Checklist
- [ ] Query depth and complexity limits configured
- [ ] Introspection and GraphiQL disabled in production
- [ ] All resolvers enforce object-level and field-level auth
- [ ] Batching disabled or capped for sensitive objects
- [ ] Rate limiting applied per IP/user
- [ ] Errors masked — no internal details in responses
- [ ] CSRF protection active for cookie-based mutation flows
