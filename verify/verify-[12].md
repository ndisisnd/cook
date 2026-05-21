---
# Allowed values: planned, complete
status: planned
---

# Verification Run [12] - React Refs Integrity and Best-Practice Fixes

> This plan authorizes a focused audit and remediation pass for the consolidated React domain.
> The current `standards/react/` folder has a new single-skill plus flat `refs/` shape, but the
> old `react-*` sub-skills still exist beside it. The goal is to preserve critical React rules,
> remove stale overlap, and update the active refs to current battle-tested React guidance.
>
> **This file is a plan. It changes nothing on its own.** Execute only the scoped edits below,
> then update this file with audit and verification results.

---

## 1. Before / After

**Before:** `standards/react/` contains the active consolidated files and the deprecated old
sub-skill folders at the same path depth. The new refs carry most old rules, but several examples
and rules are stale, incomplete, or contradictory when checked against current React, Testing
Library, TanStack Query, Redux, and OWASP guidance.

**After:** `standards/react/SKILL.md` and `standards/react/refs/*.md` hold the authoritative React
rules. Critical missing rules are added, stale examples are corrected, deliberate drops are recorded,
and the old `react-*` folders are archived or otherwise made non-loadable after a coverage pass.

| File | Action |
|---|---|
| `standards/react/SKILL.md` | edit |
| `standards/react/_INDEX.md` | edit / regenerate if the repo generator supports it |
| `standards/react/refs/component-patterns.md` | edit |
| `standards/react/refs/hooks.md` | edit |
| `standards/react/refs/performance.md` | edit |
| `standards/react/refs/security.md` | edit |
| `standards/react/refs/state-management.md` | edit |
| `standards/react/refs/testing.md` | edit |
| `standards/react/refs/tooling.md` | edit |
| `standards/react/react-*/` | move / archive after audit, or mark non-loadable by approved repo convention |
| `archive/react/react-*/` | create if archiving is selected |
| `CHANGELOG.md` | edit if present and used for standard changes |
| `verify/verify-[12].md` | update with audit result |

---

## 2. Source Trace

Map every old source that can lose rules, behavior, examples, or references.

| Source | Destination | Handling |
|---|---|---|
| `standards/react/react-component-patterns/SKILL.md` | `standards/react/SKILL.md`, `refs/component-patterns.md` | carry / reconcile |
| `standards/react/react-component-patterns/refs/REFERENCE.md` | `refs/component-patterns.md` | carry examples after TypeScript and context-value fixes |
| `standards/react/react-component-patterns/refs/patterns.md` | `refs/component-patterns.md` | carry slot/render-prop content, drop duplicate weak examples |
| `standards/react/react-hooks/SKILL.md` | `standards/react/SKILL.md`, `refs/hooks.md` | carry and update for React 19 `useEffectEvent` |
| `standards/react/react-hooks/refs/REFERENCE.md` | `refs/hooks.md` | carry only corrected typed hooks |
| `standards/react/react-performance/SKILL.md` | `standards/react/SKILL.md`, `refs/performance.md` | carry / reconcile with React Compiler-era guidance |
| `standards/react/react-performance/refs/REFERENCE.md` | `refs/performance.md` | carry profiler, image, worker, debounce examples after correctness pass |
| `standards/react/react-security/SKILL.md` | `standards/react/SKILL.md`, `refs/security.md` | carry security rules |
| `standards/react/react-security/refs/REFERENCE.md` | `refs/security.md` | carry safe examples only; drop or flag stale CSP/client-rate-limit guidance |
| `standards/react/react-state-management/SKILL.md` | `standards/react/SKILL.md`, `refs/state-management.md` | carry state selection rules |
| `standards/react/react-state-management/refs/REFERENCE.md` | `refs/state-management.md` | carry RTK/TanStack/Zustand only after removing token persistence and adding missing guardrails |
| `standards/react/react-testing/SKILL.md` | `refs/testing.md` | carry |
| `standards/react/react-testing/refs/REFERENCE.md` | `refs/testing.md` | carry examples updated to MSW v2 and semantic query priority |
| `standards/react/react-tooling/SKILL.md` | `refs/tooling.md` | carry current tooling rules, drop stale CRA-era advice where needed |
| `standards/react/react-tooling/refs/example.md` | `refs/tooling.md` | carry StrictMode, profiling, `useDebugValue` after ESM/Vite corrections |
| `standards/react/react-typescript/SKILL.md` | `standards/react/SKILL.md`, `refs/component-patterns.md` if needed | carry TypeScript prop/ref/event rules |
| `standards/react/react-typescript/refs/example.md` | `standards/react/SKILL.md`, `refs/component-patterns.md` | carry native props, generics, refs, polymorphic example if not duplicated |
| `standards/react/react-*/evals/evals.json` | `archive/react/react-*/evals/evals.json` | archive as-is; no rule content expected |

