---
# Allowed values: planned, complete
status: planned
---

# Verification Run [11] - Consolidate the `nextjs` Domain into a Single Skill

> This plan authorizes the `nextjs` migration from the old multi-skill shape into the
> single-skill shape used by `dart`, `typescript`, `global`, `database`, `graphql`, and
> `flutter`. It follows `.compress.md`, flutter verify-[7]/[9], and react verify-[5]/[8]/[10].
>
> **This file is a plan. It changes nothing on its own.** Execute only the scoped edits below,
> then update this file with audit and verification results.

---

## 1. Before / After

**Before:** `standards/nextjs/` has `_INDEX.md` plus 18 `nextjs-*/` sub-skill folders, each
with its own `SKILL.md`, `evals/evals.json`, and `refs/` content. The sources contain duplicated
always-on rules, overlapping topics, three orphaned refs, and one shared ref with no single home.

```
standards/nextjs/
├── _INDEX.md
├── nextjs-app-router/              SKILL.md + evals/ + refs/ (implementation, SELF_HOSTING)
├── nextjs-architecture/            SKILL.md + evals/ + refs/ (implementation, fsd-structure,
│                                     BUNDLING, RUNTIME_SELECTION, DEBUG_TRICKS, RSC_BOUNDARIES)
├── nextjs-authentication/          SKILL.md + evals/ + refs/ (implementation, auth-implementation)
├── nextjs-caching/                 SKILL.md + evals/ + refs/ (implementation, CACHE_COMPONENTS)
├── nextjs-data-access-layer/       SKILL.md + evals/ + refs/ (implementation, patterns)
├── nextjs-data-fetching/           SKILL.md + evals/ + refs/ (usage-examples)
├── nextjs-i18n/                    SKILL.md + evals/ + refs/ (implementation, next-intl, react-intl)
├── nextjs-optimization/            SKILL.md + evals/ + refs/ (example)
├── nextjs-pages-router/            SKILL.md + evals/ + refs/ (implementation, server-side-props,
│                                     feature-sliced-design-pages)
├── nextjs-rendering/               SKILL.md + evals/ + refs/ (strategy-matrix, implementation,
│                                     implementation-details, scaling-patterns, SUSPENSE_BAILOUT)
├── nextjs-security/                SKILL.md + evals/ + refs/ (implementation)
├── nextjs-server-actions/          SKILL.md + evals/ + refs/ (secure-actions)
├── nextjs-server-components/       SKILL.md + evals/ + refs/ (example, composition-security)
├── nextjs-state-management/        SKILL.md + evals/ + refs/ (implementation, redux, zustand, url-state)
├── nextjs-styling/                 SKILL.md + evals/ + refs/ (implementation, scss, ant-design, tailwind)
├── nextjs-testing/                 SKILL.md + evals/ + refs/ (implementation)
├── nextjs-tooling/                 SKILL.md + evals/ + refs/ (implementation)
└── nextjs-upgrade/                 SKILL.md + evals/ + refs/ (example)
```

The 18 source sub-skills declare these priorities:

| Sub-skill | Declared priority | Core topic |
|---|---|---|
| `nextjs-server-components` | P0 | RSC default, `'use client'` at leaves, serialization, hydration |
| `nextjs-data-fetching` | P0 | `fetch` in RSC, static/dynamic/revalidated, no internal `/api` |
| `nextjs-app-router` | P0 | File conventions, route groups, parallel/intercepting routes, async APIs |
| `nextjs-rendering` | P0 | SSG / SSR / ISR / Streaming / PPR selection |
| `nextjs-authentication` | P0 | HttpOnly cookies, middleware auth, token storage |
| `nextjs-security` | P0 | Middleware auth, Server Action validation, CSP, taint, `server-only` |
| `nextjs-pages-router` | P0 legacy | `getServerSideProps` / `getStaticProps` / API routes |
| `nextjs-caching` | P1 | 4 cache layers, `revalidateTag`, `'use cache'` |
| `nextjs-data-access-layer` | P1 | DAL, DTOs, taint, `server-only`, colocated auth |
| `nextjs-server-actions` | P1 | Mutations, forms, `useActionState`, optimistic |
| `nextjs-optimization` | P1 | `next/image`, `next/font`, `next/script`, metadata, Core Web Vitals |
| `nextjs-styling` | P1 | Tailwind/CSS Modules/`cn`, zero-runtime CSS |
| `nextjs-testing` | P1 | Jest/Vitest, RTL, Playwright, MSW |
| `nextjs-upgrade` | P1 | Version migrations, codemods |
| `nextjs-architecture` | P2 | Feature-Sliced Design, slices, import hierarchy |
| `nextjs-i18n` | P2 | Locale routing, next-intl/react-intl |
| `nextjs-state-management` | P2 | URL/server/client state |
| `nextjs-tooling` | P2 | Turbopack, Docker standalone, bundle analysis, env validation |

