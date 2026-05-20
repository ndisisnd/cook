---
status: complete
---

# Verification Run [6] — Cook Skill Refactor: Keyword-Driven Orchestrator

> Superseded the original mode-file plan. During execution the design changed:
> there are **no** `frontend` / `backend` / `full-stack` mode files. cook owns
> detection only; the mode rules were folded into the existing global concern
> refs by topic. This doc reflects what was actually built.

## 1. What Was Changed

### Problem before

`cook/SKILL.md` was a two-path if/else router: it sent the agent to either `review/SKILL.md` or `global/SKILL.md` and then told it to follow hardcoded domain paths. There was no keyword extraction, no programmatic index lookup, and no structured return to the calling agent.

The layer logic (`--frontend` vs `--backend` vs `--full-stack`) lived as a "Mode Routing" table in `standards/global/_INDEX.md` and as inline P1 sections in `standards/global/SKILL.md`. This meant: (a) the top-level router did not control layer selection, and (b) every global invocation loaded all three modes even when one applied.

`--full-stack` was not an orthogonal third mode — it was defined as "apply both `--frontend` and `--backend`" plus three cross-layer rules. The three-value enum was therefore non-orthogonal.

### After (as shipped)

There are **no mode flags and no mode files**. The layer concept was dissolved into per-concern rules:

1. `cook/SKILL.md` became a keyword-driven orchestrator that owns detection and composition only — it holds no rules.
2. The three P1 mode sections were **folded by topic** into the existing global concern refs (`architecture`, `security`, `performance`, `api-design`, `error-handling`). No `frontend.md` / `backend.md` / `full-stack.md` was created.
3. `standards/global/SKILL.md` was reduced to P0 universal rules + anti-patterns + references; the entire P1 mode section was removed.
4. `standards/global/_INDEX.md` became a keyword/pattern **Concern Match** table that cook reads to decide which concern refs to load. The Mode Routing and mode File-Match rows were removed.
5. `global/` is now a peer rule-library (universal P0 + concern refs), not a privileged baseline that decides layers.

cook protocol: receive summary → detect review intent → extract keywords → always load global P0 → match global concern refs → detect one-or-more domains and match their sub-skills → compile and return. A task spanning UI and server simply matches concerns and domains from both sides — that replaces "full-stack".

---

## 2. Files Touched (actual)

| File | Action |
|---|---|
| `cook/SKILL.md` | Rewrite — keyword-driven orchestrator protocol; no mode enum; review routing preserved |
| `standards/global/SKILL.md` | Edit — removed entire P1 mode section; updated frontmatter description; P0 / anti-patterns / references unchanged |
| `standards/global/_INDEX.md` | Rewrite — Concern Match table (keyword + file pattern → concern ref); mode routing removed; notes updated |
| `standards/global/refs/architecture.md` | Edit — added Component & State Structure section (one-component-per-file, local state, logic→hooks, backend-logic-leak) |
| `standards/global/refs/security.md` | Edit — added UI Security, Auth & Ownership, and Input Validation sections |
| `standards/global/refs/performance.md` | Edit — added re-render / data-waterfall rules to UI; added Database section (N+1, FK indexing) |

No new files were created. `standards/global/refs/api-design.md` and `error-handling.md` already contained the backend API-semantics and error-architecture rules verbatim, so they were not edited.

No changes to any domain skill files (`flutter/`, `nextjs/`, `react/`, `database/`, `graphql/`, `typescript/`, `dart/`) or `review/SKILL.md`.

---

## 3. Where Each P1 Rule Landed