High-risk rows: active deprecated `react-*` sub-skill folders, old refs with unsafe examples, routing/index trigger overlap, stale links in old refs to missing files, generated `_INDEX.md`, and security examples involving auth tokens, CSP, HTML injection, or persisted stores.

---

## 3. External Baseline Used For This Plan

Use these sources to validate rule updates during execution:

| Source | Rules to apply |
|---|---|
| React docs: Rules of Hooks | Hooks only at top level; no hooks in loops, conditions, nested functions, event handlers, class components, callbacks passed to hooks, or `try`/`catch`/`finally`; no hooks after conditional returns. |
| React docs: `useEffect` and You Might Not Need an Effect | Effects synchronize external systems; derived data and event-specific logic should not be effects; manual fetch effects need stale-response cleanup; prefer framework data APIs or client caches for data fetching. |
| React docs: `useEffectEvent` | In React 19+, use `useEffectEvent` for latest committed values needed by effect-local callbacks without re-synchronizing the effect; do not use it to hide real dependencies. |
| Testing Library query priority | Prefer queries accessible to users, especially `getByRole` with accessible name, then labels/text, with test IDs last. |
| TanStack Query important defaults | Add `staleTime`, default stale behavior, background refetch triggers, `gcTime`, retry defaults, and structural sharing expectations. |
| Redux Style Guide | RTK default, reducer purity, no non-serializable state/actions, selectors, feature slices, minimal derived state, RTK Query for Redux data fetching. |
| OWASP XSS Prevention Cheat Sheet | Treat React escape hatches as dangerous, validate `javascript:` and `data:` URLs, sanitize HTML with DOMPurify, avoid dangerous sinks, use CSP as defense-in-depth, consider Trusted Types. |

---

## 4. Findings To Fix