The migration fixes dead-weight per-skill frontmatter/workflow blocks, duplicated always-on rules,
unguided App Router vs Pages Router duality, split overlapping topics, the three orphaned refs, and
the shared `RSC_BOUNDARIES.md` home.

**After:** `standards/nextjs/` has one always-on `SKILL.md`, a regenerated AUTO-GENERATED
`_INDEX.md`, and 13 flat refs. The 18 original sub-skill folders are moved verbatim to
`archive/nextjs/`.

```
standards/nextjs/
├── SKILL.md
├── _INDEX.md
└── refs/

archive/nextjs/
├── nextjs-app-router/  ...  nextjs-upgrade/   (each original folder intact)
```

| File | Action |
|---|---|
| `standards/nextjs/SKILL.md` | create |
| `standards/nextjs/_INDEX.md` | edit / regenerate |
| `standards/nextjs/refs/app-router.md` | create |
| `standards/nextjs/refs/pages-router.md` | create |
| `standards/nextjs/refs/server-components.md` | create |
| `standards/nextjs/refs/data-fetching.md` | create / merge |
| `standards/nextjs/refs/rendering-and-caching.md` | create / merge |
| `standards/nextjs/refs/server-actions.md` | create |
| `standards/nextjs/refs/security.md` | create / merge |
| `standards/nextjs/refs/state-management.md` | create |
| `standards/nextjs/refs/styling-and-optimization.md` | create / merge |
| `standards/nextjs/refs/testing.md` | create |
| `standards/nextjs/refs/architecture.md` | create |
| `standards/nextjs/refs/i18n.md` | create |
| `standards/nextjs/refs/tooling.md` | create / merge |
| `standards/nextjs/nextjs-*/` | move / archive |
| `archive/nextjs/nextjs-*/` | create by `git mv` |
| `CHANGELOG.md` | edit |
| `cook/SKILL.md` | verify only |
| `verify/verify-[11].md` | edit |

The 13 refs are:

| Ref | Scope | Merges |
|---|---|---|
| `app-router.md` | File conventions, route groups, dynamic segments, parallel/intercepting routes, self-hosting | - |
| `pages-router.md` | Legacy router: `getServerSideProps`/`getStaticProps`/`getStaticPaths`, API routes, `_app`/`_document` | - |
| `server-components.md` | RSC/Client composition, serialization boundaries, server-in-client fix | - |
| `data-fetching.md` | `fetch` strategies plus Data Access Layer: DTOs, taint, `server-only`, colocated auth | data-access-layer |
| `rendering-and-caching.md` | SSG/SSR/ISR/Streaming/PPR plus strategy matrix, scaling, Suspense, cache layers, invalidation | rendering + caching |
| `server-actions.md` | Mutations, forms, `useActionState`/`useOptimistic`, secure-action validation | - |
| `security.md` | Cookies, middleware auth/RBAC, CSP, CSRF, taint, Zod validation | authentication + security |
| `state-management.md` | URL / server / client state; Redux legacy, Zustand, URL-state patterns | - |
| `styling-and-optimization.md` | Tailwind/CSS Modules/`cn`, zero-runtime CSS, image/font/script/metadata/CWV | styling + optimization |
| `testing.md` | Jest/Vitest + RTL, Playwright E2E, MSW | - |
| `architecture.md` | Feature-Sliced Design, slices/segments, bundling, runtime, debug tricks | - |
| `i18n.md` | Locale routing, next-intl, react-intl/next-translate legacy | - |
| `tooling.md` | Turbopack, standalone Docker output, bundle analysis, env validation, lint/CI, version migration / `@next/codemod` | tooling + upgrade |

`SKILL.md` target outline:

- Preamble: Router Decision. App Router is default for new work; if the project uses `pages/`, treat App Router rules as informational and load `refs/pages-router.md`.
- P0: Server & Client Components. RSC by default; push `'use client'` to interactive leaves; serialize Server-to-Client props; never pass secrets or full DB objects to the client; avoid browser-only values in initial render. Detail: `refs/server-components.md`.
- P0: Data Fetching & Access. Fetch directly in async Server Components; call DB/service/DAL directly; never fetch your own `/api`; parallelize with `Promise.all`; wrap slow fetches in `<Suspense>`; use `server-only`, auth inside every DAL function, and DTOs. Detail: `refs/data-fetching.md`.
- P0: App Router Conventions. `page`/`layout`/`loading`/`error`/`route` roles; await async APIs in Next 15+; every segment needs Client-Component `error.tsx`; keep pages thin. Detail: `refs/app-router.md`.
- P0: Security & Auth. HttpOnly + Secure + SameSite cookies; never `localStorage` for tokens; validate every Server Action input with Zod and run `auth()` inside the action; use `server-only`; cover CSP/CSRF and taint. Detail: `refs/security.md`.
- P1: Rendering & Caching. Pick SSG / SSR / ISR / PPR by data freshness; stream with `<Suspense>`; know the 4 cache layers; use `revalidateTag`/`revalidatePath` on mutation; prefer `'use cache'` + `cacheLife()` on Next 16+. Detail: `refs/rendering-and-caching.md`.
- P1: Server Actions. Mutations without endpoints; `'use server'`; `useActionState` / `useFormStatus`; define in `actions.ts`, not inside components. Detail: `refs/server-actions.md`.
- Anti-Patterns: one merged, deduplicated list drawn from all 18 source Anti-Patterns blocks.
- References: the 13 refs above, priority-grouped.

Design decisions to preserve:

- Router duality: App Router is `SKILL.md` core; Pages Router is a legacy ref gated by the Router Decision preamble.
- Merge `authentication` + `security` into `refs/security.md` because they overlap on cookies, middleware auth, taint, and `server-only`.
- Fold `data-access-layer` into `refs/data-fetching.md` because DAL is the canonical secure fetching pattern.
- Merge `rendering` + `caching` into `refs/rendering-and-caching.md` because freshness strategy and cache behavior are one decision.
- Merge `styling` + `optimization` into `refs/styling-and-optimization.md` so `next/font`, image dimensions, CSS approach, and Core Web Vitals have one owner.
- Merge `upgrade` into `refs/tooling.md` as an Upgrades section beside build/deploy tooling.
- Keep `server-components` as both a `SKILL.md` P0 principle and a depth ref.
- Default `RUNTIME_SELECTION.md` and `DEBUG_TRICKS.md` to `refs/architecture.md` unless full reading shows `rendering-and-caching.md` or `tooling.md` fits better.
- Normalize priority without inventing new rules: App Router correctness/security/data are P0; rendering/caching/actions are P1; architecture/i18n/state/tooling are P2 refs loaded on demand.

---

## 2. Source Trace

Map every source that can lose rules, behavior, examples, or references. `evals/evals.json` files
carry no rules; archive them as-is.

