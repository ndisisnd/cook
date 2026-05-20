---
status: completed
---

# Verification Run [2] — GraphQL Standards P0 Rewrite + Missing Refs

## 1. What Will Be Changed

### `standards/graphql/SKILL.md` — P0 section restructured

**Problem:** The current P0 is misaligned in two ways:
- It contains things that are **style, not correctness** (naming conventions — wrong case doesn't break anything)
- It is **missing genuinely critical rules** that cause server crashes, data leaks, and irreversible breaking changes

**Changes:**

| Section | Current | After |
|---|---|---|
| Naming | P0 | Moved to P1. Only structural naming rules (`Input`/`Payload` suffixes) survive, folded into Mutation Shape |
| Nullability | P0 | Stays. Strengthened with null-propagation explanation (wrong `!` wipes parent objects) |
| Scalars | P0 | Stays. Framed as correctness — `String` for domain types loses runtime validation |
| Interfaces & Unions | P0 | Moved to P1 — design guidance, not correctness |
| Global Object Identification | P0 | Stays. Framed around cache correctness and refetch |
| **Mutation Shape** | P1 | **Elevated to P0** — inline args make schema evolution a breaking change with no escape |
| **DataLoader** | Buried in P1 Resolvers note | **Elevated to P0** — N+1 collapses production; shared loader leaks data across users |
| **Security** (depth, complexity, auth layer, introspection) | refs/security.md only | **Core rules elevated to P0** — no limits = one query crashes the server |
| **No Breaking Changes** | refs/schema-design.md only | **Core rule elevated to P0** — removing a field breaks clients immediately and irreversibly |

**New P0 section structure:**

```
## Priority: P0 — Schema Correctness
### Nullability
### Scalars & Custom Types
### Mutation Shape (Input + Payload)
### Global Object Identification
### No Breaking Changes

## Priority: P0 — Security & Performance
### Query Depth & Complexity Limits
### Authorization
### DataLoader (N+1 Prevention)
```

**New P1 section structure:**

```
## Priority: P1 — Operations & Conventions
### Naming
### Queries
### Subscriptions
### Interfaces & Unions
### Descriptions
### Resolver Thinness
```

---

### `standards/graphql/SKILL.md` — References section updated

Current references section is a bare list with no loading conditions:
```md
## References
- [schema-design](refs/schema-design.md)
- [security](refs/security.md)
- [performance](refs/performance.md)
```

After — matches dart/typescript style with conditional loading instructions:
```md
## References

Load only what the current task requires:
- [schema-design](refs/schema-design.md) — designing mutations, pagination, error handling, or evolving an existing schema
- [security](refs/security.md) — server configuration, auth middleware, depth/complexity limits, introspection, or field-level security
- [performance](refs/performance.md) — DataLoader setup, N+1 investigation, HTTP caching, or query execution optimisation
- [testing](refs/testing.md) — writing or reviewing resolver tests, schema snapshot tests, or integration tests
- [tooling](refs/tooling.md) — setting up graphql-codegen, graphql-eslint, schema registry, or CI schema checks
```

---

### `standards/graphql/refs/testing.md` — New file

Does not exist. Will be created covering:
- **Unit testing resolvers** — mocking context, services, and DataLoaders; testing query/mutation/subscription resolvers in isolation
- **Integration testing** — spinning up a real Apollo Server in tests, executing operations with `executeOperation`, asserting on response shape and errors
- **Schema snapshot testing** — printing the SDL and diffing against a stored snapshot to catch accidental breaking changes
- **Testing error paths** — asserting on `userErrors`, GraphQL `errors` array, and HTTP status codes
- **DataLoader testing** — verifying batch functions, testing `.prime()`, asserting call counts
- **Anti-patterns** — mocking at the HTTP layer instead of the server layer; not resetting mocks between tests; testing resolvers without context

---

### `standards/graphql/refs/tooling.md` — New file

Does not exist. Will be created covering:
- **`graphql-codegen`** — generating TypeScript types from SDL; config for `typescript`, `typescript-resolvers`, and `typescript-operations` plugins; watch mode for development
- **`graphql-eslint`** — schema linting rules (`no-unreachable-types`, `require-description`, `naming-convention`); operation linting (`no-deprecated`, `require-id-when-available`, `selection-set-depth`)
- **`graphql-inspector`** — CI check for breaking schema changes; diff command; GitHub Action integration
- **Schema registry** — Apollo Studio / Rover CLI for schema publishing and checks; schema checks as a PR gate
- **Persisted queries toolchain** — `@apollo/generate-persisted-query-manifest`; registering the manifest with the server
- **Anti-patterns** — running codegen manually instead of as a CI/watch step; no schema linting; no breaking change detection in CI

---

### `standards/graphql/_INDEX.md` — Two new rows added

Current rows:

| Skill | File pattern | Keywords |
| ----- | ------------ | -------- |
| graphql → schema-design ref | `**/*.graphql`, `**/*.gql` | connection, pagination, cursor, input, payload, error, union, deprecat |
| graphql → security ref | `**/server.ts`, `**/app.ts`, `**/resolvers/**` | depth limit, complexity, rate limit, introspection, auth, authorization |
| graphql → performance ref | `**/resolvers/**`, `**/context.ts`, `**/dataloader` | DataLoader, N+1, batch, cache, loader, performance |

New rows to add:

| Skill | File pattern | Keywords |
| ----- | ------------ | -------- |
| graphql → testing ref | `**/*.test.ts`, `**/*.spec.ts`, `**/resolvers/**/*.test.ts` | resolver test, executeOperation, schema snapshot, integration test, mock context |
| graphql → tooling ref | `codegen.ts`, `codegen.yml`, `.graphqlrc.*`, `graphql.config.*` | codegen, graphql-eslint, graphql-inspector, schema registry, rover, persisted |

Loading notes section updated to include testing and tooling refs.

---

## 2. Files Touched

| File | Action |
|---|---|
| `standards/graphql/SKILL.md` | Edit — restructure P0, elevate mutation shape + DataLoader + security + breaking changes, update References section, update P1 |
| `standards/graphql/refs/testing.md` | Create |
| `standards/graphql/refs/tooling.md` | Create |
| `standards/graphql/_INDEX.md` | Edit — add 2 new ref rows and loading notes |

---

## 3. Success Criteria

### Structure
- [ ] `standards/graphql/SKILL.md` exists and is non-empty
- [ ] `standards/graphql/refs/schema-design.md` unchanged (already good)
- [ ] `standards/graphql/refs/security.md` unchanged (already good)
- [ ] `standards/graphql/refs/performance.md` unchanged (already good)
- [ ] `standards/graphql/refs/testing.md` exists
- [ ] `standards/graphql/refs/tooling.md` exists
- [ ] `standards/graphql/_INDEX.md` has 5 ref rows (schema-design, security, performance, testing, tooling)

### Content — SKILL.md P0
- [ ] P0 contains **Nullability** with null-propagation explanation
- [ ] P0 contains **Scalars & Custom Types** framed as correctness
- [ ] P0 contains **Mutation Shape** — single `input` arg, `Payload` return, `userErrors`, never Boolean/naked entity
- [ ] P0 contains **Global Object Identification** (Node interface)
- [ ] P0 contains **No Breaking Changes** — additive only, `@deprecated` before removal
- [ ] P0 contains **Query Depth & Complexity Limits** — before-execution enforcement with example values
- [ ] P0 contains **Authorization** — business layer not resolvers; return `null` not permission error
- [ ] P0 contains **DataLoader** — every foreign-key resolver; new instance per request; ordering contract
- [ ] **Naming is NOT in P0** (moved to P1)
- [ ] **Interfaces & Unions are NOT in P0** (moved to P1)

### Content — SKILL.md P1
- [ ] P1 contains Naming (with the full conventions table)
- [ ] P1 contains Queries
- [ ] P1 contains Subscriptions
- [ ] P1 contains Interfaces & Unions
- [ ] P1 contains Descriptions
- [ ] P1 contains Resolver Thinness

### Content — SKILL.md References
- [ ] Uses "Load only what the current task requires" preamble
- [ ] Each of the 5 refs has a one-line task-based condition
- [ ] testing.md and tooling.md are listed

### Content — `refs/testing.md`
- [ ] Unit testing resolvers with mocked context/services
- [ ] Integration testing with `executeOperation` against a real Apollo Server
- [ ] Schema snapshot testing (SDL diff)
- [ ] Testing `userErrors` and GraphQL error paths
- [ ] DataLoader batch function testing
- [ ] Anti-patterns section

### Content — `refs/tooling.md`
- [ ] `graphql-codegen` config with `typescript` + `typescript-resolvers` + `typescript-operations` plugins
- [ ] `graphql-eslint` config with schema and operation rules
- [ ] `graphql-inspector` CI check for breaking changes
- [ ] Schema registry / Rover CLI
- [ ] Persisted queries toolchain
- [ ] Anti-patterns section

### No duplication
- [ ] Security rules in P0 (depth, auth) are **summary rules** — the full implementation detail stays in `refs/security.md`
- [ ] DataLoader rules in P0 are **requirements** — the full DataLoader setup stays in `refs/performance.md`
- [ ] Breaking change rule in P0 is the rule — the deprecation workflow stays in `refs/schema-design.md`
- [ ] Anti-patterns in SKILL.md do not duplicate anti-patterns in individual refs