| ID | Severity | Finding | Required action |
|---|---|---|---|
| 12-A | Critical | Deprecated `standards/react/react-*` sub-skills still exist beside the new consolidated skill. This creates routing/index overlap and leaves stale old refs loadable by any scanner that discovers all `SKILL.md` files. | After coverage audit, move old `react-*` folders to `archive/react/` or apply the repo-approved non-loadable convention. Update `_INDEX.md` to say archived, not only deprecated pending removal. |
| 12-B | Critical | Old state-management ref persisted `token` in Zustand; new ref correctly forbids this, but the stale old ref remains active until 12-A is fixed. | Do not carry token persistence. Record it as deliberately dropped. Ensure active refs state that persisted stores must never hold tokens/JWTs/secrets. |
| 12-C | High | React 19 `useEffectEvent` is missing from active `SKILL.md`, `refs/hooks.md`, and `_INDEX.md` triggers. Current `SKILL.md` recommends the latest-ref pattern as the main stale-closure solution. | Add `useEffectEvent` guidance for React 19+ effect-local callbacks. Keep latest-ref as fallback for projects without `useEffectEvent` or for non-effect event patterns. Add trigger keyword. |
| 12-D | High | Hook rules are incomplete. Active `SKILL.md` covers conditions, loops, nested functions, but misses hooks after conditional return, hooks inside `try`/`catch`/`finally`, event handlers, class components, and callbacks passed to `useMemo`/`useReducer`/`useEffect`. | Expand P0 hook correctness with the full React Rules of Hooks. |
| 12-E | High | Effect guidance over-prescribes `AbortController` and does not cover stale-response/race cleanup for non-abortable async work. | Add React's `ignore`/stale-response cleanup pattern, while still using `AbortController` for cancellable fetches. State that framework data APIs, route loaders, TanStack Query, or SWR are preferred over raw fetch effects when available. |
| 12-F | High | Memoization guidance conflicts with React Compiler-era practice. `SKILL.md` says memoize objects/arrays before placing them in deps, while React guidance often prefers moving object/function creation into the effect or hoisting constants. | Rewrite to prefer eliminating unnecessary object/function dependencies first; use `useMemo`/`useCallback` only when identity stability or measured expensive computation requires it. Note that React Compiler may reduce manual memoization needs. |
| 12-G | High | `useSyncExternalStore` is not taught in hooks/state refs, despite being the preferred React API for external subscriptions. It appears only as a tooling debug-label example. | Add `useSyncExternalStore` guidance and a small typed `useOnlineStatus` or external-store subscription example to `refs/hooks.md`. |
| 12-H | High | `refs/security.md` `AuthProvider` returns an inline object context value, contradicting `refs/state-management.md` guidance and causing all consumers to re-render. | Memoize the provider value, split contexts, or reduce the auth example to avoid teaching an unstable provider value. |
| 12-I | High | `refs/component-patterns.md` compound component example returns an inline object provider value and lacks accessibility requirements for custom accordions. | Memoize or split the context value. Add keyboard/focus/ARIA requirements for custom accordions, dialogs, menus, tabs, and compound widgets. |
| 12-J | High | `refs/performance.md` TanStack Virtual example is likely layout-broken because virtual rows are transformed in normal document flow rather than absolutely positioned inside a relative spacer. | Rewrite virtualization example to the canonical pattern: scroll parent, spacer with `position: relative`, virtual row with `position: absolute`, `top: 0`, `left: 0`, `width: 100%`, `transform: translateY(...)`. |
| 12-K | High | `refs/security.md` lacks Trusted Types and context-specific XSS sink guidance. OWASP explicitly calls out React gaps around `dangerouslySetInnerHTML`, `javascript:` URLs, `data:` URLs, dangerous sinks, and post-sanitization mutation. | Add concise Trusted Types guidance for Chromium-backed apps, safe sinks vs dangerous sinks, `data:` URL caveats, and warning that modifying sanitized HTML can void sanitization. |
| 12-L | Medium | CSP guidance allows `style-src 'unsafe-inline'` without explaining nonce/hash tradeoffs, and old source had `script-src 'unsafe-inline' 'unsafe-eval'`. | Keep the new removal of `unsafe-eval`/inline scripts. Clarify that inline styles should use nonces/hashes where possible, and `'unsafe-inline'` is a compatibility fallback to justify explicitly. |
| 12-M | Medium | SSR serialized-state escaping only replaces `<` and `>`. This is too narrow for a reusable standard. | Use a robust JSON escaping helper or recommend a proven serializer. Include escaping for `<`, `>`, `&`, U+2028, and U+2029, and prefer `application/json` script tags where appropriate. |
| 12-N | Medium | Client-side rate limiting from the old security ref is not carried. That is acceptable only if documented as a deliberate drop because client rate limiting is bypassable and server enforcement is required. | Record deliberate drop, or add a UX-only debounce/throttle note that explicitly says backend rate limits are mandatory. |
| 12-O | Medium | CSRF/cookie guidance hard-codes `SameSite=Strict`, which can break OAuth or cross-site identity flows. | Change to `SameSite=Strict` or `Lax` based on flow, with CSRF tokens for cookie-authenticated state-changing requests. |
| 12-P | Medium | `refs/state-management.md` mentions Jotai in the decision table but gives no implementation or guardrails. | Either add a short Jotai section or remove Jotai from the selection table. |
| 12-Q | Medium | TanStack Query guidance is too shallow for critical server-state rules. It lacks default stale behavior, focus/reconnect refetches, retries, `gcTime`, structural sharing, query-key design, and mutation invalidation rules beyond one example. | Add a compact Important Defaults section and query-key/invalidation checklist. |
| 12-R | Medium | Redux Toolkit guidance is too shallow. It lacks no non-serializable state/actions, reducer purity, selectors, feature slices, RTK Query, and `useSelector` granularity. | Add a Redux Toolkit guardrails subsection, or explicitly state this React ref only covers minimal RTK usage and link/defer deeper Redux rules if another standard owns it. |
| 12-S | Medium | Testing ref is generally good, but missing absence-query rules, `waitFor` guardrails, fake timers with `userEvent`, and avoiding unnecessary manual `act()`. | Add `queryBy*` for absence, no side effects inside `waitFor`, configure `userEvent` with fake timers, and rely on RTL's async utilities instead of manual `act()` unless unavoidable. |
| 12-T | Medium | Tooling ESLint section is incomplete and says `exhaustive-deps` should be `warn`, which weakens a P0 rule and conflicts with `SKILL.md` saying never suppress it. | Require `rules-of-hooks` as error and `exhaustive-deps` as at least warn, preferably error in CI/strict repos. Add React Compiler-era `eslint-plugin-react-hooks` recommended rules where compatible. Never set it to off. |
| 12-U | Medium | `useId`, ref typing in React 19 (`ref` as prop), and `useLayoutEffect` visual measurement/flicker guidance are absent from active refs. | Add concise guidance: `useId` for accessible generated IDs, `useLayoutEffect` only for pre-paint layout work, and refs/imperative handles according to project React version. |
| 12-V | Low | Performance ref says avoid barrel files broadly. This is useful for tree-shaking, but too absolute for type-only or curated package-boundary barrels. | Narrow to avoid `export *` and broad runtime barrels in app code; allow explicit curated/type-only barrels when verified by bundler output. |
| 12-W | Low | Some new refs duplicate `React.memo`, context splitting, token storage, and barrel-file rules already in `SKILL.md`. Duplication is acceptable for depth refs but should not drift. | Keep duplicated P0 rules only where useful; align wording exactly or cross-reference to avoid contradictions. |
| 12-X | Low | Old refs link to missing files such as `mocking.md`, `integration-tests.md`, `hoc-pattern.md`, `custom-hooks.md`, and others. These links should not survive in active refs or archived notes. | Verify active refs contain no stale links to missing old ref files. Archived old refs may keep historical links only if archived and non-loadable. |

