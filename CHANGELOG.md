# Changelog

All notable changes to this project are documented here, newest first.

---

## [pending] - 2026-05-21 - Harden and archive React consolidation

**Closed verify-[12] by making the consolidated React skill authoritative, hardening active refs, and archiving the deprecated `react-*` sub-skills.**

- Added current React hook guidance for full Rules of Hooks coverage, `useEffectEvent`, `useSyncExternalStore`, `useId`, `useLayoutEffect`, stale async cleanup, and compiler-era memoization
- Fixed active examples and guardrails for stable context provider values, accessible compound widgets, TanStack Virtual layout, Trusted Types/safe sinks, SSR JSON escaping, cookie/CSRF nuance, TanStack Query defaults, Redux Toolkit, Jotai, RTL async/absence/timer rules, and hooks linting
- Regenerated `standards/react/_INDEX.md` keywords/loading notes and marked old React sub-skills as archived source trace
- Moved all deprecated `standards/react/react-*` folders to `archive/react/` using `git mv`, preserving their refs and evals verbatim
- Deliberately did not carry old Zustand token persistence, client-only rate limiting as a security control, unsafe script CSP guidance, duplicate weak examples, or stale missing-ref links into active refs

---

## [5005e0f] — 2026-05-21 · React refs: improve examples and cross-cutting concerns

**Modernized React ref examples, added missing cross-cutting guidance, and archived verify-[11] to open verify-[12].**

- `refs/component-patterns.md` — replaced the Compound Component example (Select → Accordion) with a factory-function context guard, added `event.preventDefault()` to the uncontrolled form example, added a Boolean Props section warning against impossible-state flag combinations and `&&`-with-zero renders
- `refs/performance.md` — added `useDeferredValue` example for urgent-vs-deferred inputs, `content-visibility: auto` CSS tip for large off-screen sections, and an RSC `cache()` deduplication pattern for server reads
- `refs/security.md` — added explicit `eval()`/`new Function` prohibition, added an Input Validation Boundary section (client-side validation is UX only; validate on the server), added `Permissions-Policy` header to the CSP example
- `refs/state-management.md` — added Jotai to the state-tool decision table, added provider memoization pattern (`useMemo`/`useCallback` on Context value), added rule against persisting tokens or secrets in Zustand/Redux/`localStorage`
- `refs/testing.md` — added shallow-rendering prohibition and real-provider guidance, added a Mocking Heavy Dependencies section with a framer-motion stub example
- Archived `verify/verify-[11.1].md` → `verify/done/` and created `verify/verify-[12].md`

---

## [87cc89c] — 2026-05-21 · Fix Next.js consolidation verification gaps

**Closed the verify-[11.1] follow-up gaps in the consolidated Next.js standard without changing archived source folders.**

- Replaced a server-side own-API cache example with direct DAL/database access using cache tags
- Updated App Router examples to use Next 15 async `params` handling
- Restored dropped source guidance for Auth.js/Clerk selection, `dynamicParams`, route colocation, Pages Router API status codes, and DAL error handling
- Documented `X-XSS-Protection` as legacy source guidance and kept CSP/output escaping as the active recommendation
- Kept the root cook router wording that loads matched domain skills plus refs because reverting it would reintroduce stale sub-skill routing after the Next.js consolidation

---

## [67ab48b] — 2026-05-21 · Consolidate nextjs domain into single-skill structure

**Collapsed 18 Next.js sub-skill folders into one `SKILL.md` + 13 topic refs, matching the single-skill domain shape used by Flutter, React, Dart, TypeScript, Global, Database, and GraphQL. All superseded files are preserved in `archive/nextjs/` for review.**

