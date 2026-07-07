# GraphQL Schema Design

> Source: [Pagination – graphql.org](https://graphql.org/learn/pagination/) · [Relay Cursor Connections Specification](https://relay.dev/graphql/connections.htm) · [Relay-Style Connections – Apollo](https://www.apollographql.com/docs/graphos/schema-design/guides/relay-style-connections) · [Error Handling – Apollo Server](https://www.apollographql.com/docs/apollo-server/data/errors) · [Schema Deprecations – Apollo](https://www.apollographql.com/docs/graphos/schema-design/guides/deprecations)

## Connections & Pagination

Use the [Relay Cursor Connections Specification](https://relay.dev/graphql/connections.htm) for all paginated lists. Offset-based pagination (`page` + `limit`) cannot express stable cursors and breaks under concurrent mutations.

### Standard Connection Shape

```graphql
type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type UserEdge {
  node: User!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}
```

### Pagination Arguments

Forward pagination uses `first` + `after`; backward pagination uses `last` + `before`. Never mix directions in a single request.

```graphql
type Query {
  users(
    first: Int
    after: String
    last: Int
    before: String
    filter: UserFilterInput
    orderBy: UserOrderByInput
  ): UserConnection!
}
```

### Cursor Implementation Notes

- Cursors must be **opaque** to clients — base64-encode them (`base64("User:123")`), never expose raw database IDs or offsets.
- Implement pagination with a `WHERE id > cursor` clause, not `OFFSET` — offset pagination degrades as pages grow and breaks under inserts ([graphql.org](https://graphql.org/learn/pagination/)).
- Return the wrapper `Connection` type even before adding pagination — you can add `first`/`after` later without a breaking change.

---

## Nullability

List elements and the list itself have separate nullability:

```graphql
# Correct — list is non-null, elements are non-null
users: [User!]!

# Wrong — two levels of null to handle; null element in a list is almost never valid
users: [User]
```

---

## Custom Scalars

Declare custom scalars for domain types instead of overloading `String`:

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

---

## Global Object Identification

The `Node` interface pattern ([graphql.org](https://graphql.org/learn/global-object-identification/)) — the `id` field must be globally unique across all types:

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

---

## Input Types & Mutation Design

Every mutation takes a **single `input` argument**. Design one input type per mutation, not a shared input reused across create/update.

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

```graphql
# Good — each mutation has its own tailored input
input CreateProductInput {
  name: String!
  description: String
  price: Float!
  categoryId: ID!
}

input UpdateProductInput {
  id: ID!
  name: String
  description: String
  price: Float
}

# Bad — a single "god" input with optional everything
input ProductInput {
  id: ID
  name: String
  price: Float
  # ...
}
```

- Required fields on create are `String!`; fields on update are nullable because only provided fields are patched.
- `DON'T` use positional arguments on mutations — adding a second argument is a breaking change; adding a field to an `Input` type is not.

---

## Error Handling

Two accepted patterns exist. Choose one and apply it consistently across the schema.

### Pattern 1: Payload with `userErrors` (Shopify/Apollo style)

Business-logic errors (validation, not-found, permission) appear in `userErrors` on the payload. HTTP-level and unexpected errors surface as top-level GraphQL errors.

```graphql
type CreateOrderPayload {
  order: Order
  userErrors: [UserError!]!
}

type UserError {
  """The input field path that caused the error, if applicable."""
  field: [String!]
  message: String!
  code: UserErrorCode!
}

enum UserErrorCode {
  NOT_FOUND
  INVALID_INPUT
  PERMISSION_DENIED
  DUPLICATE
}
```

Client usage:

```graphql
mutation CreateOrder($input: CreateOrderInput!) {
  createOrder(input: $input) {
    order { id status }
    userErrors { field message code }
  }
}
```

### Pattern 2: Union Result Types

Model errors as first-class GraphQL types in a union. Provides stronger typing but requires `__typename` discrimination on the client.

```graphql
union CreateOrderResult = Order | ValidationError | InsufficientInventoryError

type Mutation {
  createOrder(input: CreateOrderInput!): CreateOrderResult!
}

type ValidationError {
  field: String!
  message: String!
}

type InsufficientInventoryError {
  productId: ID!
  requested: Int!
  available: Int!
}
```

Client usage:

```graphql
mutation CreateOrder($input: CreateOrderInput!) {
  createOrder(input: $input) {
    __typename
    ... on Order { id status }
    ... on ValidationError { field message }
    ... on InsufficientInventoryError { productId requested available }
  }
}
```

> See [Handling GraphQL errors like a champ with unions and interfaces – LogRocket](https://blog.logrocket.com/handling-graphql-errors-like-a-champ-with-unions-and-interfaces/)

### What NOT to Do

- `DON'T` throw authentication/authorization errors as `userErrors` — use top-level GraphQL errors with `extensions.code`.
- `DON'T` return `Boolean` from mutations — there is no way to include error details.
- `DON'T` model every possible server error as a union variant — only expected, actionable failure states belong in the schema.

---

## Schema Evolution & Deprecation

GraphQL is designed to be **versionless** ([graphql.org](https://graphql.org/learn/best-practices/#versioning)). Evolve the schema forward; never introduce breaking changes.

### Breaking vs Non-Breaking Changes

| Change | Breaking? |
|---|---|
| Adding a new field to a type | No |
| Adding a nullable argument to a field | No |
| Adding a new type | No |
| Adding a new enum value | No (but may break exhaustive switches on clients) |
| Removing a field | **Yes** |
| Renaming a field | **Yes** |
| Changing a field type | **Yes** |
| Making a nullable field non-null | **Yes** |
| Adding a required argument | **Yes** |

### Deprecation Workflow

1. Add the replacement field (or type).
2. Mark the old field `@deprecated` with a migration instruction.
3. Track field-level usage in production observability (log `operationName` + deprecated fields used per request).
4. Remove the field only after zero-usage is confirmed.

```graphql
type User {
  """
  @deprecated Use `displayName` instead.
  """
  name: String @deprecated(reason: "Use `displayName` instead.")
  displayName: String!
  
  """
  @deprecated Use `address.streetLine1` instead.
  """
  street: String @deprecated(reason: "Use `address { streetLine1 }` instead.")
  address: Address
}
```

### Additive-Only Rule

Never rename — add a new field with the better name, then deprecate the old one:

```graphql
# v1 schema had: fullName: String!
# Step 1: add the replacement
type User {
  fullName: String! @deprecated(reason: "Use `firstName` and `lastName`.")
  firstName: String!
  lastName: String!
}
# Step 2 (after clients migrate): remove fullName
```

---

## Anti-Patterns

- Offset-based pagination (`page` + `pageSize`) instead of cursor-based connections
- Exposing raw database IDs or offsets as cursors
- Reusing a single Input type across create and update mutations
- Returning `Boolean` or a naked entity from mutations
- Removing fields without a deprecation period and usage monitoring
- Throwing validation errors as top-level GraphQL errors instead of `userErrors`
- Making nullable fields non-null (breaking change)
- Adding required arguments to existing fields (breaking change)
