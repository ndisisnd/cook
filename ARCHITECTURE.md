# Architecture

## Overview

Cook is a keyword-driven standards orchestrator with a cache-first control flow. Cook resolves observable signals, checks a fingerprint cache before any classification, and compiles a single standards payload from the matching rule libraries under `standards/`. The compiled output is deterministic and model-free on cache hits.

```
SKILL.md (cook)               thin entry point: identity + pointer
├── refs/
│   └── protocol-cook.md      full operational protocol (mode table, Steps 0–6)
├── vocab/
│   ├── intent-vocabulary.json   intent label constraints
│   └── tag-vocabulary.json      canonical tag set + routes_to mappings
├── scripts/
│   ├── cook_cache.py            resolver: fingerprint, lookup, write, heal
│   ├── cook_compile.py          compiler: dedup, bucket, concatenate
│   └── check_index_routes.py    CI validator: _INDEX.md route integrity
└── standards/
    ├── global/          universal P0 rules + concern refs (includes general security ref)
    ├── security/        Security standards library (core/ + owasp/); superset of global refs/security.md
    ├── flutter/         Flutter/Dart UI
    ├── dart/            Dart 3 language
    ├── swift/           Swift 6 language
    ├── macos/           macOS app platform (SwiftUI/AppKit) — pairs with swift
    ├── nextjs/          Next.js App Router
    ├── react/           React (non-Next)
    ├── css/             CSS presentation layer (cascade, layout, theming) + Tailwind ref
    ├── typescript/      TypeScript 5 language
    ├── nodejs/          Node.js runtime (event loop, streams, process lifecycle)
    ├── database/        PostgreSQL + Redis
    ├── supabase/        Supabase platform (RLS, keys, Edge functions) — co-loads with database
    └── graphql/         GraphQL schema + resolvers
```

Each `standards/` folder contains a `SKILL.md`, an `_INDEX.md` (concern/ref routing table), and a `refs/` directory of detailed ref files.

---

## Protocol

