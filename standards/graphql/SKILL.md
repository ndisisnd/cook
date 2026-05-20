---
name: graphql
description: GraphQL schema design standards and resolver conventions. Use when writing or reviewing any GraphQL schema, resolver, or operation — naming, nullability, types, input objects, mutations, queries, and operation structure.
metadata:
  triggers:
    files:
      - '**/*.graphql'
      - '**/*.gql'
      - '**/schema.ts'
      - '**/schema.js'
      - '**/resolvers/**/*.ts'
      - '**/resolvers/**/*.js'
      - '**/typeDefs.ts'
      - '**/typeDefs.js'
    keywords:
      - graphql
      - resolver
      - mutation
      - query
      - subscription
      - schema
      - type def
      - SDL
      - gql
      - Apollo
      - DataLoader
---

# GraphQL Standards

> Source: [GraphQL Best Practices](https://graphql.org/learn/best-practices/) · [Apollo Naming Conventions](https://www.apollographql.com/docs/graphos/schema-design/guides/naming-conventions) · [GraphQL Schema Design](https://graphql.org/learn/schema-design/)

## Priority: P0 — Schema Correctness

### Nullability

The GraphQL spec makes every field nullable by default. A wrong `!` is not just inaccurate — when a non-null field resolver returns `null`, GraphQL propagates the null **upward** through the response tree, wiping out the nearest nullable parent. One bad guarantee can null out an entire object from the client's response ([graphql.org](https://graphql.org/learn/schema-design/#nullability)).

- Mark a field non-null (`!`) only when the server can **guarantee** it will never be null — not just "usually non-null".
- Mutation payload root fields (`user`, `order`) must be nullable — the mutation may fail and return errors instead of data.
- List elements and the list itself have separate nullability: `[User!]!` means a non-null list of non-null users.
- `ID!` is always non-null — if you have an ID, it exists.

```graphql
# Correct — list is non-null, elements are non-null
users: [User!]!

# Wrong — two levels of null to handle; null element in a list is almost never valid
users: [User]
```

### Scalars & Custom Types

- Use built-in scalars: `String`, `Int`, `Float`, `Boolean`, `ID`.
- Add custom scalars for domain types: `DateTime`, `Date`, `URL`, `EmailAddress`, `JSON`.
- `DON'T` use `String` for dates, emails, or URLs — custom scalars carry semantic meaning, enable server-side validation, and surface intent in generated client types.

```graphql
scalar DateTime
scalar EmailAddress
scalar URL

type User {
  id: ID!
  email: EmailAddress!
  profileUrl: URL
  createdAt: DateTime!
}
```

### Mutation Shape

Every mutation must take a **single `input` argument** typed as an Input object and return a **`Payload` type** — never a naked entity, never `Boolean` ([Apollo](https://www.apollographql.com/docs/graphos/schema-design/guides/naming-conventions)).

Inline scalar arguments are a permanent trap: adding a second argument is a breaking change for every existing client. Adding a field to an Input type is not. Returning a Payload type lets you add `userErrors`, `clientMutationId`, or new fields without breaking the contract.

```graphql
# Correct
type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
  updateUser(input: UpdateUserInput!): UpdateUserPayload!
}

input CreateUserInput {
  firstName: String!
  lastName: String!
  email: EmailAddress!
  role: UserRole!
}

type CreateUserPayload {
  user: User                  # nullable — mutation may fail
  userErrors: [UserError!]!
}

type UserError {
  field: [String!]
  message: String!
  code: UserErrorCode!
}

# Wrong — inline args, no error surface, no evolution path
type Mutation {
  createUser(firstName: String!, lastName: String!, email: String!): User
}
```

### Global Object Identification

Implement the `Node` interface ([graphql.org](https://graphql.org/learn/global-object-identification/)) for any type that clients need to refetch individually. The `id` field must be **globally unique across all types** — base64-encode the type and database ID (`base64("User:123")`), never expose raw database IDs. Without this, Apollo Client and Relay cannot correctly normalise their caches.

```graphql
interface Node {
  id: ID!
}

type User implements Node {
  id: ID!
  name: String!
}

type Query {
  node(id: ID!): Node
}
```

### No Breaking Changes

GraphQL is designed to be versionless — evolve the schema forward additively. Removing or renaming a field breaks every client using it with no warning ([graphql.org](https://graphql.org/learn/best-practices/#versioning)).

- **Never remove a field** without first marking it `@deprecated` and confirming zero usage via field-level observability.
- **Never rename a field** — add the new name, deprecate the old one, remove only after migration.
- **Never make a nullable field non-null** — existing clients don't send the value; they will fail validation.
- **Never add a required argument** to an existing field — existing queries don't include it.
- Adding new nullable fields, new types, and new enum values are safe.

```graphql
type User {
  name: String @deprecated(reason: "Use `firstName` and `lastName` instead.")
  firstName: String!
  lastName: String!
}
```

See `refs/schema-design.md` for the full breaking vs non-breaking change table and deprecation workflow.

---

## Priority: P0 — Security & Performance

### Query Depth & Complexity Limits

Without execution limits, a single deeply nested or deliberately wide query can exhaust the database and crash the server. Enforce both limits **before execution** as validation rules — rejected queries never touch the data layer ([graphql.org](https://graphql.org/learn/security/)):

```typescript
import depthLimit from 'graphql-depth-limit';
import costAnalysis from 'graphql-cost-analysis';

const server = new ApolloServer({
  schema,
  validationRules: [
    depthLimit(7),
    costAnalysis({ maximumCost: 1000, defaultCost: 1, listFactor: 10 }),
  ],
});
```

- Depth limit of **5–7** covers most real-world query patterns.
- Apply a stricter limit (e.g., 3) to nested list fields — list nesting causes data to grow exponentially.
- Cost analysis catches shallow-but-wide queries that depth limiting misses.

See `refs/security.md` for rate limiting, introspection, persisted queries, and field-level security.

### Authorization

**Authorization belongs in the business logic layer, not in resolvers.** Scattering `if (!context.user)` checks across individual resolvers guarantees that some field will be missed ([graphql.org](https://graphql.org/learn/authorization/)):

```typescript
// Correct — resolver delegates; auth enforced in the model
const resolvers = {
  Query: {
    order: (_, { id }, { user }) => OrderModel.findForUser(id, user),
  },
};

// OrderModel enforces auth — not the resolver
class OrderModel {
  static async findForUser(id: string, viewer: User) {
    const order = await db.orders.findById(id);
    if (!order || order.userId !== viewer.id) return null;
    return order;
  }
}
```

- Pass a fully hydrated `user` object in `context`, not a raw token.
- Return `null` for not-found or unauthorised resources — never throw a permission error that reveals whether the resource exists (existence leakage is an information disclosure).
- For field-level authorization, use a schema transformer or plugin (`@auth` directive) that wraps resolvers — never manual `if` checks per field.

### DataLoader (N+1 Prevention)

Every field resolver that fetches by a foreign key **must** use DataLoader. Without it, a query for 100 posts and their authors fires 101 database queries. At scale this collapses response times and saturates connection pools.

**Critical rule:** create a **new DataLoader instance per request**. A shared loader caches data across requests — it will serve one user's data to another ([graphql-js.org](https://www.graphql-js.org/docs/n1-dataloader/)).

```typescript
// context.ts — new loaders per request
export function createContext({ req }: { req: Request }) {
  return {
    user: req.user,
    loaders: {
      user: new DataLoader(batchLoadUsers),
      product: new DataLoader(batchLoadProducts),
    },
  };
}

// resolver — uses loader, never direct DB call
const resolvers = {
  Post: {
    author: (post, _, { loaders }) => loaders.user.load(post.authorId),
  },
};
```

- Batch functions **must return results in the same order as input keys** — DataLoader maps `result[i]` to `keys[i]`; wrong order silently corrupts data.
- Return `null` for missing entries, never a shorter array.
- Use `.prime(key, value)` to pre-populate the cache when you already fetched the data in a list query.

See `refs/performance.md` for the full DataLoader setup, HTTP caching, and query execution patterns.

---

## Priority: P1 — Operations & Conventions

### Naming

Follow these conventions consistently across the entire schema ([Apollo](https://www.apollographql.com/docs/graphos/schema-design/guides/naming-conventions)):

| Element | Convention | Example |
|---|---|---|
| Types, interfaces, unions, enums | `PascalCase` | `UserProfile`, `PaymentMethod` |
| Fields, arguments, variables, aliases | `camelCase` | `firstName`, `createdAt` |
| Enum values | `ALL_CAPS` | `PENDING`, `IN_PROGRESS` |
| Input types | `PascalCase` + `Input` suffix | `CreateUserInput`, `UpdateOrderInput` |
| Mutation payload types | `PascalCase` + `Payload` suffix | `CreateUserPayload` |
| Directives | `camelCase` | `@deprecated`, `@auth` |

- `DON'T` prefix types with `I` for interfaces or `T` for types — GraphQL SDL already expresses this.
- `DON'T` use generic names (`data`, `result`, `response`) as field names — be specific.
- `DO` use `is`, `has`, or `can` prefixes for boolean fields: `isActive`, `hasPermission`, `canEdit`.
- Mutation names must be verb + noun: `createUser`, `updateOrder`, `deleteComment`.

### Queries

- Query fields return their primary type or a Connection type for lists — never a raw array without pagination support.
- Single-resource queries accept `id: ID!`. Multi-resource queries accept a filter input.
- Return `null` for not-found single resources; don't throw a not-found error.

```graphql
type Query {
  user(id: ID!): User
  users(filter: UserFilterInput, first: Int, after: String): UserConnection!
}
```

### Subscriptions

- Only expose subscriptions for genuine real-time needs — not as a replacement for polling.
- Subscription names use past-tense events: `userCreated`, `orderStatusChanged`.
- Return the full updated entity, not just a diff.

```graphql
type Subscription {
  orderStatusChanged(orderId: ID!): Order!
  messageReceived(conversationId: ID!): Message!
}
```

### Interfaces & Unions

- Use `interface` when types share common fields that clients query polymorphically.
- Use `union` when types have nothing structurally in common but appear in the same position.
- Always include `__typename` in fragment selections on unions/interfaces so clients can discriminate.

```graphql
interface Node {
  id: ID!
}

union SearchResult = User | Post | Comment

type Query {
  search(query: String!): [SearchResult!]!
}
```

### Descriptions

Document all types, fields, arguments, and enum values with SDL descriptions. These appear in introspection, GraphiQL, and generated client types.

```graphql
"""A registered user of the platform."""
type User {
  """Globally unique identifier."""
  id: ID!
  """The user's primary email address. Used for login and notifications."""
  email: EmailAddress!
}
```

### Resolver Thinness

Resolvers are a routing layer — not a business logic layer. Keep them as thin as possible:

- Delegate all data fetching and business logic to a service or model layer.
- Pass auth context via the `context` argument; never use module-level globals.

```typescript
const resolvers = {
  Query: {
    user: (_, { id }, { services }) => services.user.findById(id),
  },
};
```

---

## Anti-Patterns

- Inline scalar arguments on mutations instead of a single `Input` type
- Returning a naked entity or `Boolean` from a mutation instead of a `Payload` type
- Using `String` for dates, emails, or URLs — use custom scalars
- Non-null (`!`) on fields that could realistically be null
- Nullable list elements `[User]` — almost always want `[User!]!`
- `data`, `result`, `response` as field names — too generic
- Authorization checks (`if (!context.user)`) inside individual resolvers
- Field resolvers that fetch related entities with direct DB calls instead of DataLoader
- Sharing a DataLoader instance across requests — leaks data between users
- Removing or renaming fields without first adding `@deprecated`
- Making a nullable field non-null or adding a required argument — breaking changes
- No query depth or complexity limits on a publicly accessible endpoint
- Introspection enabled in production for first-party-only APIs
- `type` or `I` prefixes on types and interfaces

---

## References

Load only what the current task requires:

- [schema-design](refs/schema-design.md) — designing mutations, pagination, error handling patterns, or evolving an existing schema
- [security](refs/security.md) — server configuration, auth middleware, depth/complexity limits, introspection, rate limiting, or field-level security
- [performance](refs/performance.md) — DataLoader setup, N+1 investigation, HTTP caching, or query execution optimisation
- [testing](refs/testing.md) — writing or reviewing resolver tests, schema snapshot tests, or integration tests
- [tooling](refs/tooling.md) — setting up graphql-codegen, graphql-eslint, schema registry, or CI schema checks
