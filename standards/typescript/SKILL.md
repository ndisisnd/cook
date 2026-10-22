---
name: typescript
description: TypeScript 6.x language standards (7.x-compatible) for type safety, narrowing, generics, modules, and async code. Use for TypeScript implementation or review work; load refs only for tooling, testing, or security-specific tasks.
metadata:
  targets: "TypeScript 6.x (code must also compile on 7.x) · Node.js 24 LTS"
  last_reviewed: 2026-10-18
  triggers:
    files:
      - '**/*.ts'
      - '**/*.tsx'
      - 'tsconfig.json'
      - 'eslint.config.*'
      - 'jest.config.*'
      - 'vitest.config.*'
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

Target: TypeScript 6.x; avoid anything TypeScript 7.0 removed (every 6.0 deprecation is a hard error in 7.0).

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
- TypeScript 6.0 defaults `strict` to `true`. Keep it on; never set `"strict": false` in a new project.
- Existing repo that upgrades from 5.x without strict: set `"strict": false` explicitly, then enable sub-flags one at a time (`strictNullChecks` → `noImplicitAny` → `strictFunctionTypes`) before removing the override.
- Avoid non-null assertion (`!`). Use narrowing (`typeof`, `instanceof`, if-checks) instead.

### Erasable Syntax Only
- Write only syntax that type stripping can erase: no `enum`, no `namespace` with runtime code, no constructor parameter properties, no `import x = require()`. Node.js type stripping and `erasableSyntaxOnly` reject these.
- Use literal unions or `as const` objects instead of `enum`:

```typescript
export const Status = { Active: 'active', Disabled: 'disabled' } as const;
export type Status = (typeof Status)[keyof typeof Status];
```

### Generics, Guards, Utility Types
- Constrain generics with `extends` where appropriate.
- Narrow with `typeof`, `instanceof`, and predicate functions (`x is T`).
- Prefer built-in utility types (`Partial`, `Required`, `Pick`, `Omit`, `Record`, `Readonly`, `NonNullable`).
- Prefer `satisfies` for object literals that must conform to a contract without widening the inferred type.

### Immutability
- `readonly` on arrays and object properties. Use `as const` and `satisfies` for const assertions.

### Unions And Brands
- Use a stable discriminant such as `kind` or `type` to narrow safely. Switch on the discriminant.
- Use `never` in switch `default` to catch unhandled union members at compile time.
- Use brands only when structurally identical values such as IDs or units are easy to mix up across boundaries.

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

- Arrow functions for callbacks and inline logic. Function declarations for top-level exports.
- Prefer named exports unless a framework or file convention requires a default export.
- `import type` for types. With `verbatimModuleSyntax` on, a type-only import without `type` is a compile error.
- Prefer `async/await`. Use `Promise.all()` only for independent work that can safely run in parallel.
- `try/catch` with `catch (e: unknown)` — narrow before use. Avoid `.then().catch()` chains.
- Explicit visibility when it protects internal state or materially improves readability. Avoid redundant `public` churn unless the repo standard requires it.
- Favor composition over inheritance. Constructor injection with interfaces — not singletons. Declare fields explicitly; do not use constructor parameter properties.
- `?.` and `??` over manual null checks.

---

## Priority: P1 — Verification

After editing any `.ts`/`.tsx` file:

1. Use TypeScript diagnostics from the editor, LSP, or MCP tooling when available.
2. Run the repo's typecheck command (`tsc --noEmit`, `pnpm typecheck`, or equivalent).
3. Run the repo's lint and test commands for the changed surface. Use auto-fix only when the repo already expects it.


---

## Anti-Patterns

- `require()` in TypeScript source — use `import`
- Empty interfaces — use `type` or a non-empty interface
- Unsafe mock casts — use `vi.mocked()` / `jest.Mocked<T>` or `as unknown as T`
- `@ts-ignore` — use `@ts-expect-error` (self-documents intent; fails if the error disappears)
- Global `eslint-disable` — suppress per-line; fix root cause
- A one-step strict flip on a large legacy repo
- `eval`, `Function` constructor, or string literals as timer callbacks

---

## References

Load only what the current task requires:

- [tooling](refs/tooling.md) — configuring tsconfig, ESLint, Vitest, Jest, build pipeline, or CI
- [testing](refs/testing.md) — writing, debugging, or reviewing tests
- [security](refs/security.md) — input validation, authentication, JWT, secrets, or API security

Do not load refs for ordinary type-shape, refactor, or local implementation tasks.
