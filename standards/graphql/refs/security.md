# GraphQL Security

> Source: [Security – graphql.org](https://graphql.org/learn/security/) · [OWASP GraphQL Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/GraphQL_Cheat_Sheet.html) · [Security & GraphQL – howtographql.com](https://www.howtographql.com/advanced/4-security/) · [Authorization – graphql.org](https://graphql.org/learn/authorization/)

## Query Depth Limiting

Deeply nested queries can cause exponential database load. Reject operations that exceed a maximum depth **before execution** ([graphql.org](https://graphql.org/learn/security/#query-depth-limiting)):

```typescript
import depthLimit from 'graphql-depth-limit';

const server = new ApolloServer({
  schema,
  validationRules: [depthLimit(7)],
});
```

- A depth limit of **5–7** covers most real-world query patterns.
- Apply a **stricter separate limit** (e.g., 3) to nested list fields — list nesting causes data to grow exponentially.
- Return a clear error when the limit is exceeded so clients can fix their queries; don't silently truncate.

---

## Query Complexity Analysis

Depth alone is insufficient — a shallow query with many expensive fields can still be harmful. Weight fields by estimated cost and reject queries that exceed a budget ([graphql.org](https://graphql.org/learn/security/#query-complexity)):

```typescript
import costAnalysis from 'graphql-cost-analysis';

const server = new ApolloServer({
  schema,
  validationRules: [
    costAnalysis({
      maximumCost: 1000,
      defaultCost: 1,
      scalarCost: 1,
      objectCost: 2,
      listFactor: 10, // multiply cost per list item
    }),
  ],
});
```

- Cost analysis runs **before execution** — expensive queries are rejected without hitting the database.
- A typical threshold is **1,000–5,000 points** depending on infrastructure capacity.
- Expose the estimated cost in the response `extensions` during development so clients can tune their queries.

---

## Rate Limiting

GraphQL-aware rate limiting must account for actual operation count and complexity — not just HTTP request count, since clients can batch multiple queries into a single HTTP request ([OWASP](https://cheatsheetseries.owasp.org/cheatsheets/GraphQL_Cheat_Sheet.html)):

- Apply limits per **user/token**, not per IP.
- Factor in complexity cost: deduct the query's estimated cost from the client's per-minute budget, not just +1 per request.
- Limit batch query arrays to a maximum count (e.g., 10 operations per batch request).

```typescript
// Pseudocode: cost-based rate limit
const estimatedCost = computeQueryCost(document);
const remaining = await rateLimiter.consume(userId, estimatedCost);
if (remaining < 0) {
  throw new GraphQLError('Rate limit exceeded', {
    extensions: { code: 'RATE_LIMITED', retryAfter: remaining.msBeforeNext },
  });
}
```

---

## Introspection

Introspection exposes the full schema to anyone who can reach the endpoint. Disable it in production for APIs that only serve known first-party clients ([graphql.org](https://graphql.org/learn/security/#introspection)):

```typescript
const server = new ApolloServer({
  schema,
  introspection: process.env.NODE_ENV !== 'production',
});
```

- Keep introspection enabled in `development` and `staging` for tooling (GraphiQL, code generation).
- If third-party developers need to integrate, provide a separate developer portal or schema registry rather than enabling introspection on the production endpoint.
- As an alternative to full disablement, restrict introspection to authenticated users with a specific role.

---

## Authorization

**Authorization belongs in the business logic layer, not in resolvers.** GraphQL resolvers are a thin execution layer; putting auth checks inside them scatters policy throughout the codebase and makes it easy to miss fields ([graphql.org](https://graphql.org/learn/authorization/)):

```typescript
// Good — resolver delegates to a model that enforces auth
const resolvers = {
  Query: {
    order: (_, { id }, { user }) => OrderModel.findForUser(id, user),
  },
  Mutation: {
    cancelOrder: (_, { input }, { user }) => OrderModel.cancelForUser(input.id, user),
  },
};

// OrderModel.ts — auth enforced here, not in the resolver
class OrderModel {
  static async findForUser(id: string, viewer: User) {
    const order = await db.orders.findById(id);
    if (!order || order.userId !== viewer.id) return null; // not found = not authorized
    return order;
  }
}
```

- Pass a fully hydrated `user` object in `context`, not a raw token.
- Return `null` for not-found resources instead of throwing a permission error — leaking the existence of a resource is itself an information disclosure ([OWASP](https://cheatsheetseries.owasp.org/cheatsheets/GraphQL_Cheat_Sheet.html)).
- For directive-based authorization (`@auth`, `@hasRole`), apply it via a schema transformer or plugin that wraps resolvers — never rely on manual `if` checks in every resolver.

```graphql
# Directive-based auth (applied via schema transformer)
type Mutation {
  deleteUser(id: ID!): DeleteUserPayload! @auth(requires: ADMIN)
  updateOwnProfile(input: UpdateProfileInput!): UpdateProfilePayload! @auth(requires: USER)
}
```

---

## Field-Level Security

- Never expose internal database IDs directly — use opaque IDs (e.g., global IDs from the `Node` interface).
- Audit the schema for fields that reveal infrastructure details: internal service names, stack traces in error messages, server paths.
- Strip stack traces from production error responses:

```typescript
const server = new ApolloServer({
  schema,
  formatError: (formattedError) => {
    // Remove stack trace in production
    if (process.env.NODE_ENV === 'production') {
      const { stacktrace, ...safeExtensions } = formattedError.extensions ?? {};
      return { ...formattedError, extensions: safeExtensions };
    }
    return formattedError;
  },
});
```

---

## Persisted Queries

Use persisted queries (trusted documents or automatic persisted queries) to prevent clients from submitting arbitrary operations in production ([graphql.org](https://graphql.org/learn/performance/)):

- The client sends a **hash** of the query; the server resolves it from a stored registry.
- Blocks ad-hoc introspection and query injection from unauthenticated actors.
- Reduces payload size and enables HTTP GET caching for queries.

```typescript
import { createPersistedQueryLink } from '@apollo/client/link/persisted-queries';
import { sha256 } from 'crypto-hash';

const link = createPersistedQueryLink({ sha256 }).concat(httpLink);
```

---

## Anti-Patterns

- Authorization logic (`if (!context.user) throw ...`) inside individual resolvers
- Introspection enabled in production for first-party-only APIs
- Rate limiting by HTTP request count without accounting for batching or complexity
- Returning detailed permission errors that reveal resource existence
- Exposing raw database IDs that clients can enumerate
- Stack traces in production error `extensions`
- No depth or complexity limits on a publicly accessible endpoint
- Accepting arbitrary query documents in production instead of using persisted queries
