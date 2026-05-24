# Architecture

## Overview

Cook is a keyword-driven standards orchestrator with a cache-first control flow. Cook resolves observable signals, checks a fingerprint cache before any classification, and compiles a single standards payload from the matching rule libraries under `standards/`. The compiled output is deterministic and model-free on cache hits.

```
SKILL.md (cook)
├── vocab/
│   ├── intent-vocabulary.json   intent label constraints
│   └── tag-vocabulary.json      canonical tag set + routes_to mappings
├── scripts/
│   ├── cook_cache.py            resolver: fingerprint, lookup, write, heal
│   ├── cook_compile.py          compiler: dedup, bucket, concatenate
│   └── check_index_routes.py    CI validator: _INDEX.md route integrity
└── standards/
    ├── global/          universal P0 rules + concern refs
    ├── review/          adversarial review skill
    ├── flutter/         Flutter/Dart UI
    ├── dart/            Dart 3 language
    ├── nextjs/          Next.js App Router
    ├── react/           React (non-Next)
    ├── typescript/      TypeScript 5 language
    ├── nodejs/          Node.js runtime (event loop, streams, process lifecycle)
    ├── database/        PostgreSQL + Redis
    ├── supabase/        Supabase platform (RLS, keys, Edge functions) — co-loads with database
    └── graphql/         GraphQL schema + resolvers
```

Each `standards/` folder contains a `SKILL.md`, an `_INDEX.md` (concern/ref routing table), and a `refs/` directory of detailed ref files.

---

## Protocol

Cook operates in three control-flow paths, selected at Step 1:

| Path | Condition | LLM? | Cache write? |
|---|---|---|---|
| **Cache hit** | fingerprint present and fresh | No | No |
| **Miss** | no cache entry or stale | Yes (classify only) | Yes |
| **Fallback** | cache file corrupt | No | No |

### Step 1 — Resolve and branch

Run `cook_cache.py lookup` to build a fingerprint from raw observable signals (files, frameworks, domain hints, concern hints) and check the cache. Extensions are emitted as signals for classification but are not part of the fingerprint.

- **`hit`** — routing is cached and fresh. Skip to Step 3 then Step 7. No LLM.
- **`miss` | `stale`** — continue to classification (Step 1c).
- **`fallback`** — cache corrupt. Use `signals.domain_hints` for greedy broad routing. Skip `write`/`heal`.

On a **miss**, classify the intent against `vocab/intent-vocabulary.json` and canonicalize signals onto tags from `vocab/tag-vocabulary.json`. These `canonical_tags` are the only input to Steps 4–5. Tags not in the vocabulary are dropped.

### Step 2 — Review intent?

If intent is `review-code`, derive the code surface (frontend / backend / full-stack, with `security-sensitive` appended when relevant signals appear), load `standards/review/SKILL.md`, write the cache entry, and stop.

### Step 3 — Load global P0 (always)

Load `standards/global/SKILL.md`. Unconditional — applies on every path including fallback and weak classification.

### Step 4 — Match global concerns

For each `canonical_tag` routing to a `concern:*` target, load the matched ref under `standards/global/refs/`. On `fallback: true`, load the full concern set.

### Step 5 — Match domains

For each `canonical_tag` routing to a `domain:*` target, load that domain's `SKILL.md` plus matched `refs/*.md`. Multiple domains may match simultaneously. On `fallback: true`, load all domains in `signals.domain_hints`.

### Step 6 — Write cache (miss path only)

Run `cook_cache.py write` with the full skills path list, canonical tags, intent, confidence, and per-index checksums. The entry records the complete routing; read failures are not routing failures and do not suppress the write.

### Step 7 — Compile and self-heal

Run `cook_compile.py` with the path list from Steps 3–5 (or `routing.skills` on a hit). The compiler deduplicates, buckets by layer (Universal → Domain → Concern), strips YAML frontmatter, and concatenates with terse section headers. Output is JSON: `content`, `degraded`, `metadata`.

After compiling, run `cook_cache.py heal` to stamp the compiler's `degraded` list onto the cache entry, except on the corrupt-cache fallback path where no trusted entry exists. On a cache hit this clears previously-flagged files that now read and sets newly missing ones — keeping the entry current without re-classification.

Return the JSON envelope to the invoking agent. A non-empty `degraded` is a partial load; surviving sections are still delivered and P0 always loads.

---

## Skills