- Created `standards/nextjs/SKILL.md` with Router Decision guidance, P0 rules for RSC boundaries, data fetching/access, App Router conventions, and security/auth, plus P1 rules for rendering/caching and Server Actions
- Created 13 flat refs under `standards/nextjs/refs/`: `app-router`, `pages-router`, `server-components`, `data-fetching`, `rendering-and-caching`, `server-actions`, `security`, `state-management`, `styling-and-optimization`, `testing`, `architecture`, `i18n`, `tooling`
- Merged overlapping domains: authentication + security, data-access-layer + data-fetching, rendering + caching, styling + optimization, and upgrade + tooling
- Carried forward the high-risk orphan/shared refs: `data-access-layer/refs/patterns.md`, `rendering/refs/SUSPENSE_BAILOUT.md`, `pages-router/refs/feature-sliced-design-pages.md`, and `architecture/refs/RSC_BOUNDARIES.md` as the single `server-components` boundary home
- Modernized examples where the source already pointed to Next 15/16 behavior: async request APIs, Cache Components / `'use cache'`, `cacheLife()`, `useActionState`, and direct service/DAL calls instead of internal API fetches
- Regenerated `standards/nextjs/_INDEX.md` to the AUTO-GENERATED format with File Match, Loading Instructions, and archived source trace
- Moved all 18 `nextjs-<name>/` folders to `archive/nextjs/` using `git mv`, preserving `SKILL.md`, `refs/`, and `evals/` contents verbatim

---

## [8f4c60c] — 2026-05-21 · Refine React consolidation audit

**Validated the verify-[10] React ref extraction against the legacy `react-*` sources and tightened the active refs where the migration introduced ambiguity or internal conflicts.**

- `SKILL.md` — softened arbitrary component-size, one-component, and prop-drilling rules into responsibility-based guidance while preserving the original intent
- `refs/component-patterns.md` — replaced a `key={i}` render-props example with an explicit `getKey` contract so it no longer conflicts with the stable-key rule
- `refs/hooks.md` — tightened `useLocalStorage`, `useWindowSize`, `useIntersectionObserver`, and `usePrevious` examples for latest-state updates, hydration safety, memoized options, and clearer typing
- `refs/security.md` — made the safe-link URL validation example exception-safe and SSR-safe
- `refs/tooling.md` — clarified the `why-did-you-render` snippet as a Vite example and used `import.meta.env.DEV`

---

## [8f4c60c] — 2026-05-21 · React ref-extraction gap fix (verify-[10])

**Closed the source-coverage gaps the verify-[10] audit found in the React consolidation, satisfying verify-[8] §3 before the deprecated `react-*/` folders are archived. All changes are additive to the active React skill.**

- Created `standards/react/refs/hooks.md` — a 7th ref with the custom-hooks library extracted from `react-hooks/refs/REFERENCE.md`, rewritten as typed TypeScript: `useLocalStorage`, `useDebounce`, `useWindowSize`, `useOnClickOutside`, `useIntersectionObserver`, `usePrevious`, `useToggle`. Each carries its correctness note (cleanup, exhaustive deps, SSR-safe access) (10-A · HIGH)
- `SKILL.md` — appended a `hooks` entry to the References list
- `refs/performance.md` — added a "Native Image Lazy-Loading" note (`loading="lazy"`, `decoding="async"`) in the Reduce Bundle Size section, deferring `next/image` to the nextjs domain (10-C · LOW)
- `_INDEX.md` — added a `react → hooks ref` File Match row and a Loading Instruction line for the new ref
- Documented deliberate drop (10-B): `createRateLimiter` ("Rate Limiting on Client") from `react-security/refs/REFERENCE.md` is **not** carried over — client-side rate limiting is not an enforceable security control (trivially bypassed; the server owns rate limits) and would imply false assurance in a security ref

---

## [d01640c] — 2026-05-21 · Flutter refs: resolve conflicts and fill gaps

**Fixed two critical conflicts and three gap/cross-reference issues across `standards/flutter/refs/`. No content deleted; all changes are additive edits or priority demotions.**

