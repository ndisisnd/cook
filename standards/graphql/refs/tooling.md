# GraphQL Tooling

> Source: [graphql-code-generator](https://the-guild.dev/graphql/codegen) · [graphql-eslint](https://the-guild.dev/graphql/eslint) · [graphql-inspector](https://the-guild.dev/graphql/inspector) · [Apollo Rover CLI](https://www.apollographql.com/docs/rover/) · [Persisted Queries – Apollo](https://www.apollographql.com/docs/apollo-server/performance/apq/)

## graphql-codegen

Generate TypeScript types from your SDL so resolvers and client operations are always in sync with the schema. Running this as a CI step catches type mismatches before they reach production.

### Installation

```bash
npm install -D @graphql-codegen/cli @graphql-codegen/typescript \
  @graphql-codegen/typescript-resolvers @graphql-codegen/typescript-operations
```

### Config (`codegen.ts`)

```typescript
import type { CodegenConfig } from '@graphql-codegen/cli';

const config: CodegenConfig = {
  schema: './src/schema/**/*.graphql',
  documents: './src/**/*.graphql',   // client operations — omit for server-only projects
  generates: {
    // Server-side resolver types
    './src/generated/resolvers.ts': {
      plugins: ['typescript', 'typescript-resolvers'],
      config: {
        contextType: '../context#Context',
        mappers: {
          User: '../models/user#UserModel',
          Post: '../models/post#PostModel',
        },
        useIndexSignature: true,
      },
    },
    // Client-side operation types (if applicable)
    './src/generated/operations.ts': {
      plugins: ['typescript', 'typescript-operations'],
    },
  },
};

export default config;
```

### Running codegen

```json
// package.json scripts
{
  "codegen": "graphql-codegen --config codegen.ts",
  "codegen:watch": "graphql-codegen --config codegen.ts --watch"
}
```

- Run `codegen:watch` during development — regenerates on schema or operation file change.
- Run `codegen` in CI as a pre-build step and fail the pipeline if generated files are out of date (`git diff --exit-code src/generated/`).
- Commit generated files to the repo — they serve as a schema change audit trail in PRs.

---

## graphql-eslint

Lint both the schema SDL and client operations using ESLint. Enforces naming conventions, requires descriptions, prevents deprecated field usage, and limits operation depth.

### Installation

```bash
npm install -D @graphql-eslint/eslint-plugin
```

### Config (`eslint.config.js`)

```javascript
import graphqlPlugin from '@graphql-eslint/eslint-plugin';

export default [
  // Schema SDL files
  {
    files: ['**/*.graphql'],
    languageOptions: {
      parser: graphqlPlugin.parser,
      parserOptions: {
        graphQLConfig: {
          schema: './src/schema/**/*.graphql',
          documents: './src/**/*.graphql',
        },
      },
    },
    plugins: { '@graphql-eslint': graphqlPlugin },
    rules: {
      // Schema rules
      '@graphql-eslint/naming-convention': ['error', {
        types: 'PascalCase',
        FieldDefinition: 'camelCase',
        InputValueDefinition: 'camelCase',
        EnumValueDefinition: 'UPPER_CASE',
        DirectiveDefinition: 'camelCase',
      }],
      '@graphql-eslint/require-description': ['error', {
        types: true,
        FieldDefinition: true,
        EnumValueDefinition: true,
      }],
      '@graphql-eslint/no-unreachable-types': 'error',
      '@graphql-eslint/no-unused-fields': 'warn',
      // Operation rules
      '@graphql-eslint/no-deprecated': 'warn',
      '@graphql-eslint/require-id-when-available': 'error',
      '@graphql-eslint/selection-set-depth': ['error', { maxDepth: 7 }],
      '@graphql-eslint/no-anonymous-operations': 'error',
      '@graphql-eslint/unique-operation-name': 'error',
    },
  },
];
```

---

## graphql-inspector (Breaking Change Detection)

Detect breaking schema changes before they reach production by diffing the current schema against the last published version in CI.

### Installation

```bash
npm install -D @graphql-inspector/cli
```

### CI check (`github-actions.yml`)

```yaml
- name: Check for breaking schema changes
  run: |
    npx graphql-inspector diff \
      'git:main:./src/schema/**/*.graphql' \
      './src/schema/**/*.graphql' \
      --fail-on-breaking
```

`--fail-on-breaking` exits with a non-zero code when any breaking change is detected, blocking the PR merge. Non-breaking changes (new fields, new types) are reported as informational.

### Annotating intentional breaking changes

If a breaking change is deliberate (e.g., removing a field after confirmed zero usage), document it explicitly in the PR and override the check:

```bash
# In a temporary CI override — requires PR approval
npx graphql-inspector diff ... --ignore-breaking
```

---

## Schema Registry (Apollo Rover CLI)

Use a schema registry to publish and validate schemas across services. Apollo Studio provides schema checks as a PR gate — comparing the proposed schema against active client operations tracked in production.

### Installation

```bash
npm install -g @apollo/rover
```

### Publishing the schema

```bash
rover graph publish my-graph@current \
  --schema ./src/schema.graphql \
  --name my-service
```

### Schema checks in CI

```yaml
- name: Run Apollo schema checks
  env:
    APOLLO_KEY: ${{ secrets.APOLLO_KEY }}
  run: |
    rover graph check my-graph@current \
      --schema ./src/schema.graphql \
      --query-count-threshold 1
```

Schema checks compare proposed changes against real client operations tracked in Apollo Studio. A check fails if any active operation would break under the proposed schema, even if `graphql-inspector` reports no breaking changes (because the check is against actual usage, not syntactic compatibility).

---

## Persisted Queries Toolchain

Persisted queries lock the server to a known set of operations, preventing arbitrary query submission in production.

### Generating the manifest

```bash
npm install -D @apollo/generate-persisted-query-manifest
npx generate-persisted-query-manifest
```

This scans all `.graphql` operation documents and outputs `persisted-query-manifest.json` with `operationId → body` mappings.

### Registering with the server

```typescript
import { createPersistedQueryManifestVerificationLink } from '@apollo/persisted-query-lists';
import manifest from './persisted-query-manifest.json';

// Apollo Server — reject operations not in the manifest
const server = new ApolloServer({
  schema,
  plugins: [
    ApolloServerPluginPersistedQueryManifest({ manifest }),
  ],
});
```

### Client (Automatic Persisted Queries — APQ)

For public APIs or third-party clients where a fixed manifest isn't feasible, use APQ instead. The client sends a hash; the server checks its cache before requesting the full query body.

```typescript
import { createPersistedQueryLink } from '@apollo/client/link/persisted-queries';
import { sha256 } from 'crypto-hash';

const link = createPersistedQueryLink({ sha256 }).concat(httpLink);
```

---

## Anti-Patterns

- Running `graphql-codegen` manually instead of as a watch task or CI step — generated types silently drift from the schema
- No `graphql-eslint` on schema files — naming violations and missing descriptions accumulate unremedied
- No breaking change detection in CI — clients break without warning on schema deployments
- Committing schema files but not generated types — reviewers cannot see the type impact of schema changes
- Using a schema registry without enabling schema checks — publishing without checking active operations defeats the purpose
- Registering persisted queries in development but not in production — the protection only matters in production
- Using `graphql-inspector diff` without `--fail-on-breaking` — detects changes but doesn't block the pipeline