| Original P1 rule | Now lives in |
|---|---|
| One component per file; no cross-concern mixing | `refs/architecture.md` (new) |
| Keep state local; lift only when shared | `refs/architecture.md` (new) |
| Extract business logic to hooks/services | `refs/architecture.md` |
| No `dangerouslySetInnerHTML` without sanitization | `refs/security.md` (new) |
| No URLs from unsanitized input | `refs/security.md` (new) |
| No auth tokens in `localStorage` | `refs/security.md` (new) |
| Avoid unnecessary re-renders (memoize) | `refs/performance.md` (new) |
| Avoid data waterfalls (parallel fetch) | `refs/performance.md` (new) |
| Virtualize long lists | `refs/performance.md` (pre-existing) |
| `GET` read-only / idempotent | `refs/api-design.md` (pre-existing) |
| Correct status codes; never 200 for error | `refs/api-design.md` (pre-existing) |
| Paginate; default 20 / max 100 | `refs/api-design.md` (pre-existing) |
| Domain / API / Infrastructure error layers | `refs/error-handling.md` (pre-existing) |
| Scope query by owner/tenant | `refs/security.md` (new) |
| Require auth by default | `refs/security.md` (new) |
| Role guard on every gated action | `refs/security.md` (new) |
| No N+1 queries | `refs/performance.md` (pre-existing) |
| Index FK and filter columns | `refs/performance.md` (new) |
| No backend business logic leaked into frontend | `refs/architecture.md` (new) |
| Validate once at server boundary; mirror in UI for UX | `refs/security.md` (new) |
| API contract change requires version bump | `refs/api-design.md` (pre-existing) |

---

## 4. Expected Output When Running the Skill

### Scenario A — Frontend component work in Next.js

Input: "add a user profile page using App Router, Tailwind, and zustand for local state"

Keywords: `App Router`, `Tailwind`, `zustand`, `state`, `page.tsx`
Global P0: always loaded.
Concern match: `refs/architecture.md` (component, state), `refs/performance.md` (re-render).
Domain match: nextjs → `nextjs-app-router`, `nextjs-styling`, `nextjs-state-management`.

Returns: global P0 + matched concern refs + the three nextjs sub-skills.

### Scenario B — Backend API work

Input: "add a paginated list endpoint for orders, scoped by tenant, using a repository pattern"

Keywords: `endpoint`, `paginated`, `tenant`, `repository`, `api`
Concern match: `refs/api-design.md` (endpoint, pagination), `refs/security.md` (tenant/auth), `refs/architecture.md` (repository/layer).
Domain match: none (no framework signal) — global only.

Returns: global P0 + matched concern refs.

### Scenario C — Full-stack feature (no longer a special mode)

Input: "connect the order list UI to the new orders API, validate on both client and server"

Keywords: `UI`, `API`, `validate`, `client`, `server`
Concern match: `refs/api-design.md`, `refs/security.md` (validate-at-boundary), `refs/architecture.md` (logic-leak).
Domain match: nextjs (UI + server actions) and, if a schema is touched, database — both load.

Returns: global P0 + matched concern refs + matched sub-skills from every matched domain. "Full-stack" is just multiple matches.

### Scenario D — Flutter state management work

Input: "add a BlocProvider for the cart feature using flutter_bloc"

Keywords: `BlocProvider`, `flutter_bloc`, `state`, `_bloc.dart`
Concern match: `refs/architecture.md` (state).
Domain match: flutter → `flutter-bloc-state-management`.

Returns: global P0 + matched concern refs + flutter-bloc-state-management.

### Scenario E — Code review

Input: "review this PR"

Review intent detected → load `standards/review/SKILL.md`. Steps 3–7 skipped. (Unchanged behaviour.)

---

## 5. Success Criteria (verified)

### Structure
- [x] `cook/SKILL.md` exists and has a step-by-step protocol section
- [x] No `frontend.md` / `backend.md` / `full-stack.md` files exist (intentional)
- [x] `standards/global/SKILL.md` no longer contains `### --frontend`, `### --backend`, or `### --full-stack` headings, nor the P1 mode section
- [x] `standards/global/_INDEX.md` no longer contains a Mode Routing or mode File-Match table