---

## 5. Execution Plan

1. Read every source row in Section 2 before editing.
2. Patch active `SKILL.md` first for P0 rules: hooks, effects, memoization, security boundary, TypeScript/ref/accessibility essentials.
3. Patch `refs/hooks.md` for `useEffectEvent`, `useSyncExternalStore`, stale async cleanup, `useId`, `useLayoutEffect`, and version-aware ref guidance.
4. Patch `refs/component-patterns.md` for stable provider values, accessible compound widgets, controlled/uncontrolled nuance, and React 19 ref patterns if appropriate.
5. Patch `refs/performance.md` for the virtualizer bug, compiler-aware memoization, raw fetch effect caveats, and narrowed barrel guidance.
6. Patch `refs/security.md` for stable auth context, Trusted Types, safe sinks, robust SSR JSON escaping, cookie/CSRF nuance, CSP wording, and deliberate drop of client-only rate limiting.
7. Patch `refs/state-management.md` for TanStack Query defaults, Redux Toolkit guardrails, Jotai handling, and persisted-store secret rules.
8. Patch `refs/testing.md` for absence queries, `waitFor`, fake timers with `userEvent`, MSW v2 consistency, and manual `act()` guidance.
9. Patch `refs/tooling.md` for modern ESLint/React Compiler rules, StrictMode wording, bundle analysis, and production-removal guardrails for debugging tools.
10. Update `_INDEX.md` keywords/loading notes, especially `useEffectEvent`, `useSyncExternalStore`, `useId`, `useLayoutEffect`, Trusted Types, and accessibility terms if the generator allows manual edits.
11. Run a coverage audit against Section 2 and record carried rules and deliberate drops.
12. Archive or otherwise de-activate `standards/react/react-*` only after the coverage audit passes.
13. Update `CHANGELOG.md` if present in the repo and used for standards changes.
14. Re-read every edited active ref for coherence, stale links, and contradictions.

### Audit Result

- Status: `pending`
- Gaps fixed: `pending`
- Deliberate drops expected: old Zustand token persistence; old client-side rate limiting as security control; old CSP `unsafe-inline`/`unsafe-eval` script guidance; duplicate weak JSX examples; stale missing-ref links.

