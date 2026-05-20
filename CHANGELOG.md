# Changelog

All notable changes to this project are documented here, newest first.

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