### `cook/SKILL.md` protocol
- [x] Named step for receiving the code summary from the caller
- [x] Named step for review-intent detection that routes to `standards/review/SKILL.md`
- [x] Named step for keyword extraction
- [x] Named step that always loads global P0
- [x] Named step for matching global concern refs via the Concern Match table
- [x] Named step for domain detection that allows multiple matched domains
- [x] Named step for compiling all matched rules and returning them to the caller
- [x] No mode flags or three-value mode enum anywhere in the file

### `cook/SKILL.md` domain detection table
- [x] `flutter` → `standards/flutter/_INDEX.md` (`**/*.dart` + Flutter terms)
- [x] `nextjs` → `standards/nextjs/_INDEX.md` (Next.js patterns/terms)
- [x] `react` → `standards/react/_INDEX.md` (React terms, no Next.js signal)
- [x] `database` → `standards/database/_INDEX.md` (sql, schema, migration, redis, postgres, prisma)
- [x] `graphql` → `standards/graphql/_INDEX.md` (graphql, resolver, schema, gql, Apollo)
- [x] `typescript` → `standards/typescript/SKILL.md` (`*.ts`, no framework signal)
- [x] `dart` → `standards/dart/_INDEX.md` (non-Flutter Dart terms)

### Concern folding (no rule lost)
- [x] All component-structure rules present in `refs/architecture.md`
- [x] All UI-security, auth/ownership, and validate-at-boundary rules present in `refs/security.md`
- [x] All frontend + backend performance rules present in `refs/performance.md`
- [x] API semantics + versioning rules present in `refs/api-design.md`
- [x] Three-layer error architecture present in `refs/error-handling.md`
- [x] Cross-layer logic-leak rule present in `refs/architecture.md`

### `global/SKILL.md` after edit
- [x] P0 universal rules section unchanged
- [x] P1 mode section removed entirely
- [x] Frontmatter description updated to drop mode-flag invocation
- [x] Anti-patterns and References sections unchanged

### `global/_INDEX.md` after edit
- [x] Mode Routing section removed
- [x] Mode File-Match rows removed
- [x] Concern Match table present (keyword + file pattern → concern ref)
- [x] Notes updated: layer/mode selection now happens in `cook/SKILL.md`; no mode files

### No unintended changes
- [x] No files under `standards/flutter/`, `nextjs/`, `react/`, `database/`, `graphql/`, `typescript/`, `dart/` were modified
- [x] `standards/review/SKILL.md` was not modified
- [x] Only six files changed: `cook/SKILL.md`, `global/SKILL.md`, `global/_INDEX.md`, and the three concern refs (`architecture`, `security`, `performance`)

---

## 6. Post-Verification Audit (2026-05-21)

Re-verified every claim above against the working tree and commit `d290dac` ("refactor(standards): make cook keyword-driven"). All positive and negative claims hold: that commit touched exactly the six standards files listed (plus `CHANGELOG.md`), and `api-design.md` / `error-handling.md` were correctly left untouched as pre-existing.

### Regression found and fixed

The original criteria only checked that `standards/review/SKILL.md` was unmodified (true) but never inspected its `refs/`. Removing the mode flags left `standards/review/refs/skill-routing.md` as a **dangling reference** — it still told reviewers to load `standards/global/SKILL.md` "with the appropriate mode flag" and mapped review surfaces to `--frontend` / `--backend` / `--full-stack`, which no longer exist.

Fixed `skill-routing.md` to match the keyword-driven model:
- Global Review Base loads `global/SKILL.md` for P0 and matches concern refs via the `_INDEX.md` Concern Match table — no mode flags.
- The mode-flag table became a **Surface-to-Skills Mapping** (surface → concern refs + domain skills, additive union).
- Worked examples now load the specific concern refs instead of mode-flag invocations.

Confirmed afterward that the only remaining `--frontend` / `--backend` / `--full-stack` mentions outside `verify/` are the intentional "there are no mode flags" disclaimers in `cook/SKILL.md`, `global/_INDEX.md`, and `skill-routing.md`.
