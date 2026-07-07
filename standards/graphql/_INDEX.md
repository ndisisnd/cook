<!-- AUTO-GENERATED from SKILL.md frontmatters — do not edit manually -->
# graphql Skills Index

## File Match (auto-check against the file you are editing)

| Skill | File pattern | Keywords |
| ----- | ------------ | -------- |
| **graphql** | `**/*.graphql`, `**/*.gql`, `**/schema.ts`, `**/typeDefs.ts`, `**/resolvers/**/*.ts` | graphql, resolver, mutation, query, subscription, schema, SDL, gql, Apollo, DataLoader |
| graphql → schema-design ref | `**/*.graphql`, `**/*.gql` | connection, pagination, cursor, input, payload, error, union, deprecat, scalar, node, global id |
| graphql → conventions ref | `**/*.graphql`, `**/*.gql`, `**/resolvers/**` | naming, camelCase, PascalCase, enum value, boolean prefix, subscription, interface, union, description, docstring, resolver thinness |
| graphql → security ref | `**/server.ts`, `**/app.ts`, `**/resolvers/**` | depth limit, complexity, rate limit, introspection, auth, authorization |
| graphql → performance ref | `**/resolvers/**`, `**/context.ts`, `**/dataloader` | DataLoader, N+1, batch, cache, loader, performance |
| graphql → testing ref | `**/*.test.ts`, `**/*.spec.ts`, `**/resolvers/**/*.test.ts` | resolver test, executeOperation, schema snapshot, integration test, mock context |
| graphql → tooling ref | `codegen.ts`, `codegen.yml`, `.graphqlrc.*`, `graphql.config.*` | codegen, graphql-eslint, graphql-inspector, schema registry, rover, persisted |

> Load `<SKILLS>/graphql/SKILL.md` for any `.graphql` / `.gql` file or resolver — it covers schema correctness and security (P0) and operation conventions (P1).
> Load `<SKILLS>/graphql/refs/schema-design.md` when designing mutations, custom scalars, global object identification, pagination, error handling, or evolving an existing schema.
> Load `<SKILLS>/graphql/refs/conventions.md` when naming schema elements, shaping queries or subscriptions, using interfaces/unions, writing SDL descriptions, or structuring resolvers.
> Load `<SKILLS>/graphql/refs/security.md` when touching server configuration, auth middleware, depth/complexity limits, or field-level security.
> Load `<SKILLS>/graphql/refs/performance.md` when writing resolvers that fetch related entities, or when investigating slow queries.
> Load `<SKILLS>/graphql/refs/testing.md` when writing or reviewing resolver tests, schema snapshot tests, or integration tests.
> Load `<SKILLS>/graphql/refs/tooling.md` when setting up graphql-codegen, graphql-eslint, schema registry, or CI schema checks.
