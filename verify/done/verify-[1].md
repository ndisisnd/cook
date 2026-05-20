---
status: completed
---

# Verification Run [1] — TypeScript Standards Compression + Dart Ref Gap Fix

## 1. What Was Changed

### TypeScript standards — full restructure

**Before:** 4 separate skill directories, each with their own `SKILL.md` and `refs/REFERENCE.md` stubs:
```
standards/typescript/
├── typescript-best-practices/   (P1 — code patterns)
├── typescript-language/         (P0 — type system)
├── typescript-security/         (P0 — security)
└── typescript-tooling/          (P1 — build/lint)
```
Each `REFERENCE.md` contained dead links to files that did not exist. Rules were duplicated across files (`no any`, `getDiagnostics`, mock typing).

**After:** Single skill directory following the dart exemplar:
```
standards/typescript/
├── SKILL.md                     (merged: P0 type correctness, P0 security, P1 conventions, P1 verification, anti-patterns)
└── refs/
    ├── tooling.md               (tsconfig, ESLint, Jest/Vitest, CI, pre-commit)
    ├── testing.md               (type-safe mocking, async mocks, test organisation, failure patterns)
    └── security.md              (Zod, JWT, secure cookies, middleware stack, RBAC, child process, ReDoS)
```

**`_INDEX.md` updated:** Now points to `standards/typescript/SKILL.md` as a single skill instead of routing to 4 separate skills.

### TypeScript SKILL.md — conditional ref loading added

The `## References` section was updated from a flat list to a conditional loading instruction:
```
Load only what the current task requires:
- [tooling](refs/tooling.md) — configuring tsconfig, ESLint, Jest, Vitest, build pipeline, or CI
- [testing](refs/testing.md) — writing, debugging, or reviewing tests
- [security](refs/security.md) — input validation, authentication, JWT, secrets, or API security
```

### Dart SKILL.md — same conditional ref loading gap fixed

`standards/dart/SKILL.md` previously listed refs with no loading conditions. Updated to:
```
Load only what the current task requires:
- [tooling](refs/tooling.md) — setting up or modifying analysis_options, dart format, DCM, build_runner, pubspec, coverage, CI, or pre-commit hooks
- [testing](refs/testing.md) — writing or reviewing unit tests, mocks (mocktail), stream tests, or fake_async time-dependent tests
```

### Online research incorporated and verified

All claims sourced from online research (TypeScript tsconfig docs, typescript-eslint, Jest docs, Vitest docs, OWASP, npm packages) were verified by a dedicated subagent against official sources. 15/16 confirmed; 1 corrected (JWT algorithm confusion attack wording softened — library defaults provide implicit mitigation, pinning `algorithms` is defense-in-depth, not a guaranteed fix).

### Post-verification fixes (Run [1])

Four issues found and applied in order of priority:

| Priority | File | Fix |
|---|---|---|
| P0 | `refs/security.md` | JWT `AuthService` changed from `RS256` to `HS256`. RS256 is asymmetric and requires PEM keys — using `process.env.JWT_SECRET` (a string) with RS256 throws a runtime key-parsing error. Added a note on when RS256 applies and what it requires. |
| P1 | `refs/testing.md` | Removed "Casting mocks directly `as SomeService` without `unknown` intermediary" from anti-patterns — duplicate of SKILL.md #8 "Unsafe mock casts". Body of the file still demonstrates the correct pattern. |
| P1 | `refs/security.md` | Removed "`child_process.exec()` or `spawn({ shell: true })` with any dynamic content" from anti-patterns — duplicate of SKILL.md #13 "Shell string interpolation with user input". Child Process Safety section covers the risk in full. |
| P2 | `refs/tooling.md` | Removed "Exact dependency version pins without a comment" from anti-patterns — general package management convention, not TypeScript-tooling-specific. |

---

## 2. Expected Output When Running the Skill

When a coding agent loads the TypeScript standard and uses the conditional ref instructions correctly:

### Scenario A — Writing a TypeScript class with DI
- Loads: `typescript/SKILL.md` only
- Does NOT load any ref (no tooling, testing, or security task)
- Applies: naming conventions, class modifiers, constructor injection, `async/await`, type annotations

