---
name: typescript
description: TypeScript 5.x language standards, code conventions, and security. Use when writing or reviewing any TypeScript code — type safety, generics, classes, async, modules, input validation, and authentication.
metadata:
  triggers:
    files:
      - '**/*.ts'
      - '**/*.tsx'
      - 'tsconfig.json'
      - '.eslintrc.*'
      - 'jest.config.*'
    keywords:
      - type
      - interface
      - generic
      - enum
      - union
      - readonly
      - async
      - import
      - export
      - validate
      - sanitize
      - auth
      - token
      - secret
      - eslint
      - jest
      - vitest
---

# TypeScript Standards

## Priority: P0 — Type Correctness

### Type Annotations
- Explicit params and return types on all public declarations. Infer locals.
- Never use `any`. Use `unknown` or a specific type.
- Never use the `Function` type. Use a typed signature: `() => void`.

### Interfaces vs Types
- `interface` for object shapes that describe APIs — supports declaration merging.
- `type` for unions, intersections, mapped types, and conditional types.

### Strict Mode
- `strict: true` in tsconfig. On existing repos, migrate incrementally: `strictNullChecks` → `noImplicitAny` → `strictFunctionTypes`. Never flip `strict: true` in one step.
- Avoid non-null assertion (`!`). Use narrowing (`typeof`, `instanceof`, if-checks) instead.
- `?.` and `??` for null safety — use narrowing, not `!`.

### Enums
- Literal unions or `as const` objects. No runtime `enum`.

### Generics
- Use generics for reusable, type-safe code. Constrain with `extends` where appropriate.

### Type Guards
- Use `typeof`, `instanceof`, and predicate functions (`x is T`) to narrow types.

### Utility Types
- Prefer built-ins: `Partial`, `Required`, `Pick`, `Omit`, `Record`, `Readonly`, `NonNullable`.

### Immutability
- `readonly` on arrays and object properties. Use `as const` and `satisfies` for const assertions.

### Discriminated Unions
- Use a literal `kind` property to narrow type safely. Switch on the discriminant.

```typescript
type Result<T> = { kind: 'ok'; data: T } | { kind: 'err'; error: Error };
```

### Branded Types
- Use brands to prevent mixing structurally identical types at compile time.

```typescript
type UserId = string & { readonly __brand: 'UserId' };
function createUserId(id: string): UserId { return id as UserId; }
```

### Exhaustiveness
- Use `never` in switch `default` to catch unhandled union members at compile time.

---

## Priority: P0 — Security

### Input Validation
- Use `Zod`, `Joi`, or `class-validator` at every API boundary. Always parse and validate user-controlled input before use.
- Use `safeParse` for error handling without throwing. Return `400` with structured errors on failure.

### Injection and XSS
- **SQL**: Parameterized queries (`pool.query('... WHERE id = $1', [id])`) or type-safe ORMs (Prisma, TypeORM). Use `Prisma.sql` for raw queries.
- **XSS**: `DOMPurify` for HTML sanitization.
- **Command injection**: Never interpolate user input or env vars into `execSync`/`spawnSync` strings. Use `execFileSync('git', ['arg1', arg2])` — static command, separate args array.
- **SSRF**: Validate URL origins against an allowlist before calling `fetch()`/`axios` with any externally-sourced URL.

### Authentication
- `Argon2id` for password hashing. JWT via `jsonwebtoken` or `jose` with `HttpOnly`/`Secure` cookies. Use `RS256` for public/private key pairs. Implement refresh token rotation.
- CORS: strict origin whitelisting — never `origin: '*'`.
- Encryption: Node.js `crypto` or Web Crypto API. Avoid MD5 and SHA1.

### Secrets
- `.env` files or a secret manager. Never commit secrets to Git.

---

## Priority: P1 — Code Conventions

### Naming
- `PascalCase`: classes, types, interfaces.
- `camelCase`: variables, functions, methods.
- `UPPER_SNAKE_CASE`: static constants only.

### Functions
- Arrow functions for callbacks and inline logic. Function declarations for top-level exports.
- Always type return values on public API functions.

### Modules
- Named exports only — enables better refactoring and auto-imports.
- `import type` for interfaces and types — zero runtime overhead.
- Import order: external packages → internal modules → relative imports. Enforce via `eslint-plugin-import`.

### Async
- `async/await` with `Promise.all()` for parallel execution.
- `try/catch` with `catch (e: unknown)` — narrow before use. Avoid `.then().catch()` chains.

### Classes
- Explicit `private`, `protected`, and `public` modifiers on every member.
- Favor composition over inheritance. Constructor injection with interfaces — not singletons.

### Optional Chaining
- `?.` and `??` over manual null checks.

---

## Priority: P1 — Verification

After editing any `.ts`/`.tsx` file:

1. Call `getDiagnostics` (typescript-lsp MCP tool) — surfaces type errors in real time.
2. Run `tsc --noEmit` in CI — catches project-wide errors LSP may miss.
3. Run `eslint --fix` — auto-fix formatting and lint violations.

> Fallback when typescript-lsp is unconfigured: run `tsc --noEmit` directly.

Use `getHover` to inspect inferred types. Use `getReferences` before renaming symbols.

---

## Anti-Patterns

- `any` — use `unknown` or a specific type
- `Function` type — use a typed signature `() => void`
- Runtime `enum` — use literal unions or `as const`
- Non-null assertion `!` — use narrowing
- Default exports — use named exports
- `require()` — use ES6 `import`
- Empty interfaces — use `type` or a non-empty interface
- Unsafe mock casts — use `jest.Mocked<T>` or `as unknown as T`
- `@ts-ignore` — use `@ts-expect-error` (self-documents intent; fails if the error disappears)
- Global `eslint-disable` — suppress per-line; fix root cause
- Atomic `strict: true` flip on an existing repo — migrate incrementally starting with `strictNullChecks`
- `eval`, `Function` constructor, or string literals as timer callbacks
- Shell string interpolation with user input (`execSync(\`cmd ${userInput}\`)`)
- Unvalidated externally-sourced URLs passed to `fetch()`/`axios`
- Plaintext secrets in code or Git

---

## References

Load only what the current task requires:

- [tooling](refs/tooling.md) — configuring tsconfig, ESLint, Jest, Vitest, build pipeline, or CI
- [testing](refs/testing.md) — writing, debugging, or reviewing tests
- [security](refs/security.md) — input validation, authentication, JWT, secrets, or API security