Step 0 intercepts the telemetry management flags (`--enable-telemetry`,
`--disable-telemetry`, `--status`) before any routing — see
[Telemetry](#telemetry). Otherwise cook operates in three control-flow paths,
selected at Step 1:

| Path | Condition | LLM? | Cache write? |
|---|---|---|---|
| **Cache hit** | fingerprint present and fresh | No | No |
| **Miss** | no cache entry or stale | Yes (classify only) | Yes |
| **Fallback** | cache file corrupt | No | No |

### Step 1 — Resolve and branch

Run `cook_cache.py lookup` to build a fingerprint from raw observable signals (files, frameworks, domain hints, concern hints) and check the cache. Extensions are emitted as signals for classification but are not part of the fingerprint.

- **`hit`** — routing is cached and fresh. Skip to Step 2 then Step 6. No LLM.
- **`miss` | `stale`** — continue to classification (Step 1c).
- **`fallback`** — cache corrupt. Use `signals.domain_hints` for greedy broad routing. Skip `write`/`heal`.

On a **miss**, classify the intent against `vocab/intent-vocabulary.json` and canonicalize signals onto tags from `vocab/tag-vocabulary.json`. These `canonical_tags` are the only input to Steps 3–4. Tags not in the vocabulary are dropped.

### Step 2 — Load global P0 (always)

Load `standards/global/SKILL.md`. Unconditional — applies on every path including fallback and weak classification.

### Step 3 — Match global concerns

For each `canonical_tag` routing to a `concern:*` target, load the matched ref under `standards/global/refs/`. On `fallback: true`, load the full concern set.

### Step 4 — Match domains

For each `canonical_tag` routing to a `domain:*` target, load that domain's `SKILL.md` plus matched `refs/*.md`. Multiple domains may match simultaneously. On `fallback: true`, load all domains in `signals.domain_hints`.

### Step 5 — Write cache (miss path only)

Run `cook_cache.py write` with the full skills path list, canonical tags, intent, confidence, and per-index checksums. The entry records the complete routing; read failures are not routing failures and do not suppress the write.

### Step 6 — Compile and self-heal

Run `cook_compile.py --out <file>` with the path list from Steps 2–4 (or `routing.skills` on a hit). The compiler deduplicates, buckets by layer (Universal → Domain → Concern), strips YAML frontmatter, concatenates with terse section headers, and writes the assembled markdown to the `--out` file. Stdout is a compact JSON summary envelope: `path`, `bytes`, `sections`, `degraded`, `metadata` — the payload content never transits the model's context inline.

After compiling, run `cook_cache.py heal` to stamp the compiler's `degraded` list onto the cache entry, except on the corrupt-cache fallback path where no trusted entry exists. On a cache hit this clears previously-flagged files that now read and sets newly missing ones — keeping the entry current without re-classification.

Return the summary envelope (path + sections + degraded) to the invoking agent — never the payload content itself; the invoker reads the payload file. A non-empty `degraded` is a partial load; surviving sections are still delivered and P0 always loads.

---

## Args

Cook supports three invocation modes, selected by the presence of flags and/or prose arguments:

| Mode | Condition | Auto-detect? | P0 loaded? | Cache participates? |
|---|---|---|---|---|
| `auto` | `/cook` (no args) | yes | yes (always) | yes (signals fingerprint) |
| `explicit-flags` | `/cook --security`, `/cook --react --nextjs` | no | **no** | yes (signals + flags fingerprint) |
| `explicit-prose` | `/cook refactor OAuth callback`, `/cook --react fix re-renders` | no | **no** | **no** |

**"Any explicit args"** (flags, prose, or both) is the single break-point for
P0 and auto-detection. The contract is "load exactly what I named."

**Simple flags** are validated against `valid_flags()`, which strips any
`concern:` / `domain:` / `shelf:` prefix from every `routes_to` target in
`vocab/tag-vocabulary.json`. `cook_cache.py` computes this at runtime — never
from a hard-coded list.

**Sub-ref flags** use the format `--<domain>:<ref>`. `valid_domain_flags()`
derives the allowed domain part from `domain:*` targets in the vocab;
`valid_sub_flags(domain)` enumerates actual `.md` file stems under
`standards/<domain>/refs/` at runtime. Sub-ref flags load only the named ref
file — the domain SKILL.md does not auto-load.

**`--global`** routes to `shelf:global` in the vocab, loading
`standards/global/SKILL.md` + every `standards/global/refs/*.md` (P0 +
all concern refs). It is the only explicit-mode path that loads the P0 floor.

**Cache-key extension.** For `explicit-flags` invocations the fingerprint basis
is extended to `(signals, sorted(flags))`. Auto-mode entries (no flags) keep
their byte-identical basis, so existing cache entries remain valid after the
upgrade with no flush. Flag-only invocations with the same flags on the same
signal surface hash to the same fingerprint; different flags on the same surface
produce distinct entries. Prose is deliberately excluded from the key: there is
no way to compute a deterministic key from prose without either requiring
verbatim string equality (rephrasings miss) or normalising with an LLM (which
defeats the cache's core guarantee that a hit never wakes the model).

---

## Skills

| Skill | Description |
|---|---|
| cook | Entry-point orchestrator: cache-first routing, classification, and payload compilation. |
| global | Universal P0 rules that apply to every task; concern refs are loaded on top by cook. Includes `refs/security.md`, a general-purpose security standard usable standalone. |
| security | Comprehensive security standards library. Three always-apply P0 rules (no hardcoded credentials, approved crypto, certificate hygiene) plus 30+ concern-specific refs and 100+ OWASP cheat sheets. Use for security-focused work; `global/refs/security.md` is the lighter standalone alternative. |
| flutter | Flutter/Dart UI standards covering widgets, state management, navigation, architecture, performance, and testing. |
| dart | Dart 3.x language standards: null safety, patterns, sealed classes, records, class modifiers, naming, immutability, collections, async, and import organisation. |
| swift | Swift 6.x language standards: optionals, error handling, strict concurrency (actors, Sendable, @MainActor), value types, protocols/generics, ARC, naming, and access control. Language-only; pairs with macos for platform concerns. |
| macos | macOS app development standards: SwiftUI/AppKit app structure, scenes/windows, menu bar apps, App Sandbox/TCC, signing/notarization, distribution, persistence choice, localization, and HIG conventions. Scoped to macOS only (not iOS/iPadOS/watchOS/visionOS). |
| nextjs | Next.js App Router standards: RSC boundaries, server data access, async route APIs, Server Actions, rendering/cache strategy, and Pages Router awareness. |
| react | React + TypeScript standards: hook rules, component structure, prop typing, and boundary safety for non-Next.js projects. |
| css | Lightweight, principle-driven CSS presentation-layer standards — the SKILL favours judgment over rigid rules: six battle-tested principles (low specificity, scope by default, tokenize, Flexbox/Grid, platform-first, compose over override) + a minimal accessibility/security floor, with depth (architecture, layout, theming, performance, accessibility, tailwind, tooling, security) pushed to on-demand refs. Co-loads with framework shelves. |
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
| `vocab/tag-vocabulary.json` | Canonical tag set. Each tag carries a `routes_to` field (`concern:*` or `domain:*`) that drives Steps 3–4. Tags not in this file are dropped at canonicalization. |

---

## Scripts

| Script | Role |
|---|---|
| `scripts/cook_cache.py` | Implements the resolver (file-derivation cascade, fingerprint, lookup), cache writer (atomic tmp+rename, checksum stamps), and `heal` sub-command (degraded-flag reconciliation). |
| `scripts/cook_compile.py` | Deterministic compiler: dedup, layer bucketing, frontmatter stripping, concatenation, degraded tracking. No LLM involvement. |
| `scripts/check_index_routes.py` | CI / pre-commit validator. Fails the build if any `_INDEX.md` route target points at a missing file — upstream prevention for broken routing. |
| `scripts/cook_telemetry.py` | Optional usage log (`enable` / `disable` / `status` / `record`). Off by default; stores `telemetry/telemetry.json` under the cook root. `record` is a silent no-op when disabled and never fails a fire. |

---

## Telemetry

An **opt-in, off-by-default** log of what cook fires. It observes only — it never
changes routing, loading, or the return envelope. `refs/telemetry.md` is the
protocol contract; `scripts/cook_telemetry.py` does the mechanical work.

- **State + storage** — a single JSON file, `telemetry/telemetry.json`, holding
  the `enabled` flag and the `records` array together, so state persists across
  fires. Gitignored and not shipped by the installer; created lazily.
- **Scope — local-first** — resolution prefers `<project>/telemetry/telemetry.json`
  (created by `--init`) over the global `<cook-root>/telemetry/telemetry.json`
  (peer to `.agent-skills/`). A repo that has been `--init`-ed keeps its own log
  and its cook calls record there; every other repo falls back to the global
  store. Every telemetry call takes `--project <dir>` for resolution; `--global`
  forces the install store. This mirrors the local-vs-global pref pattern.
- **Management flags** (Step 0) — `--init`, `--enable-telemetry`,
  `--disable-telemetry`, `--status` are intercepted before routing. Alone they
  run and terminate; combined with load args they run first, then the remaining
  args load normally. `--init` creates + enables the local store (idempotent).
- **Record step** (end of Step 6) — best-effort `record` appends one entry per
  successful fire: `ts`, `intent` (a `vocab/intent-vocabulary.json` label),
  `prompt` (the raw task summary), `mode`, and `standards` (folder → the
  standards loaded within it, `SKILL` or `refs/<name>`). A no-op when disabled.
- **`--status`** — prints enabled state, total fires, time window, and ranked
  breakdowns by individual standard, folder, and intent.

---

## Refs

### global

- `refs/architecture.md`: Component and state structure rules across layers.
- `refs/api-design.md`: HTTP verb semantics, status codes, request/response shape.
- `refs/error-handling.md`: Error architecture, propagation, and user-facing error design.
- `refs/security.md`: General-purpose security rules (OWASP Top 10 quick-ref, parameterized queries, secret management, input validation). Usable standalone — lighter alternative to the full `security/` shelf.
- `refs/auth.md`: Authentication and authorisation patterns.
- `refs/performance.md`: Performance workflow and profiling discipline.
- `refs/debug.md`: Scientific debugging method and instrumentation rules.
- `refs/cicd.md`: CI/CD pipeline and deployment configuration.

### security

`standards/security/` uses two subdirectories rather than a flat `refs/` layout:

**`core/`** — language-agnostic, always-applicable rules (23 files):
- `hardcoded-credentials.md`, `crypto-algorithms.md`, `digital-certificates.md`: always-apply P0 rules checked on every task.
- Concern refs: additional cryptography, API/web services, auth/MFA, authorization/access control, client-side web security, cloud/Kubernetes, data storage, DevOps/CI/CD/containers, file handling, framework-and-languages, IaC, input validation/injection, logging, MCP/AI security, mobile apps, privacy/data protection, C/C++ safe functions, session management/cookies, supply chain, XML/serialization.

**`owasp/`** — detailed OWASP cheat sheet guidance (90+ files): authentication, authorization, injection, XSS/DOM-XSS, CSRF, session management, crypto storage, transport security, HTTP headers, OAuth2, JWT, SAML, IDOR, mass assignment, file upload, XXE, deserialization, Docker, Kubernetes, CI/CD, microservices, zero trust, and framework-specific sheets (Node.js, Django, Java, PHP, Ruby, .NET).

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

### swift

- `refs/concurrency.md`: Swift 6 migration, actors and reentrancy, Sendable/sending, structured vs unstructured tasks, AsyncSequence/AsyncStream, continuation bridging, deinit isolation.
- `refs/memory-management.md`: ARC model, weak/unowned decisions, delegate and parent/child patterns, retain-cycle sources, Memory Graph Debugger.
- `refs/testing.md`: Swift Testing (@Test/#expect/#require, parameterized, traits), what stays XCTest, protocol-based fakes, migration mapping.
- `refs/tooling.md`: SwiftLint + swift-format, SPM/Package.resolved hygiene, Xcode build settings, CI ordering.
- `refs/performance.md`: Existential boxing vs generics, ARC traffic, string/collection costs, devirtualization, build-time hygiene, Instruments/OSSignposter/MetricKit.
- `refs/interop.md`: CoreFoundation ownership (Unmanaged), pointer lifetime, Obj-C nullability, @objc/dynamic discipline, block-based KVO.

### macos

- `refs/architecture-and-state.md`: Observation framework internals, @State/@Bindable ownership, @Environment/@Entry DI, MVVM tradeoffs, SwiftData vs Core Data decision.
- `refs/windows-and-scenes.md`: Scene selection, window/menu-bar management, the Settings-from-accessory recipe, commands and focus/responder bridging, document apps.
- `refs/sandbox-and-tcc.md`: App Sandbox, entitlement reference, hardened runtime exceptions, Keychain, TCC grant flows, code-signing basics, XPC security boundaries.
- `refs/distribution.md`: Signing certificates, notarytool/stapling, MAS constraints, Sparkle 2, universal binaries, dmg/pkg packaging.
- `refs/performance-accessibility.md`: Instruments templates, main-thread/beachball hygiene, background work, launch-time optimization, VoiceOver, Dynamic Type/@ScaledMetric.
- `refs/localization.md`: String Catalogs, plural rules, FormatStyle, pseudo-localization, RTL, testing with -AppleLanguages.

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

### css

- `refs/architecture.md`: Cascade layers (`@layer`), methodology selection (BEM/ITCSS/utility-first/CSS Modules), `@scope`, specificity strategy, and file organization.
- `refs/layout.md`: Flexbox vs Grid, subgrid, container queries, logical properties, intrinsic sizing, `aspect-ratio`, fluid `clamp()` type, and breakpoint strategy.
- `refs/theming.md`: Custom-property token layering, `color-scheme`/`light-dark()` dark mode, `oklch()`/`color-mix()`/relative colour, and `@property`.
- `refs/performance.md`: Compositor-only animation, `contain`/`content-visibility`, `will-change` discipline, critical CSS, and web-font loading.
- `refs/accessibility.md`: `:focus-visible`, `prefers-reduced-motion`, `forced-colors`/`prefers-contrast`, contrast, target sizes, and screen-reader-only utilities.
- `refs/tailwind.md`: TailwindCSS (v4 CSS-first `@theme` + v3 config), utility-first discipline, `cn()`/`tailwind-merge`, `cva` variants, arbitrary values, and dark mode.
- `refs/tooling.md`: Stylelint, Prettier, PostCSS/Lightning CSS, `browserslist`, and Sass `@use`/`@forward` and native nesting.
- `refs/security.md`: CSS injection, attribute-selector data exfiltration, third-party/`@import` risk, clickjacking overlays, and user-generated-style sanitization.

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
