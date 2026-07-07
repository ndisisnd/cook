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

### Scalars & Custom Types

- Use built-in scalars: `String`, `Int`, `Float`, `Boolean`, `ID`.
- Add custom scalars for domain types: `DateTime`, `Date`, `URL`, `EmailAddress`, `JSON`.
- `DON'T` use `String` for dates, emails, or URLs — custom scalars carry semantic meaning, enable server-side validation, and surface intent in generated client types.

See `refs/schema-design.md` for custom scalar declaration examples.

### Mutation Shape

Every mutation must take a **single `input` argument** typed as an Input object and return a **`Payload` type** — never a naked entity, never `Boolean` ([Apollo](https://www.apollographql.com/docs/graphos/schema-design/guides/naming-conventions)).

See `refs/schema-design.md` for input/payload design rationale and full examples.

### Global Object Identification

Implement the `Node` interface ([graphql.org](https://graphql.org/learn/global-object-identification/)) for any type that clients need to refetch individually. The `id` field must be **globally unique across all types** — base64-encode the type and database ID (`base64("User:123")`), never expose raw database IDs. Without this, Apollo Client and Relay cannot correctly normalise their caches.

### No Breaking Changes

GraphQL is designed to be versionless — evolve the schema forward additively. Removing or renaming a field breaks every client using it with no warning ([graphql.org](https://graphql.org/learn/best-practices/#versioning)).

- **Never remove a field** without first marking it `@deprecated` and confirming zero usage via field-level observability.
- **Never rename a field** — add the new name, deprecate the old one, remove only after migration.
- **Never make a nullable field non-null** — existing clients don't send the value; they will fail validation.
- **Never add a required argument** to an existing field — existing queries don't include it.
- Adding new nullable fields, new types, and new enum values are safe.

See `refs/schema-design.md` for the full breaking vs non-breaking change table and deprecation workflow.

---

## Priority: P0 — Security & Performance

### Query Depth & Complexity Limits

Without execution limits, a single deeply nested or deliberately wide query can exhaust the database and crash the server. Enforce both limits **before execution** as validation rules — rejected queries never touch the data layer ([graphql.org](https://graphql.org/learn/security/)).

- Depth limit of **5–7** covers most real-world query patterns.
- Apply a stricter limit (e.g., 3) to nested list fields — list nesting causes data to grow exponentially.
- Cost analysis catches shallow-but-wide queries that depth limiting misses.

See `refs/security.md` for validation-rule setup, rate limiting, introspection, persisted queries, and field-level security.

### Authorization

**Authorization belongs in the business logic layer, not in resolvers.** Scattering `if (!context.user)` checks across individual resolvers guarantees that some field will be missed ([graphql.org](https://graphql.org/learn/authorization/)).

- Pass a fully hydrated `user` object in `context`, not a raw token.
- Return `null` for not-found or unauthorised resources — never throw a permission error that reveals whether the resource exists (existence leakage is an information disclosure).
- For field-level authorization, use a schema transformer or plugin (`@auth` directive) that wraps resolvers — never manual `if` checks per field.

### DataLoader (N+1 Prevention)

Every field resolver that fetches by a foreign key **must** use DataLoader. Without it, a query for 100 posts and their authors fires 101 database queries. At scale this collapses response times and saturates connection pools.

**Critical rule:** create a **new DataLoader instance per request**. A shared loader caches data across requests — it will serve one user's data to another ([graphql-js.org](https://www.graphql-js.org/docs/n1-dataloader/)).

- Batch functions **must return results in the same order as input keys** — DataLoader maps `result[i]` to `keys[i]`; wrong order silently corrupts data.
- Return `null` for missing entries, never a shorter array.
- Use `.prime(key, value)` to pre-populate the cache when you already fetched the data in a list query.

See `refs/performance.md` for the full DataLoader setup, HTTP caching, and query execution patterns.

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

- [schema-design](refs/schema-design.md) — designing mutations, custom scalars, global object identification, pagination, error handling patterns, or evolving an existing schema
- [conventions](refs/conventions.md) — naming conventions, query/subscription shape, interfaces and unions, SDL descriptions, and resolver thinness
- [security](refs/security.md) — server configuration, auth middleware, depth/complexity limits, introspection, rate limiting, or field-level security
- [performance](refs/performance.md) — DataLoader setup, N+1 investigation, HTTP caching, or query execution optimisation
- [testing](refs/testing.md) — writing or reviewing resolver tests, schema snapshot tests, or integration tests
- [tooling](refs/tooling.md) — setting up graphql-codegen, graphql-eslint, schema registry, or CI schema checks
