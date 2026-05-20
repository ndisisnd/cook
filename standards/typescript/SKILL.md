---
name: typescript
description: TypeScript 5.x language standards for type safety, narrowing, generics, modules, and async code. Use for TypeScript implementation or review work; load refs only for tooling, testing, or security-specific tasks.
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

Default load: this file only. Pull `refs/tooling.md`, `refs/testing.md`, or `refs/security.md` only when the task explicitly needs that depth.

## Priority: P0 — Type Correctness

### Type Annotations
- Explicit params and return types on all public declarations. Infer locals.
- Avoid `any`. Prefer `unknown`, generics, or a narrowly-scoped escape hatch with a comment when interop forces it.
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
- Prefer `satisfies` for object literals that must conform to a contract without widening the inferred type.

### Immutability
- `readonly` on arrays and object properties. Use `as const` and `satisfies` for const assertions.

### Discriminated Unions
- Use a stable discriminant such as `kind` or `type` to narrow safely. Switch on the discriminant.

```typescript
type Result<T> = { kind: 'ok'; data: T } | { kind: 'err'; error: Error };
```

### Branded Types
- Use brands only when structurally identical values such as IDs or units are easy to mix up across boundaries.

```typescript
type UserId = string & { readonly __brand: 'UserId' };
function createUserId(id: string): UserId { return id as UserId; }
```

### Exhaustiveness
- Use `never` in switch `default` to catch unhandled union members at compile time.

---

## Priority: P0 — Boundary Safety

### External Data
- Treat data from I/O boundaries as untrusted until it is parsed, validated, and narrowed.
- Prefer schema-based validation at API and persistence boundaries when the project already uses a validator. Load `refs/security.md` for concrete API/auth guidance.

### Dangerous Sinks
- Never interpolate untrusted input into SQL, shell commands, HTML, filesystem paths, or externally-sourced URLs.
- Use parameterized queries, safe child-process APIs, output sanitization, and origin allowlists where the sink requires them.

### Secrets
- Never hardcode secrets, tokens, or credentials in source.
- Never log secrets or raw auth tokens.

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
- Prefer named exports unless a framework or file convention requires a default export.
- `import type` for interfaces and types — zero runtime overhead.
- Keep import grouping consistent with the repo. Load `refs/tooling.md` when changing lint enforcement.

### Async
- Prefer `async/await`. Use `Promise.all()` only for independent work that can safely run in parallel.
- `try/catch` with `catch (e: unknown)` — narrow before use. Avoid `.then().catch()` chains.

### Classes
- Use explicit visibility when it protects internal state or materially improves readability. Avoid redundant `public` churn unless the repo standard requires it.
- Favor composition over inheritance. Constructor injection with interfaces — not singletons.

### Optional Chaining
- `?.` and `??` over manual null checks.

---

## Priority: P1 — Verification

After editing any `.ts`/`.tsx` file:

1. Use TypeScript diagnostics from the editor, LSP, or MCP tooling when available.
2. Run the repo's typecheck command (`tsc --noEmit`, `pnpm typecheck`, or equivalent).
3. Run the repo's lint and test commands for the changed surface. Use auto-fix only when the repo already expects it.

> Fallback when no LSP tooling is configured: run the repo's typecheck command directly.

Inspect inferred types before adding annotations that may fight the compiler. Check references before large renames or signature changes.

---

## Anti-Patterns

- Broad `any` usage when `unknown`, generics, or a local escape hatch would work
- `Function` type — use a typed signature `() => void`
- Runtime `enum` — use literal unions or `as const`
- Non-null assertion `!` — use narrowing
- Default exports where the framework or file convention does not require them
- `require()` — use ES6 `import`
- Empty interfaces — use `type` or a non-empty interface
- Unsafe mock casts — use `jest.Mocked<T>` or `as unknown as T`
- `@ts-ignore` — use `@ts-expect-error` (self-documents intent; fails if the error disappears)
- Global `eslint-disable` — suppress per-line; fix root cause
- Atomic `strict: true` flip on an existing repo — migrate incrementally starting with `strictNullChecks`
- `eval`, `Function` constructor, or string literals as timer callbacks
- Shell string interpolation with untrusted input (`execSync(\`cmd ${userInput}\`)`)
- Unvalidated externally-sourced URLs passed to network or redirect APIs
- Plaintext secrets in code, tests, fixtures, or Git

---

## References

Load only what the current task requires:

- [tooling](refs/tooling.md) — configuring tsconfig, ESLint, Jest, Vitest, build pipeline, or CI
- [testing](refs/testing.md) — writing, debugging, or reviewing tests
- [security](refs/security.md) — input validation, authentication, JWT, secrets, or API security

Do not load refs for ordinary type-shape, refactor, or local implementation tasks.
