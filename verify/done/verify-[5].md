---
status: completed
---

# Verification Run [5] — React Skill Consolidation

## 1. What Was Changed

### Problem before

The React standard was spread across 8 separate sub-skills, each with its own `SKILL.md` and refs:

- `react-component-patterns/`
- `react-hooks/`
- `react-performance/`
- `react-security/`
- `react-state-management/`
- `react-testing/`
- `react-tooling/`
- `react-typescript/`

This meant a router had to load multiple skill files for ordinary React work, TypeScript typing was in its own isolated skill, and hook correctness rules were separated from the component basics they apply to.

### After

A single `standards/react/SKILL.md` covers hook correctness, component basics, boundary safety, TypeScript patterns, and style conventions. Six refs are loaded conditionally by task type. The structure matches the dart/graphql exemplar exactly.

### `standards/react/SKILL.md` — new single skill

**P0 — Hook Correctness** (merged from `react-hooks/SKILL.md`)
- Exhaustive dependency arrays, no linter suppression
- Objects/arrays must be memoized before entering dependency arrays
- `useEffect` for external system sync only, with cleanup
- No conditional hook calls
- No derived-state via `useEffect`
- Lazy state initialization
- `useMemo`/`useCallback` only after measuring
- `useRef` for mutable non-render values
- `useTransition`/`useDeferredValue` for non-blocking updates

**P0 — Component Basics** (merged from `react-component-patterns/SKILL.md`)
- Function components only, no classes
- Named exports, PascalCase, one per file, under ~250 lines
- No nested definitions, stable list keys, ternary over `&&`
- No prop drilling beyond two levels

**P0 — Boundary Safety** (merged from `react-security/SKILL.md` — summary only)
- No `dangerouslySetInnerHTML` without DOMPurify
- No tokens/secrets in `localStorage`
- No `javascript:` URIs

**P1 — TypeScript** (merged from `react-typescript/SKILL.md`, inline — no separate ref)
- `interface`/`type` for props, not `React.FC`
- `ReactNode` for children
- Specific event handler types
- Typed refs and state generics
- `ComponentPropsWithoutRef` for native element extension
- Generic components, discriminated unions, utility types
- No `any`

**P1 — Conventions**
- Custom hooks start with `use`
- Naming conventions for components, hooks, boolean props
- No direct state mutation
- Static objects/JSX extracted outside component scope

**Anti-patterns** — consolidated from all 8 sub-skills

**References** — 6 conditional refs with load trigger descriptions

### `standards/react/_INDEX.md` — rewritten

Old: split routing across sub-skill folders by file pattern and keyword match.
New: single skill with ref routing table, loading instructions, and deprecation notice for the old sub-skill folders.

### `standards/react/refs/` — 6 new ref files

| File | Source content |
|---|---|
| `component-patterns.md` | `react-component-patterns/refs/patterns.md` + `refs/REFERENCE.md` |
| `state-management.md` | `react-state-management/refs/REFERENCE.md` |
| `performance.md` | `react-performance/SKILL.md` + `refs/REFERENCE.md` |
| `testing.md` | `react-testing/SKILL.md` + `refs/REFERENCE.md` |
| `security.md` | `react-security/refs/REFERENCE.md` |
| `tooling.md` | `react-tooling/SKILL.md` + `refs/example.md` |

---

## 2. Files Touched

| File | Action |
|---|---|
| `standards/react/SKILL.md` | Created — single unified skill |
| `standards/react/_INDEX.md` | Rewritten — single-skill routing table |
| `standards/react/refs/component-patterns.md` | Created |
| `standards/react/refs/state-management.md` | Created |
| `standards/react/refs/performance.md` | Created |
| `standards/react/refs/testing.md` | Created |
| `standards/react/refs/security.md` | Created |
| `standards/react/refs/tooling.md` | Created |

Old sub-skill folders left in place (pending deletion decision):
- `react-component-patterns/`, `react-hooks/`, `react-performance/`, `react-security/`, `react-state-management/`, `react-testing/`, `react-tooling/`, `react-typescript/`

---

## 3. Expected Output When Running the Skill

### Scenario A — Ordinary component or hook work
- Loads: `SKILL.md` only
- Applies: hook dependency rules, component structure, TypeScript typing patterns, boundary safety

