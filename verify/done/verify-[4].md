---
status: completed
---

# Verification Run [4] — TypeScript Skill Leaning + Conditional Ref Discipline

## 1. What Was Changed

### `standards/typescript/SKILL.md` — default load made leaner

**Problem before:** The main TypeScript skill mixed three layers into the default load:
- core TypeScript language rules
- detailed backend/auth/security guidance
- tool-specific verification commands

That made ordinary TypeScript runs heavier than necessary and reduced the value of the conditional refs.

**After:** The main skill is now biased toward language-level reasoning and pushes deeper detail to refs only when needed.

### Description rewritten

Frontmatter description changed from a broad "code conventions and security" summary to a narrower language-first description:

- focus on type safety, narrowing, generics, modules, and async code
- explicitly states that refs should be loaded only for tooling, testing, or security-specific tasks

This should improve trigger quality and reduce unnecessary detail in ordinary runs.

### Explicit default-load rule added

The top of `standards/typescript/SKILL.md` now states:

- load this file by default
- pull `refs/tooling.md`, `refs/testing.md`, or `refs/security.md` only when the task explicitly needs that depth

This makes the intended token discipline visible inside the skill itself, not only in repository-level routing docs.

### Type correctness guidance made more intelligent

The P0 language section was kept, but several rules were sharpened:

- **`any`** is no longer treated as an absolute ban; it is now discouraged in favor of `unknown`, generics, or a narrow documented escape hatch for interop
- **`satisfies`** is now explicitly recommended for object literals that must conform without widening inference
- **discriminated unions** now refer to a stable discriminant such as `kind` or `type`, not only `kind`
- **branded types** are now framed as situational for IDs/units, not as a default pattern everywhere

This keeps strong TypeScript guidance while avoiding cargo-cult rules.

### Inline security payload reduced to boundary-safety rules

The previous `P0 — Security` section was replaced with a smaller `P0 — Boundary Safety` section.

**Removed from default load:**
- concrete validator recommendations (`Zod`, `Joi`, `class-validator`)
- SQL/XSS/SSRF/API examples
- JWT/Argon2id/CORS/encryption implementation detail

**Kept in default load as universal principles:**
- external data is untrusted until parsed, validated, and narrowed
- dangerous sinks must not receive untrusted input
- secrets must not be hardcoded or logged

**Why:** this information still exists in `refs/security.md`, but no longer taxes every TypeScript run that is only about typing, refactoring, or local implementation.

### Conventions made repo-aware instead of rigid

Several P1 rules were softened so the skill adapts to real repositories better:

- **exports**: from "named exports only" to "prefer named exports unless framework/file convention requires default export"
- **imports**: from a mandatory `eslint-plugin-import` formulation to "keep grouping consistent with the repo" and load tooling ref when needed
- **async**: `Promise.all()` is now scoped to independent work that can safely run in parallel
- **class visibility**: from requiring explicit modifiers on every member to using explicit visibility where it materially helps

This should make the skill smarter during framework-specific work and reduce unnecessary churn in edits.

### Verification workflow generalized

The verification section previously assumed a specific TypeScript MCP + exact commands:

- `getDiagnostics`
- `tsc --noEmit`
- `eslint --fix`

It now instructs the agent to:

- use TypeScript diagnostics from editor, LSP, or MCP tooling when available
- run the repo's typecheck command (`tsc --noEmit`, `pnpm typecheck`, or equivalent)
- run the repo's lint and test commands for the changed surface

This preserves rigor while making the skill portable across repos.

### Anti-patterns updated to match the smarter rules

The anti-pattern list was updated to align with the new positioning:

- `any` -> broad `any` usage
- default exports -> only when framework/file convention does not require them
- shell interpolation wording changed from "user input" to broader "untrusted input"
- URL rule expanded from `fetch()`/`axios` to network or redirect APIs
- plaintext secrets widened to code, tests, fixtures, or Git

### References section strengthened

The references section still points to the same three refs:

- `refs/tooling.md`
- `refs/testing.md`
- `refs/security.md`

New instruction added:

- do **not** load refs for ordinary type-shape, refactor, or local implementation tasks

This is the key token-efficiency guardrail added in this change.

---

## 2. Files Touched

| File | Action |
|---|---|
| `standards/typescript/SKILL.md` | Edit — narrowed default scope, reduced inline security detail, softened rigid conventions, generalized verification workflow, strengthened conditional ref guidance |

No changes were made to:

- `standards/typescript/_INDEX.md`
- `standards/typescript/refs/tooling.md`
- `standards/typescript/refs/testing.md`
- `standards/typescript/refs/security.md`