| Source | Destination | Handling |
|---|---|---|
| `nextjs-server-components/SKILL.md` | `SKILL.md` P0 Server & Client Components | carry |
| `nextjs-server-components/refs/example.md` | `refs/server-components.md` | carry |
| `nextjs-server-components/refs/composition-security.md` | `refs/server-components.md` | carry |
| `nextjs-architecture/refs/RSC_BOUNDARIES.md` | `refs/server-components.md` | carry; shared ref gets single home |
| `nextjs-data-fetching/SKILL.md` | `SKILL.md` P0 Data Fetching & Access | carry |
| `nextjs-data-fetching/refs/usage-examples.md` | `refs/data-fetching.md` | carry |
| `nextjs-data-access-layer/SKILL.md` | `SKILL.md` P0 Data Fetching & Access plus `refs/data-fetching.md` | merge |
| `nextjs-data-access-layer/refs/implementation.md` | `refs/data-fetching.md` DAL section | carry |
| `nextjs-data-access-layer/refs/patterns.md` | `refs/data-fetching.md` DAL section | carry or drop with reason; orphan |
| `nextjs-app-router/SKILL.md` | `SKILL.md` P0 App Router Conventions | carry |
| `nextjs-app-router/refs/implementation.md` | `refs/app-router.md` | carry |
| `nextjs-app-router/refs/SELF_HOSTING.md` | `refs/app-router.md` Self-Hosting section | carry |
| `nextjs-rendering/SKILL.md` | `SKILL.md` P1 Rendering & Caching plus `refs/rendering-and-caching.md` | merge |
| `nextjs-rendering/refs/strategy-matrix.md` | `refs/rendering-and-caching.md` Strategy Matrix section | carry |
| `nextjs-rendering/refs/implementation.md` | `refs/rendering-and-caching.md` | carry |
| `nextjs-rendering/refs/implementation-details.md` | `refs/rendering-and-caching.md` | carry |
| `nextjs-rendering/refs/scaling-patterns.md` | `refs/rendering-and-caching.md` Scaling section | carry |
| `nextjs-rendering/refs/SUSPENSE_BAILOUT.md` | `refs/rendering-and-caching.md` Suspense section | carry or drop with reason; orphan |
| `nextjs-caching/SKILL.md` | `SKILL.md` P1 Rendering & Caching plus `refs/rendering-and-caching.md` | merge |
| `nextjs-caching/refs/implementation.md` | `refs/rendering-and-caching.md` Caching section | carry |
| `nextjs-caching/refs/CACHE_COMPONENTS.md` | `refs/rendering-and-caching.md` Cache Components / PPR section | carry |
| `nextjs-authentication/SKILL.md` | `SKILL.md` P0 Security & Auth plus `refs/security.md` | merge |
| `nextjs-authentication/refs/implementation.md` | `refs/security.md` Auth section | carry |
| `nextjs-authentication/refs/auth-implementation.md` | `refs/security.md` Auth section | carry |
| `nextjs-security/SKILL.md` | `SKILL.md` P0 Security & Auth plus `refs/security.md` | merge |
| `nextjs-security/refs/implementation.md` | `refs/security.md` | carry |
| `nextjs-pages-router/SKILL.md` | `refs/pages-router.md` | carry as legacy router guidance |
| `nextjs-pages-router/refs/implementation.md` | `refs/pages-router.md` | carry |
| `nextjs-pages-router/refs/server-side-props.md` | `refs/pages-router.md` | carry |
| `nextjs-pages-router/refs/feature-sliced-design-pages.md` | `refs/pages-router.md` or `refs/architecture.md` | carry or drop with reason; orphan |
| `nextjs-server-actions/SKILL.md` | `SKILL.md` P1 Server Actions plus `refs/server-actions.md` | carry |
| `nextjs-server-actions/refs/secure-actions.md` | `refs/server-actions.md` with cross-ref to `refs/security.md` | carry |
| `nextjs-optimization/SKILL.md` | `refs/styling-and-optimization.md` Optimization section | merge |
| `nextjs-optimization/refs/example.md` | `refs/styling-and-optimization.md` Optimization section | carry |
| `nextjs-styling/SKILL.md` | `refs/styling-and-optimization.md` Styling section | merge |
| `nextjs-styling/refs/{implementation,scss,ant-design,tailwind}.md` | `refs/styling-and-optimization.md` Styling sections | carry |
| `nextjs-testing/SKILL.md` | `refs/testing.md` | carry |
| `nextjs-testing/refs/implementation.md` | `refs/testing.md` | carry |
| `nextjs-architecture/SKILL.md` | `refs/architecture.md` | carry |
| `nextjs-architecture/refs/implementation.md` | `refs/architecture.md` | carry |
| `nextjs-architecture/refs/fsd-structure.md` | `refs/architecture.md` FSD Structure section | carry |
| `nextjs-architecture/refs/BUNDLING.md` | `refs/architecture.md` Bundling section | carry |
| `nextjs-architecture/refs/RUNTIME_SELECTION.md` | `refs/architecture.md` Runtime section, or `refs/rendering-and-caching.md` if content fits better | carry |
| `nextjs-architecture/refs/DEBUG_TRICKS.md` | `refs/architecture.md` Debug section, or `refs/tooling.md` if content fits better | carry |
| `nextjs-i18n/SKILL.md` | `refs/i18n.md` | carry |
| `nextjs-i18n/refs/{implementation,next-intl,react-intl}.md` | `refs/i18n.md` | carry |
| `nextjs-state-management/SKILL.md` | `refs/state-management.md` | carry |
| `nextjs-state-management/refs/{implementation,redux,zustand,url-state}.md` | `refs/state-management.md` | carry |
| `nextjs-tooling/SKILL.md` | `refs/tooling.md` | merge |
| `nextjs-tooling/refs/implementation.md` | `refs/tooling.md` | carry |
| `nextjs-upgrade/SKILL.md` | `refs/tooling.md` Upgrades section | merge |
| `nextjs-upgrade/refs/example.md` | `refs/tooling.md` Upgrades section | carry |
| All 18 `nextjs-*/evals/evals.json` | `archive/nextjs/nextjs-*/evals/evals.json` | archive as-is; no content carried |

