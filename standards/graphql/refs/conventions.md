# GraphQL Operations & Conventions

> Source: [Apollo Naming Conventions](https://www.apollographql.com/docs/graphos/schema-design/guides/naming-conventions) · [GraphQL Best Practices](https://graphql.org/learn/best-practices/)

Priority: P1 — Operations & Conventions.

## Naming

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

---

## Queries

- Query fields return their primary type or a Connection type for lists — never a raw array without pagination support.
- Single-resource queries accept `id: ID!`. Multi-resource queries accept a filter input.
- Return `null` for not-found single resources; don't throw a not-found error.

```graphql
type Query {
  user(id: ID!): User
  users(filter: UserFilterInput, first: Int, after: String): UserConnection!
}
```

---

## Subscriptions

- Only expose subscriptions for genuine real-time needs — not as a replacement for polling.
- Subscription names use past-tense events: `userCreated`, `orderStatusChanged`.
- Return the full updated entity, not just a diff.

```graphql
type Subscription {
  orderStatusChanged(orderId: ID!): Order!
  messageReceived(conversationId: ID!): Message!
}
```

---

## Interfaces & Unions

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

---

## Descriptions

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

---

## Resolver Thinness

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