---

## 3. Expected Output When Running the Skill

When an agent loads the TypeScript standard correctly after this change:

### Scenario A — Local refactor or typing-only work
- Loads: `standards/typescript/SKILL.md` only
- Applies: type annotations, narrowing, unions, generics, `satisfies`, exhaustiveness, module/async/class guidance
- Does NOT load: `tooling.md`, `testing.md`, `security.md`

### Scenario B — tsconfig / ESLint / build pipeline work
- Loads: `standards/typescript/SKILL.md` + `refs/tooling.md`
- Applies: main language rules plus tsconfig, ESLint, CI, Jest/Vitest, build-tool guidance
- Does NOT load: `testing.md`, `security.md` unless the task explicitly also needs them

### Scenario C — Writing or reviewing tests
- Loads: `standards/typescript/SKILL.md` + `refs/testing.md`
- Applies: main language rules plus typed mocks, async mocking, test organization, failure-pattern guidance
- Does NOT load: `tooling.md`, `security.md` unless the task explicitly also needs them

### Scenario D — Auth, input validation, or API security work
- Loads: `standards/typescript/SKILL.md` + `refs/security.md`
- Applies: main language rules plus validator, JWT, cookie, middleware, RBAC, child-process, and ReDoS guidance
- Does NOT load: `tooling.md`, `testing.md` unless the task explicitly also needs them

---

## 4. Success Criteria

### Structure
- [x] `verify/done/verify-[4].md` exists
- [x] `standards/typescript/SKILL.md` exists and is non-empty
- [x] `standards/typescript/refs/tooling.md` still exists
- [x] `standards/typescript/refs/testing.md` still exists
- [x] `standards/typescript/refs/security.md` still exists

### Content — Description and load behavior
- [x] `standards/typescript/SKILL.md` description is language-first, not a broad security/tooling summary
- [x] The file contains an explicit default-load sentence near the top
- [x] The refs section still uses conditional loading language
- [x] The refs section includes the instruction not to load refs for ordinary type-shape, refactor, or local implementation tasks

### Content — Type correctness improvements
- [x] The `Type Annotations` section says to avoid `any`, not that `any` is categorically forbidden
- [x] The `Utility Types` section explicitly mentions `satisfies`
- [x] The `Discriminated Unions` section allows `kind` or `type` as the discriminant
- [x] The `Branded Types` section frames brands as situational, not universal

### Content — Boundary safety reduction
- [x] The old `P0 — Security` heading no longer exists in `standards/typescript/SKILL.md`
- [x] A `P0 — Boundary Safety` section exists instead
- [x] The main skill now contains only summary guidance about untrusted external data, dangerous sinks, and secrets
- [x] Detailed auth/API/security implementation guidance remains in `refs/security.md`, not inline in the main skill

### Content — Smarter conventions
- [x] The `Modules` section says to prefer named exports unless conventions require default export
- [x] The `Modules` section no longer mandates `eslint-plugin-import` inline
- [x] The `Async` section limits `Promise.all()` to independent safe parallel work
- [x] The `Classes` section no longer requires explicit `public` on every member

### Content — Verification portability
- [x] The verification section no longer depends on `getDiagnostics` wording as the only path
- [x] The verification section refers to the repo's typecheck command, not only `tsc --noEmit`
- [x] The verification section tells the agent to run repo lint and test commands for the changed surface

### Content — Anti-pattern alignment
- [x] Anti-patterns mention broad `any` usage rather than blanket `any`
- [x] Anti-patterns mention default exports only when conventions do not require them
- [x] Anti-patterns mention shell interpolation with untrusted input
- [x] Anti-patterns mention unvalidated URLs passed to network or redirect APIs
- [x] Anti-patterns mention plaintext secrets in code, tests, fixtures, or Git

### No unintended scope expansion
- [x] `standards/typescript/_INDEX.md` was not changed by this run
- [x] `refs/tooling.md`, `refs/testing.md`, and `refs/security.md` were not modified by this run
- [x] The main change is a leaner default skill load, not additional ref content

---

## 5. Verification Notes for Another Agent

Recommended verification steps:

1. Read `standards/typescript/SKILL.md` top-to-bottom and confirm the default load is now language-first.
2. Compare the current `Boundary Safety` section against the deeper content in `refs/security.md` and confirm the detail has been pushed down, not deleted.
3. Confirm that ordinary TypeScript work can now be handled from `SKILL.md` alone without needing any ref.
4. Confirm that tooling, testing, and security work still have concrete depth available through the existing refs.
5. Confirm that no other TypeScript files changed in this run.