| Skill | Description |
|---|---|
| cook | Entry-point orchestrator: cache-first routing, classification, and payload compilation. |
| global | Universal P0 rules that apply to every task; concern refs are loaded on top by cook. |
| review | Adversarial review that detects bugs, design gaps, and security risks; auto-fix or eval-report output. |
| flutter | Flutter/Dart UI standards covering widgets, state management, navigation, architecture, performance, and testing. |
| dart | Dart 3.x language standards: null safety, patterns, sealed classes, records, class modifiers, naming, immutability, collections, async, and import organisation. |
| nextjs | Next.js App Router standards: RSC boundaries, server data access, async route APIs, Server Actions, rendering/cache strategy, and Pages Router awareness. |
| react | React + TypeScript standards: hook rules, component structure, prop typing, and boundary safety for non-Next.js projects. |
| typescript | TypeScript 5.x language standards: type safety, narrowing, generics, modules, and async code. |
| nodejs | Node.js runtime standards: event-loop safety, streams/backpressure, process lifecycle, Buffer safety, runtime pinning, installs, env loading, and logging. |
| database | Database standards for PostgreSQL schema/migration/query design and Redis caching and cache invalidation. |
| supabase | Supabase platform standards: Row-Level Security, the anon/service_role key boundary, Postgres/Edge function security, Storage, Realtime, and the CLI migration workflow. Co-loads with database on Supabase Postgres work. |
| graphql | GraphQL schema design and resolver conventions: naming, nullability, types, input objects, mutations, queries, and operation structure. |

---

## Vocabulary

| File | Role |
|---|---|
| `vocab/intent-vocabulary.json` | Exhaustive list of valid intent labels. Classification is constrained to this set. |
| `vocab/tag-vocabulary.json` | Canonical tag set. Each tag carries a `routes_to` field (`concern:*` or `domain:*`) that drives Steps 4–5. Tags not in this file are dropped at canonicalization. |

---

## Scripts

| Script | Role |
|---|---|
| `scripts/cook_cache.py` | Implements the resolver (file-derivation cascade, fingerprint, lookup), cache writer (atomic tmp+rename, checksum stamps), and `heal` sub-command (degraded-flag reconciliation). |
| `scripts/cook_compile.py` | Deterministic compiler: dedup, layer bucketing, frontmatter stripping, concatenation, degraded tracking. No LLM involvement. |
| `scripts/check_index_routes.py` | CI / pre-commit validator. Fails the build if any `_INDEX.md` route target points at a missing file — upstream prevention for broken routing. |

---

## Refs

### global

- `refs/architecture.md`: Component and state structure rules across layers.
- `refs/api-design.md`: HTTP verb semantics, status codes, request/response shape.
- `refs/error-handling.md`: Error architecture, propagation, and user-facing error design.
- `refs/security.md`: UI, API, and auth security rules.
- `refs/auth.md`: Authentication and authorisation patterns.
- `refs/performance.md`: Performance workflow and profiling discipline.
- `refs/debug.md`: Scientific debugging method and instrumentation rules.
- `refs/cicd.md`: CI/CD pipeline and deployment configuration.

### review

- `refs/report-format.md`: Output format, vibecoder field guidance, and severity reference for review reports.
- `refs/review-lenses.md`: Correctness, Security, and Reliability lenses applied during review.

### flutter

- `refs/architecture.md`: Layer separation and feature-first folder structure.
- `refs/cicd.md`: CI/CD pipeline and release configuration.
- `refs/concurrency.md`: Isolates, async, and stream concurrency rules.
- `refs/dependency-injection.md`: DI patterns and service locator conventions.
- `refs/design-system.md`: Design tokens, theming, and widget composition.
- `refs/error-handling.md`: Error propagation and user-facing error handling in Flutter.
- `refs/localization.md`: i18n and l10n setup and ARB file conventions.
- `refs/navigation.md`: GoRouter / AutoRoute patterns and deep-link handling.
- `refs/networking.md`: HTTP client setup, interceptors, and retry strategy.
- `refs/notifications.md`: Push notification setup and permission handling.
- `refs/security.md`: Secure storage, certificate pinning, and obfuscation.
- `refs/state-management.md`: Bloc/Cubit, Riverpod, and GetX conventions.
- `refs/testing.md`: Unit, widget, and integration test conventions.

### dart

- `refs/testing.md`: Dart test conventions and coverage rules.
- `refs/tooling.md`: Dart toolchain, linter, and formatter configuration.