High-risk rows: orphaned refs `data-access-layer/refs/patterns.md`,
`rendering/refs/SUSPENSE_BAILOUT.md`, and `pages-router/refs/feature-sliced-design-pages.md`;
shared ref `nextjs-architecture/refs/RSC_BOUNDARIES.md`; the `git mv` archive; regenerated
`_INDEX.md`; stale links to archived paths.

---

## 3. Execution

### Phase 1 - Build `SKILL.md` and the 13 refs

Follow `.compress.md` Steps 1-6. For each ref, read all mapped sources in §2 in full, then write
the merged ref: deduplicate, resolve wording conflicts toward the strongest rule, keep every
concrete code example, rewrite stale examples to current Next 15/16 idioms where the sources point
there, and add a one-line intro per `##` section. For the merged refs
`rendering-and-caching`, `styling-and-optimization`, `security`, and `data-fetching`, use clear
`##` section dividers so each former skill's content is locatable.

Write `SKILL.md` last, once the refs exist. Its frontmatter must use `name: nextjs`, an
exemplar-voice description, union trigger files from the source globs, and high-signal keywords.
Its body must include a Router Decision preamble, P0/P1 rule blocks, a deduplicated Anti-Patterns
list, and priority-grouped References.

Add nothing not traceable to a source, except connective Router Decision text and the Phase 4
decision tables/cross-references that organize existing options.

### Phase 2 - Coverage-audit gate

Re-walk the §2 trace. For every source row, confirm each meaningful rule, example, and anti-pattern
is present in its destination or recorded as a deliberate drop with a stated reason. Pay special
attention to the orphaned refs and shared ref. Do not archive anything until this passes.

### Audit Result

- Status: `pending`
- Gaps fixed: `pending`
- Deliberate drops: `pending`

### Phase 3 - Regenerate `_INDEX.md` and archive the 18 folders

Regenerate `standards/nextjs/_INDEX.md` to the AUTO-GENERATED format used by flutter/react: File
Match table, Loading Instructions block, and an Archived note reproducing the §2 trace so a
reviewer can verify no rule was lost.

Use `git mv` to move each `standards/nextjs/nextjs-*/` folder to `archive/nextjs/nextjs-*/`
verbatim. After the move, `standards/nextjs/` must contain only `SKILL.md`, `_INDEX.md`, and
`refs/`.

Confirm the `cook/SKILL.md` Next.js domain row resolves to `standards/nextjs/_INDEX.md` and does
not instruct the router to load `nextjs/<skill>/SKILL.md` sub-folders. Verify only; no change is
expected.

### Phase 4 - Ref conflict/gap fixes

Add the decision guidance and cross-references the merged refs need so no reader is left with an
ambiguous choice or a rule that breaks when read in isolation:

- `rendering-and-caching.md`: one decision table mapping data freshness to strategy to cache directive (`force-cache`, `revalidate: N`, `no-store`, `'use cache'`).
- `styling-and-optimization.md`: confirm `next/font` and image-CLS guidance has a single owner after the merge; the Library Selection verdict table is the styling decision anchor.
- `state-management.md`: a "which state tool" decision note covering URL, server-cache, client store, and legacy Redux.
- Cross-references: `data-fetching` ↔ `rendering-and-caching` for revalidation; `security` ↔ `server-actions` for action validation; `server-components` ↔ `architecture` for RSC_BOUNDARIES.

Re-read each merged ref in full to confirm coherence: no mid-section splices and no dangling links
to archived paths.

### Wrap-up - CHANGELOG

Update `CHANGELOG.md` newest first, `[pending] - 2026-05-21`, describing the 18 → 1+13
consolidation, the merges, the three orphan carries, the Next 15/16 modernizations, and the archive
to `archive/nextjs/`. Match the flutter consolidation entry's voice.

---

## 4. Guardrails