- `refs/navigation.md` — Added "Router Decision Rule" table at top; demoted GetX Navigation from P0 to P1 (HIGH), resolving the dual-P0 conflict with go_router
- `refs/state-management.md` — Renamed BLoC state template headings (Union ✅ PREFERRED, Flat ⚠️ LIMITED USE, Equatable ⚠️ LEGACY); inserted "Which to use" guidance block between Union and Flat sections
- `refs/architecture.md` — Added "Which Architecture to Use" decision table at top with 5 criteria and an explicit default ("Feature-Based for new projects")
- `refs/design-system.md` — Added idiomatic `Row(spacing:)` note to Spacing section with ✅/⚠️ examples and cross-reference to SKILL.md § P1 Idiomatic Flutter
- `refs/security.md` — Added `SecurityModule` DI snippet after raw `FlutterSecureStorage()` example; added cross-reference to `refs/dependency-injection.md § Third-Party Modules`
- `refs/error-handling.md` — Added scoping note to Repository Error Mapping section pointing to `refs/networking.md § Token Refresh Pattern` for global HTTP concerns

---

## [8995082] — 2026-05-21 · Consolidate flutter domain into single-skill structure

**Collapsed 22 flutter sub-skill folders into one `SKILL.md` + 13 topic refs, matching the dart/graphql exemplar shape. All superseded files are preserved in `archive/flutter/` for review.**

- Created `standards/flutter/SKILL.md` with always-on P0 rules (design system, error handling) and P1 rules (widgets, idiomatic Flutter, performance), plus a References section listing all 13 refs
- Created 13 flat refs under `standards/flutter/refs/`: `state-management`, `navigation`, `architecture`, `networking`, `error-handling`, `dependency-injection`, `design-system`, `localization`, `notifications`, `security`, `concurrency`, `cicd`, `testing`
- Merged conflicting go_router skills (`flutter-navigation` P1 + `flutter-go-router-navigation` P0) into a single unified go_router section in `refs/navigation.md`
- Carried forward 3 previously orphaned refs: `dls-modular-pattern.md` and `monolithic-pattern.md` into `refs/design-system.md`; `repository-mapping.md` into `refs/architecture.md`
- Confirmed 5 broken `REFERENCE.md` indexes (dangling targets that never existed) — no content carried; files preserved in archive
- Regenerated `standards/flutter/_INDEX.md` to AUTO-GENERATED format with File Match table, Loading Instructions, and Archived section referencing `archive/flutter/`
- Moved all 22 `flutter-<name>/` folders to `archive/flutter/` (repo root) using `git mv`, preserving full history; no files deleted
- `cook/SKILL.md` Flutter row already resolves to `standards/flutter/_INDEX.md`; no change required

---

## [56c3d70] — 2026-05-21 · Align skill-routing with keyword-driven model

**Fixed a dangling reference left in the review skill routing after the keyword-driven refactor.**

- Rewrote `standards/review/refs/skill-routing.md` to drop the `--frontend`/`--backend`/`--full-stack` mode flags and match concern refs via `standards/global/_INDEX.md` instead
- Replaced the mode-flag table with a Surface-to-Skills Mapping (concern refs + domain skills, additive union)
- Updated worked examples to load specific concern refs instead of mode-flag invocations
- Added §6 "Post-Verification Audit" to `verify-[6].md` and moved it into `verify/done/`

---

## [d290dac] — 2026-05-21 · Make cook a keyword-driven orchestrator

**cook now detects what a task touches by keyword and composes standards from concern refs — mode flags are gone.**

- Rewrote the top-level `SKILL.md` as a keyword-driven orchestrator: receive summary → detect review intent → extract keywords → load global P0 → match concern refs → detect domains → compile
- Removed the `--frontend`/`--backend`/`--full-stack` mode flags and the P1 mode section from `standards/global/SKILL.md`
- Converted `standards/global/_INDEX.md` into a Concern Match table (keyword + file pattern → concern ref)
- Folded the frontend/backend layer rules into concern refs: `architecture.md`, `security.md`, `performance.md`

---

## [d679bf1] — 2026-05-21 · Add changelog and verify-[6] plan

**Introduced a root changelog and captured the next verification plan as a standalone artifact.**

- Added `CHANGELOG.md` to track notable repository changes in reverse chronological order
- Added `verify/verify-[6].md` with the verification plan for the latest standards restructuring work

---

## [93f14d2] — 2026-05-20 · Consolidate standards into domain-based structure