### Scenario B — Configuring tsconfig or ESLint
- Loads: `typescript/SKILL.md` + `refs/tooling.md`
- Does NOT load: `testing.md`, `security.md`
- Applies: full tsconfig with companion flags beyond `strict: true`, ESLint flat config with strict-tier rules, build tool guidance

### Scenario C — Writing tests
- Loads: `typescript/SKILL.md` + `refs/testing.md`
- Does NOT load: `tooling.md`, `security.md`
- Applies: `satisfies jest.Mocked<T>`, `mockResolvedValue`, test organisation, failure pattern fixes

### Scenario D — Writing an auth endpoint or input validation
- Loads: `typescript/SKILL.md` + `refs/security.md`
- Does NOT load: `tooling.md`, `testing.md`
- Applies: Zod `safeParse` route handler, JWT `AuthService` with algorithm pinning, `hpp` + body limit + helmet middleware stack, RBAC

---

## 3. Success Criteria

### Structure
- [ ] `standards/typescript/SKILL.md` exists and is non-empty
- [ ] `standards/typescript/refs/tooling.md` exists
- [ ] `standards/typescript/refs/testing.md` exists
- [ ] `standards/typescript/refs/security.md` exists
- [ ] `standards/typescript/refs/types.md` does NOT exist (decided against it; content is inline in SKILL.md)
- [ ] The 4 old subdirectories (`typescript-best-practices`, `typescript-language`, `typescript-security`, `typescript-tooling`) do NOT exist
- [ ] `standards/typescript/_INDEX.md` references a single skill (`typescript`) not four

### Content — SKILL.md
- [ ] Contains a P0 — Type Correctness section covering: type annotations, interfaces vs types, strict mode, enums, generics, type guards, utility types, immutability, discriminated unions, branded types, exhaustiveness
- [ ] Contains a P0 — Security section covering: input validation (Zod/Joi), injection/XSS, authentication (Argon2id, JWT, CORS), secrets
- [ ] Contains a P1 — Code Conventions section covering: naming, functions, modules, async, classes, optional chaining
- [ ] Contains a P1 — Verification section with the getDiagnostics → tsc --noEmit → eslint --fix workflow
- [ ] Contains a consolidated Anti-Patterns list (15 items, no duplicates)
- [ ] References section uses conditional loading language ("Load only what the current task requires")

### Content — Refs
- [ ] `tooling.md` contains: tsconfig JSON with companion flags beyond `strict`, ESLint flat config, build tool table, Jest config with ts-jest, Vitest config with `mergeConfig`, CI YAML, pre-commit hooks
- [ ] `testing.md` contains: `satisfies jest.Mocked<T>` pattern, async mock APIs, common failure patterns, test organisation rules
- [ ] `security.md` contains: Zod route handler, JWT AuthService, secure cookie options, middleware stack (helmet + hpp + body limit), RBAC, child process safety (`execFile`), ReDoS guidance

### No duplication
- [ ] SKILL.md anti-patterns do not appear in ref anti-patterns (spot-check: `origin: '*'`, `@ts-ignore`, `plaintext secrets`, `getDiagnostics` workflow)
- [ ] "Unsafe mock casts" does NOT appear in `testing.md` anti-patterns (fixed P1)
- [ ] "Shell string interpolation" / `child_process.exec()` does NOT appear in `security.md` anti-patterns (fixed P1)
- [ ] No ref repeats another ref's content (tooling ≠ testing ≠ security)

### Dart fix
- [ ] `standards/dart/SKILL.md` References section contains "Load only what the current task requires"
- [ ] Each dart ref has a task-based condition, not just a filename

### Accuracy (spot-check key online-sourced claims)
- [ ] tsconfig: `strict: true` does not include `noUnusedLocals`, `noUnusedParameters`, `noImplicitReturns`, `noFallthroughCasesInSwitch`
- [ ] `@typescript-eslint/no-floating-promises`, `no-misused-promises`, `switch-exhaustiveness-check` are real rules
- [ ] ts-jest type-checks during test runs; Babel-only does not
- [ ] `child_process.exec()` invokes `/bin/sh`; `execFile()` does not
- [ ] `hpp` and `vuln-regex-detector` are real npm packages