### Scenario B — Designing a reusable component API
- Loads: `SKILL.md` + `refs/component-patterns.md`
- Applies: composition, compound components, HOC, render props, controlled vs uncontrolled, polymorphic `as`

### Scenario C — State architecture decision
- Loads: `SKILL.md` + `refs/state-management.md`
- Applies: tool selection table, Context split pattern, Zustand, Redux Toolkit, TanStack Query, URL state

### Scenario D — Performance investigation
- Loads: `SKILL.md` + `refs/performance.md`
- Applies: parallel fetch, Suspense streaming, lazy loading, bundle analysis, virtualization, Web Workers

### Scenario E — Writing tests
- Loads: `SKILL.md` + `refs/testing.md`
- Applies: RTL/Vitest, userEvent, MSW, context/router wrapping, axe accessibility checks

### Scenario F — Auth, XSS, or CSP work
- Loads: `SKILL.md` + `refs/security.md`
- Applies: DOMPurify, HttpOnly cookies, CSRF tokens, CSP headers, SSR serialization escaping

### Scenario G — Build config, DevTools, bundle analysis
- Loads: `SKILL.md` + `refs/tooling.md`
- Applies: Vite config, StrictMode, why-did-you-render, Profiler API, bundle visualizer, ESLint setup

---

## 4. Success Criteria

### Structure
- [ ] `standards/react/SKILL.md` exists and is non-empty
- [ ] `standards/react/_INDEX.md` exists and references the single skill
- [ ] `standards/react/refs/component-patterns.md` exists
- [ ] `standards/react/refs/state-management.md` exists
- [ ] `standards/react/refs/performance.md` exists
- [ ] `standards/react/refs/testing.md` exists
- [ ] `standards/react/refs/security.md` exists
- [ ] `standards/react/refs/tooling.md` exists

### SKILL.md content — P0 hook correctness
- [ ] Contains exhaustive-deps rule and explanation of why objects/arrays cause loops
- [ ] States that `useEffect` is for external system sync only
- [ ] Contains cleanup requirement (subscriptions, timers, AbortController)
- [ ] States no conditional hook calls
- [ ] States no `useEffect` to sync derived state

### SKILL.md content — P0 component basics
- [ ] Function components only, no classes
- [ ] Named exports, PascalCase, one per file
- [ ] No nested component definitions
- [ ] Stable list keys (no array index)
- [ ] Ternary over `&&` for conditional rendering

### SKILL.md content — P0 boundary safety
- [ ] `dangerouslySetInnerHTML` requires DOMPurify
- [ ] Tokens must not go in `localStorage`
- [ ] No `javascript:` URIs

### SKILL.md content — P1 TypeScript (inline, no separate ref)
- [ ] Props typed with `interface` or `type`, not `React.FC`
- [ ] `ReactNode` for children
- [ ] Specific event handler types mentioned
- [ ] `useRef` nullability rule for DOM refs
- [ ] `ComponentPropsWithoutRef` for native element extension
- [ ] Generic components pattern
- [ ] Discriminated unions mentioned
- [ ] No `any` rule

### SKILL.md content — References section
- [ ] Lists exactly 6 refs with conditional load descriptions
- [ ] No `typescript.md` ref (TypeScript is inline)
- [ ] Each ref entry describes the trigger condition

### _INDEX.md content
- [ ] References `SKILL.md` as the single skill (not sub-skill folders)
- [ ] Has a loading instructions section
- [ ] Lists the 8 old sub-skill folders as deprecated

### Ref files — component-patterns.md
- [ ] Covers composition/slot pattern
- [ ] Covers compound components with context
- [ ] Covers render props
- [ ] Covers HOC with auth guard example
- [ ] Covers controlled vs uncontrolled with guidance on when to use each
- [ ] Covers polymorphic `as` prop

### Ref files — state-management.md
- [ ] Has a tool selection table
- [ ] Covers Context with split State/Dispatch pattern
- [ ] Covers Zustand with slice subscription example
- [ ] Covers Redux Toolkit with createSlice
- [ ] Covers TanStack Query with useQuery and useMutation
- [ ] Covers URL state with useSearchParams