**All skill files and references are now organized by domain — one skill entry point per domain, shared refs in a flat folder.**

- Merged separate PostgreSQL, MongoDB, and Redis skills into a single `standards/database/SKILL.md`
- Moved all database reference files into `standards/database/refs/` with vendor prefixes (e.g. `postgresql-best-practices.md`, `redis-checklist.md`)
- Collapsed all global sub-skills (api-design, architecture, code-review, coding-principles, debug, error-handling, owasp, performance, security-audit, security-standards) into a single `standards/global/SKILL.md` backed by consolidated `standards/global/refs/` files
- Added a new React consolidated `standards/react/SKILL.md` with full refs: component-patterns, performance, security, state-management, testing, tooling
- Added GraphQL refs for testing and tooling
- Moved completed verification artifacts into `verify/done/`

---

## [46aa432] — 2026-05-20 · Update review skill routing

**Small update to wire the new code review skill into the global index.**

- Updated `standards/global/_INDEX.md` to reference the new review skill
- Updated `standards/global/code-review/SKILL.md` with routing adjustments
- Updated `standards/review/SKILL.md` trigger language

---

## [4415cda] — 2026-05-20 · Add findings-first code review skill

**A new structured code review skill that outputs findings before explanations.**

- Created `standards/review/SKILL.md` — the main review skill definition
- Created `standards/review/_INDEX.md` — index for review standards
- Added reference files: `finding-severity.md`, `report-format.md`, `review-lenses.md`, `skill-routing.md`
- Added `review-plan.md` — the review workflow plan
- Updated root `SKILL.md` to include the new review skill

---

## [da88c8a] — 2026-05-20 · Reorganize TypeScript and add global standards

**TypeScript skills are consolidated into a single skill; global standards directory added.**

- Added `.gitignore`
- Updated Dart skill and its refs (testing, tooling)
- Added `standards/global/SKILL.md` and `standards/global/_INDEX.md` — new top-level global standards entry point
- Added unified `standards/typescript/SKILL.md` replacing four separate sub-skills
- Added new TypeScript ref files: `security.md`, `testing.md`, `tooling.md`
- Removed old TypeScript sub-skill directories: `typescript-best-practices`, `typescript-language`, `typescript-security`, `typescript-tooling`
- Added `verify/verify-[1].md` — first verification artifact

---

## [aeb9765] — 2026-05-19 · Rename context folders to refs

**Every skill's supporting files moved from `context/` to `refs/` — cleaner, more descriptive naming.**

- Renamed all `context/` directories to `refs/` across all skill domains: dart, database, flutter, global, graphql, nextjs, react, typescript
- Updated all `SKILL.md` files to point to `refs/` instead of `context/`
- No content changes — purely a folder rename

---

## [58c4303] — 2026-05-19 · Initial commit

**First commit — the full standards library from scratch.**

- Added `AGENTS.md` and root `SKILL.md`
- Added **Dart** standards with testing and tooling context
- Added **Database** standards: MongoDB (anti-patterns, best-practices, checklist, implementation, postgres-comparison), PostgreSQL (anti-patterns, best-practices, checklist, implementation, sql-gotchas), Redis (best-practices, checklist)
- Added **Flutter** standards: auto-route navigation, BLoC state management, CI/CD, concurrency, dependency injection, design system, error handling, feature-based clean architecture, GetX navigation, GetX state management, go-router navigation, idiomatic flutter, layer-based clean architecture, localization, navigation, notifications, performance, Retrofit networking, Riverpod state management, security, testing, widgets
- Added **Global** standards: API design, architecture, code review, coding principles, debug, error handling, OWASP (web + API), performance, security audit, security standards
- Added **GraphQL** standards: performance, schema design, security
- Added **Next.js** standards: app router, architecture, authentication, caching, data access layer, data fetching, i18n, optimization, pages router, rendering, security, server actions, server components, state management, styling, testing, tooling, upgrade guide
- Added **React** standards: component patterns, hooks, performance, security, state management, testing, tooling, TypeScript integration
- Added **TypeScript** standards: best practices, language features, security, tooling
