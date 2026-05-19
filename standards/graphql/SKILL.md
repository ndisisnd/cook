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

```graphql
# Good
type User {
  id: ID!
  firstName: String!
  lastName: String!
  isActive: Boolean!
  createdAt: DateTime!
}

enum OrderStatus {
  PENDING
  IN_PROGRESS
  COMPLETED
  CANCELLED
}

# Bad — non-descriptive, wrong case
type userdata {
  Info: String
  active: Boolean
}
```

### Nullability
The GraphQL spec makes every field nullable by default. Apply `!` (non-null) deliberately ([graphql.org](https://graphql.org/learn/schema-design/#nullability)):

- Mark a field non-null (`!`) only when the server can **guarantee** it will never be null — not just "usually non-null".
- Mutation payload root fields (`user`, `order`) should be nullable — the mutation may fail and return errors instead.
- List elements and the list itself have separate nullability: `[User!]!` means a non-null list of non-null users.
- `ID!` is always non-null — if you have an ID, it exists.

```graphql
# Prefer: list is non-null, elements are non-null
users: [User!]!

# Avoid: nullable list of nullable users — two levels of null to handle
users: [User]
```

### Scalars
- Use built-in scalars: `String`, `Int`, `Float`, `Boolean`, `ID`.
- Add custom scalars for domain types: `DateTime`, `Date`, `URL`, `EmailAddress`, `JSON`.
- `DON'T` use `String` for dates or URLs — custom scalars carry semantic meaning and enable validation.

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

### Interfaces and Unions
- Use `interface` when types share common fields that clients will query polymorphically.
- Use `union` when types have nothing structurally in common but can appear in the same position.
- Always include `__typename` in fragment selections on unions/interfaces so clients can discriminate.

```graphql
interface Node {
  id: ID!
}

union SearchResult = User | Post | Comment

type Query {
  node(id: ID!): Node
  search(query: String!): [SearchResult!]!
}
```

### Global Object Identification
Implement the `Node` interface ([graphql.org](https://graphql.org/learn/global-object-identification/)) for any type that clients need to refetch individually. The `id` field must be globally unique across all types.

```graphql
interface Node {
  id: ID!
}

type User implements Node {
  id: ID!       # globally unique, e.g. base64("User:123")
  name: String!
}

type Query {
  node(id: ID!): Node
}
```

---

## Priority: P1 — Operations & Conventions

### Queries
- Query fields return their primary type or a Connection type for lists — never a raw array without pagination support.
- Single-resource queries accept `id: ID!`. Multi-resource queries accept a filter input.
- Return `null` for not-found single resources; don't throw a not-found error.

```graphql
type Query {
  user(id: ID!): User                           # null if not found
  users(filter: UserFilterInput, first: Int, after: String): UserConnection!
  post(id: ID!): Post
}
```

### Mutations
- Every mutation takes a **single** input argument named `input` typed as an Input object — not inline scalar args ([Apollo](https://www.apollographql.com/docs/graphos/schema-design/guides/naming-conventions)).
- Every mutation returns a **Payload** type — never the naked entity. This allows adding fields (errors, clientMutationId) without breaking changes.
- The Payload type should include the mutated entity on success and be able to express failure (see `refs/schema-design.md`).

```graphql
type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
  updateUser(input: UpdateUserInput!): UpdateUserPayload!
  deleteUser(input: DeleteUserInput!): DeleteUserPayload!
}

input CreateUserInput {
  firstName: String!
  lastName: String!
  email: EmailAddress!
  role: UserRole!
}

type CreateUserPayload {
  user: User
  userErrors: [UserError!]!
}

type UserError {
  field: [String!]
  message: String!
}
```

### Subscriptions
- Only expose subscriptions for real-time data needs — not as a replacement for polling.
- Subscription names should be past-tense events: `userCreated`, `orderStatusChanged`.
- Return the full updated entity, not just a diff.

```graphql
type Subscription {
  orderStatusChanged(orderId: ID!): Order!
  messageReceived(conversationId: ID!): Message!
}
```

### Descriptions
Document all types, fields, arguments, and enum values with SDL descriptions. These appear in introspection and tools like GraphiQL.

```graphql
"""
A registered user of the platform.
"""
type User {
  """Globally unique identifier."""
  id: ID!
  """The user's primary email address. Used for login and notifications."""
  email: EmailAddress!
}
```

### Schema Evolution & Deprecation
Never remove or rename fields without deprecating first ([Apollo](https://www.apollographql.com/docs/graphos/schema-design/guides/deprecations)):

```graphql
type User {
  name: String @deprecated(reason: "Use `firstName` and `lastName` instead.")
  firstName: String!
  lastName: String!
}
```

- Add new fields; deprecate old ones; only remove after confirming zero client usage via field-level observability.
- Prefer field evolution over URL versioning — GraphQL is designed to be versionless ([graphql.org](https://graphql.org/learn/best-practices/#versioning)).

### Resolvers
- Keep resolvers thin — delegate data fetching and business logic to a service/model layer.
- Pass auth context via the `context` argument; never use module-level globals.
- Always use DataLoader for any resolver that fetches by a foreign key (see `refs/performance.md`).
- Authorization belongs in the business logic layer, not in resolvers ([graphql.org](https://graphql.org/learn/authorization/)).

```typescript
// Thin resolver — delegates to service and loader
const resolvers = {
  Query: {
    user: (_, { id }, { services }) => services.user.findById(id),
  },
  Post: {
    // DataLoader prevents N+1
    author: (post, _, { loaders }) => loaders.user.load(post.authorId),
  },
};
```

---

## Anti-Patterns

- Inline scalar arguments on mutations instead of an `Input` type
- Returning the raw entity from a mutation instead of a `Payload` type
- Using `String` for dates, IDs, emails — use custom scalars
- Non-null (`!`) on fields that could realistically be null
- Nullable list elements `[User]` — almost always want `[User!]!`
- `data`, `result`, `response` as field names — too generic
- Authorization logic inside resolvers instead of the business layer
- Resolvers that fetch related entities directly instead of using DataLoader
- Removing or renaming fields without first adding `@deprecated`
- `type` or `I` prefixes on types and interfaces

---

## References

- [schema-design](refs/schema-design.md)
- [security](refs/security.md)
- [performance](refs/performance.md)