### Ref files — performance.md
- [ ] Covers parallel fetch with Promise.all
- [ ] Covers Suspense streaming
- [ ] Covers lazy loading with React.lazy
- [ ] Covers bundle analysis commands
- [ ] Covers list virtualization
- [ ] Covers startTransition
- [ ] Covers Web Workers

### Ref files — testing.md
- [ ] Uses userEvent, not fireEvent
- [ ] Uses MSW for network mocking with v2 API (`http`, `HttpResponse`)
- [ ] Shows how to test context providers
- [ ] Shows how to test with React Router
- [ ] Shows findBy vs waitFor distinction
- [ ] Includes accessibility check with jest-axe

### Ref files — security.md
- [ ] DOMPurify sanitization example
- [ ] URL protocol validation for safe links
- [ ] HttpOnly cookie setup (server-side)
- [ ] Auth context that never holds the token
- [ ] CSRF token pattern
- [ ] CSP header configuration
- [ ] SSR serialization escaping

### Ref files — tooling.md
- [ ] Vite config example
- [ ] StrictMode setup in main.tsx
- [ ] why-did-you-render setup (dev only)
- [ ] Profiler API usage
- [ ] useDebugValue example
- [ ] Bundle analysis commands for Vite and webpack
- [ ] ESLint config with react-hooks plugin
- [ ] Environment variable guidance

### No unintended changes
- [ ] Old sub-skill folders still exist (not deleted)
- [ ] No changes to `standards/dart/`, `standards/graphql/`, or `standards/typescript/`

---

## 5. Verification Notes for Another Agent

Recommended steps:

1. Read `standards/react/SKILL.md` top-to-bottom and confirm it covers all four sections (P0 hooks, P0 component basics, P0 boundary safety, P1 TypeScript) without referencing external files for its core rules.
2. Confirm the References section lists exactly 6 refs and that none of them is a `typescript.md`.
3. Read each ref file and confirm its scope matches the trigger description in SKILL.md — no overlap between refs, no content that belongs in the main skill.
4. Read `_INDEX.md` and confirm it routes to `SKILL.md` (not sub-skill folders) and marks the old sub-skills as deprecated.
5. Confirm that the old sub-skill folders (`react-hooks/`, `react-component-patterns/`, etc.) still exist and were not deleted.
6. Confirm that no files outside `standards/react/` were modified.

### Task 7 — Source coverage audit

Read every old sub-skill file in full, then compare its content against the corresponding new ref. For each old file, verify that every meaningful rule, pattern, and example was either:

- carried forward into the new ref or into `SKILL.md`, or
- deliberately dropped with a clear reason (e.g. duplicated elsewhere, superseded by a better pattern, too implementation-specific).

Files to read and their target destinations:

| Old file | Maps to |
|---|---|
| `react-hooks/SKILL.md` | `SKILL.md` P0 Hook Correctness |
| `react-hooks/refs/REFERENCE.md` | `SKILL.md` P0 Hook Correctness (custom hook patterns) |
| `react-component-patterns/SKILL.md` | `SKILL.md` P0 Component Basics |
| `react-component-patterns/refs/patterns.md` | `refs/component-patterns.md` |
| `react-component-patterns/refs/REFERENCE.md` | `refs/component-patterns.md` |
| `react-performance/SKILL.md` | `refs/performance.md` |
| `react-performance/refs/REFERENCE.md` | `refs/performance.md` |
| `react-security/SKILL.md` | `SKILL.md` P0 Boundary Safety + `refs/security.md` |
| `react-security/refs/REFERENCE.md` | `refs/security.md` |
| `react-state-management/SKILL.md` | `refs/state-management.md` |
| `react-state-management/refs/REFERENCE.md` | `refs/state-management.md` |
| `react-testing/SKILL.md` | `refs/testing.md` |
| `react-testing/refs/REFERENCE.md` | `refs/testing.md` |
| `react-tooling/SKILL.md` | `refs/tooling.md` |
| `react-tooling/refs/example.md` | `refs/tooling.md` |
| `react-typescript/SKILL.md` | `SKILL.md` P1 TypeScript |
| `react-typescript/refs/example.md` | `SKILL.md` P1 TypeScript |

For any gap found — a rule, example, or anti-pattern present in the old file but absent from the new destination — flag it explicitly with the source file, the missing content, and the recommended destination. Do not silently pass a check when content is missing.