- Allowed paths: `standards/nextjs/`, `archive/nextjs/`, `CHANGELOG.md`, `verify/verify-[11].md`.
- Verify only: `cook/SKILL.md`.
- Do not edit unrelated files or redesign outside this task.
- Do not edit other domains, including `standards/{dart,typescript,global,database,graphql,flutter,react,review}/`.
- Do not silently drop content; every removal, merge, or archive must appear in §2 and the audit result.
- No source file is deleted; superseded folders are moved with `git mv` to preserve history.
- The coverage gate is hard; no folder moves until Phase 2 passes.
- Read the three orphaned refs in full before their folders move.
- Use repo generators/scripts for generated files.
- Stop and ask if concurrent user changes directly conflict.

---

## 5. Success Criteria

### `SKILL.md`

- [ ] `standards/nextjs/SKILL.md` exists with `name: nextjs`, exemplar-voice description, and union triggers.
- [ ] It carries a Router Decision preamble and the P0/P1 blocks, each with a `Detail -> refs/...` pointer.
- [ ] It has one merged, deduplicated Anti-Patterns list.
- [ ] It has a References section listing all 13 refs, priority-grouped.

### `refs/`

- [ ] All 13 refs listed in §1 exist under `standards/nextjs/refs/`, flat with no nested folders.
- [ ] `security.md` contains the merged authentication and security content.
- [ ] `data-fetching.md` contains the DAL content, including orphaned `patterns.md` or a recorded drop reason.
- [ ] `rendering-and-caching.md` contains rendering strategy content, orphaned `SUSPENSE_BAILOUT.md` or a recorded drop reason, and the 4-layer caching content.
- [ ] `styling-and-optimization.md` contains styling and optimization content with a single owner for `next/font`.
- [ ] `tooling.md` contains upgrade/codemod content as a section.
- [ ] `server-components.md` is the single home of RSC_BOUNDARIES; `architecture.md` cross-references it.
- [ ] `pages-router.md` or `architecture.md` carries orphaned `feature-sliced-design-pages.md` or records a drop reason.

### Coverage Gate

- [ ] Every §2 source row is confirmed present in its destination or recorded as a deliberate drop with reason.
- [ ] High-risk rows were read in full and handled explicitly.
- [ ] The Audit Result subsection records pass/fail, gaps fixed, and deliberate drops.

### Archive And Routing

- [ ] `archive/nextjs/` exists at the repo root with all 18 `nextjs-*/` folders verbatim.
- [ ] No `nextjs-*/` subfolders remain under `standards/nextjs/`.
- [ ] The move used `git mv`.
- [ ] `_INDEX.md` is regenerated to AUTO-GENERATED format with File Match table, Loading Instructions, and an Archived note reproducing the §2 trace.
- [ ] `cook/SKILL.md` Next.js row resolves to `standards/nextjs/_INDEX.md` and has no stale sub-skill loading instruction.

### Conflict And Gap Fixes

- [ ] `rendering-and-caching.md` has a freshness -> strategy -> cache-directive decision table.
- [ ] `styling-and-optimization.md` has no duplicated `next/font` or image guidance after merge.
- [ ] `state-management.md` has a "which state tool" decision note with a default.
- [ ] Cross-references are added between the interlocking refs listed in Phase 4.
- [ ] Each merged ref is re-read in full; no dangling links point to archived paths.

### No Loss / No Unintended Changes

- [ ] Target files/actions in §1 are complete.
- [ ] Every §2 source row is accounted for or deliberately dropped with reason.
- [ ] Required indexes/docs/changelog/routing are updated.
- [ ] Verification command(s): `pending`.
- [ ] No unintended files changed; no user changes reverted.
- [ ] All §4 guardrails held.

---

## 6. Notes for Executor

- Work in order: trace, edit, audit, cleanup, verify.
- Respect the hard gate: build and audit before any `git mv`.
- Read every mapped source in full before writing a ref; the depth lives in the refs, not only the old `SKILL.md` bodies.
- The four merged refs each pull from two former skills; read both sides before merging.
- Carry stale-source rules but write examples to the current Next 15/16 idioms the sources already point toward; record modernizations in `CHANGELOG.md`.
- `evals/evals.json` files carry no rules; archive them as-is.
- After Phase 1, read each new ref in full for coherence and stale links.
- Use `git mv` for the archive so the diff is reviewable as renames.
- Prefer narrow edits over broad rewrites.
- Record deviations, failed checks, and follow-ups here.