### nextjs

- `refs/app-router.md`: App Router file conventions, layouts, and route handlers.
- `refs/architecture.md`: Project structure and layer boundaries for Next.js apps.
- `refs/data-fetching.md`: Data fetching patterns: fetch, cache, revalidation.
- `refs/i18n.md`: Internationalisation setup for App Router.
- `refs/pages-router.md`: Legacy Pages Router patterns and migration notes.
- `refs/rendering-and-caching.md`: Static, dynamic, and streaming rendering; cache semantics.
- `refs/security.md`: Next.js-specific security: headers, CSRF, server boundary leaks.
- `refs/server-actions.md`: Server Action conventions, validation, and error handling.
- `refs/server-components.md`: RSC rules: data access, serialisation, and client boundary placement.
- `refs/state-management.md`: Client-side state patterns compatible with RSC.
- `refs/styling-and-optimization.md`: CSS Modules, Tailwind, fonts, images, and bundle optimisation.
- `refs/testing.md`: Next.js testing: unit, component, and E2E conventions.
- `refs/tooling.md`: Next.js toolchain: ESLint, TypeScript, and build configuration.

### react

- `refs/component-patterns.md`: Component composition, slot patterns, and API design.
- `refs/hooks.md`: Custom hook rules, dependency arrays, and effect discipline.
- `refs/performance.md`: Memoisation, code splitting, and render optimisation.
- `refs/security.md`: XSS prevention and safe DOM interaction in React.
- `refs/state-management.md`: Local, context, and external store patterns.
- `refs/testing.md`: React Testing Library conventions and coverage rules.
- `refs/tooling.md`: Vite, ESLint, and React toolchain configuration.

### typescript

- `refs/security.md`: Type-safe input validation and injection prevention.
- `refs/testing.md`: TypeScript test patterns and type-level testing.
- `refs/tooling.md`: tsconfig, strict mode, and compiler flag conventions.

### nodejs

- `refs/runtime-safety.md`: Event-loop budget, streams/backpressure, worker threads, Buffer safety, and graceful shutdown.
- `refs/async-errors.md`: Promise rejection lifecycle, callback-boundary throws, global process handlers, and timeout/cancellation mechanics.
- `refs/tooling.md`: Node/package-manager pinning, frozen installs, environment boot validation, and structured logging setup.
- `refs/testing.md`: Node service, CLI, worker, integration, and network-boundary test conventions.

### database

- `refs/postgresql-best-practices.md`: Schema design, constraints, and indexing best practices.
- `refs/postgresql-anti-patterns.md`: Common PostgreSQL mistakes and how to avoid them.
- `refs/postgresql-checklist.md`: Pre-migration and pre-deploy checklist for schema changes.
- `refs/postgresql-implementation.md`: Concrete implementation patterns: transactions, CTEs, batch writes.
- `refs/redis-best-practices.md`: Key design, TTL strategy, and data structure selection.
- `refs/redis-checklist.md`: Pre-deploy checklist for Redis usage.
- `refs/sql-gotchas.md`: SQL edge cases: NULL semantics, type coercion, lock behaviour.

### supabase

- `refs/rls.md`: Row-Level Security — enable-on-create, per-operation policies, `SELECT`+`UPDATE` pairing, `WITH CHECK`, `(select auth.uid())` wrapping, `app_metadata` vs `user_metadata`, indexing predicate columns.
- `refs/keys-and-clients.md`: anon vs service_role boundary, browser/mobile bundle rules, SSR admin-client separation, public-env pitfalls.
- `refs/database-functions.md`: `SECURITY INVOKER`/`SECURITY DEFINER`, `search_path = ''`, schema qualification, RLS helper functions.
- `refs/edge-functions.md`: Deno runtime, `verify_jwt`/in-code auth, project secrets, Postgres connection pooling.
- `refs/migrations.md`: Supabase CLI workflow, RLS-as-SQL, dashboard drift, storage and Realtime policies.
- `refs/checklist.md`: Pre-deploy review checklist for a Supabase change.

### graphql

- `refs/schema-design.md`: Type naming, nullability defaults, and field design rules.
- `refs/performance.md`: DataLoader usage, query complexity limits, and N+1 prevention.
- `refs/security.md`: Depth limits, introspection policy, and auth on resolvers.
- `refs/testing.md`: Schema and resolver testing conventions.
- `refs/tooling.md`: Code generation, linting, and GraphQL toolchain setup.