---

## 6. Guardrails

- Allowed paths: `standards/react/`, `archive/react/`, `CHANGELOG.md`, `verify/verify-[12].md`.
- Verify-only unless explicitly needed: root `SKILL.md`, other standards domains, package/build scripts.
- Do not edit unrelated domains.
- Do not silently drop old-source content; carry it or record a deliberate drop with reason.
- Do not keep stale unsafe examples in active refs just because they existed in old refs.
- Prefer narrow additive edits and small example replacements over broad rewrites.
- Archive old folders with history-preserving moves if the repo convention supports it.
- Stop and ask if a repo generator would overwrite manual `_INDEX.md` edits and the generator behavior is unclear.

---

## 7. Success Criteria

### Active React Skill And Refs

- [ ] `standards/react/SKILL.md` contains complete Rules of Hooks coverage.
- [ ] `standards/react/SKILL.md` distinguishes effects from derived render logic and event-specific logic.
- [ ] `standards/react/SKILL.md` and `refs/hooks.md` include React 19 `useEffectEvent` guidance with a fallback path.
- [ ] `refs/hooks.md` includes `useSyncExternalStore`, stale async cleanup, `useId`, and `useLayoutEffect` guidance.
- [ ] `refs/component-patterns.md` examples do not teach unstable context provider values.
- [ ] `refs/component-patterns.md` includes accessibility requirements for custom compound widgets.
- [ ] `refs/performance.md` virtualized list example follows a correct layout pattern.
- [ ] `refs/performance.md` memoization guidance is compatible with React Compiler-era practice.
- [ ] `refs/security.md` includes Trusted Types, safe sinks, robust serialized-state escaping, and cookie/CSRF nuance.
- [ ] `refs/security.md` does not carry old `unsafe-eval` script CSP guidance or client-only rate limiting as a security control.
- [ ] `refs/state-management.md` includes TanStack Query defaults and Redux Toolkit guardrails, or records why they are delegated.
- [ ] `refs/testing.md` covers absence queries, `waitFor` guardrails, fake timers with `userEvent`, and manual `act()` guidance.
- [ ] `refs/tooling.md` includes modern React Hooks linting and does not weaken exhaustive deps to an ignorable-only standard.

### Overlap And Archive

- [ ] Every Section 2 source row is accounted for in active refs or deliberate drops.
- [ ] Old `standards/react/react-*` folders are archived or made non-loadable after the audit pass.
- [ ] `_INDEX.md` no longer implies active deprecated sub-skills can be loaded as peers.
- [ ] Active refs contain no links to missing old ref files.
- [ ] Active refs contain no examples that persist tokens/JWTs/secrets in JS-accessible storage.

### Verification Commands

- [ ] `git diff --check && git diff --cached --check`
- [ ] Grep active refs for stale old paths: `standards/react/react-`, `../react-`, `refs/REFERENCE.md`, and old missing file names.
- [ ] Grep active refs for unsafe token persistence: `token`, `JWT`, `localStorage`, `sessionStorage`, `persist`.
- [ ] Grep active refs for CSP regressions: `unsafe-eval`, `script-src.*unsafe-inline`.
- [ ] Grep active refs for hooks coverage: `useEffectEvent`, `useSyncExternalStore`, `useId`, `useLayoutEffect`, `try`, `conditional return`.
- [ ] Grep active refs for provider value regressions: `Provider value={{`.
- [ ] Verify active React domain has exactly one authoritative `SKILL.md` under `standards/react/` once archived, unless repo policy intentionally keeps deprecated folders non-loadable.
- [ ] No unintended files changed; no user changes reverted.

---

## 8. Notes For Executor

- The old refs are useful as source trace, not as correctness authority. Prefer current React and security docs when old examples conflict.
- Preserve token economy. Keep `SKILL.md` compact and put depth in refs.
- Keep duplicated P0 rules short and aligned across refs to prevent drift.
- If React version is unknown in a target app, phrase React 19-only APIs as conditional: use when available, otherwise apply the fallback.
- Record every stale old-source example that is intentionally not carried.
