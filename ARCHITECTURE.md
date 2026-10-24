# Architecture

## Overview

Cook is a keyword-driven standards orchestrator with a cache-first control flow. Cook resolves observable signals, checks a fingerprint cache before any classification, and compiles a single standards payload from the matching rule libraries under `standards/`. The compiled output is deterministic and model-free on cache hits.

```
SKILL.md (cook)               thin entry point: the one command + the needs_llm branch
├── refs/
│   ├── protocol-cook.md      run command, telemetry flags, needs_llm rule (read when /cook has args)
│   ├── protocol-explicit.md  flag/prose grammar (for parsing by hand; the script does it)
│   ├── protocol-manual.md    step-by-step flow + explicit path-list rules (Codex, humans)
│   └── telemetry.md          opt-in fire log contract
├── vocab/
│   ├── intent-vocabulary.json   intent label constraints
│   └── tag-vocabulary.json      canonical tag set + routes_to mappings
├── scripts/
│   ├── cook_run.py              single-call entry point: the whole pipeline in one process
│   ├── cook_route.py            skill-list rules (auto routes, explicit flags) + --explain reasons
│   ├── cook_cache.py            resolver: fingerprint, lookup, classify, write, heal
│   ├── cook_compile.py          compiler: dedup, bucket, concatenate
│   └── check_index_routes.py    CI validator: _INDEX.md route integrity
└── standards/
    ├── global/          universal P0 rules + concern refs (includes the security ref)
    ├── flutter/         Flutter/Dart UI
    ├── dart/            Dart 3 language
    ├── swift/           Swift 6 language
    ├── ios/             iOS/iPadOS app platform (SwiftUI/UIKit) — pairs with swift
    ├── macos/           macOS app platform (SwiftUI/AppKit) — pairs with swift
    ├── nextjs/          Next.js App Router
    ├── react/           React (non-Next)
    ├── css/             CSS presentation layer (cascade, layout, theming) + Tailwind ref
    ├── typescript/      TypeScript 6 language
    ├── nodejs/          Node.js runtime (event loop, streams, process lifecycle)
    ├── database/        PostgreSQL + Redis
    ├── supabase/        Supabase platform (RLS, keys, Edge functions) — co-loads with database
    └── graphql/         GraphQL schema + resolvers
```

Each `standards/` folder contains a `SKILL.md`, an `_INDEX.md` (concern/ref routing table), and a `refs/` directory of detailed ref files.

The installed tree lives at `~/.claude/skills/cook` and that is the single source
of truth. The installer additionally links `~/.agents/skills/cook` to it so the
OpenAI Codex CLI discovers the same skill from its own search path. One copy on
disk, two agents, no drift.

---

## Protocol

The model runs one command, `scripts/cook_run.py`, and reads one JSON envelope. The script does the resolve, classify, route, compile, cache-write and telemetry work in a single process, importing `cook_cache`, `cook_compile`, `cook_route` and `cook_telemetry` as modules. Every old subcommand still works on its own for Codex and debugging; the step-by-step text is in `refs/protocol-manual.md`.

The only model-side branching is Step 0 (the telemetry management flags `--init`, `--enable-telemetry`, `--disable-telemetry`, `--status`, intercepted before routing; see [Telemetry](#telemetry)) and the `needs_llm` branch below.

| Path | Condition | LLM? | Cache write? |
|---|---|---|---|
| **Cache hit** | fingerprint present and fresh | No | No |
| **Miss** | no cache entry or stale | Only if nothing resolves (`needs_llm`) | Yes |
| **Fallback** | cache file corrupt | No | No |

### What `cook_run.py` does

1. **Resolve.** Builds a fingerprint from raw observable signals (files, frameworks, domain hints, concern hints) and checks the cache. Extensions are emitted as signals for classification but are not part of the fingerprint.
2. **Hit.** The routing is cached and fresh, and the entry stores a finished payload: the script returns that payload with no classification, no compile and no `heal`. A changed source standard, a missing payload file or a changed compiler makes the entry `stale`.
3. **Miss or stale.** Matches the signals against the aliases in `vocab/tag-vocabulary.json`. The resulting canonical tags route to `concern:*` and `domain:*` targets.
4. **Skill list.** `cook_route.py` derives it: global `SKILL.md` (P0, auto mode only), each routed concern ref, each routed domain `SKILL.md` plus the refs its `_INDEX.md` selects by file pattern, content signal (`content:<token>` in a touched source file, scanned once by `scan_contents`) or keyword, plus the shelf's core refs: an `_INDEX.md` line `Core refs (auto mode): ...` (react: hooks, performance, security; typescript: `global/error-handling`) loads whenever that domain routes in auto mode. Aliases match prose, extensions, frameworks and whole path segments, never part of a file name. Explicit flags use the path-list rules in `cook_route.py` instead.
5. **Compile.** `cook_compile.py` deduplicates, buckets by layer (Universal → Domain → Concern), strips YAML frontmatter, concatenates with terse section headers, and writes the markdown and a section manifest. The payload content never transits the model's context.
6. **Persist.** Writes the routing entry with the payload path (miss path only; never on a corrupt cache or for prose). Read failures are not routing failures and do not suppress the write; the compiler's `degraded` list is stamped onto the entry.
7. **Record.** Best-effort telemetry; a failure never changes the exit code or the envelope.

On a corrupt cache (`cache_corrupt: true`) the script routes greedily: P0, every domain in `signals.domain_hints`, and all concern refs. It skips the cache write.

### The `needs_llm` branch

When no `domain:*` route resolves, or shared Apple vocabulary is ambiguous between iOS and macOS, the script stops after classify and returns `needs_llm: true` with `llm_input` (vocab path, raw signals, matched tags). The model picks canonical tags (never invents one) and runs `cook_run.py --resume <fingerprint> --tags <list>`. This is the only two-call path.

### The envelope

`mode`, `status` (`hit|miss|stale|skip|needs_llm`), `fingerprint`, `payload` (`path`, `bytes`, `sections`), `manifest_path`, `sections` (`header`, `rel`, `bytes` per payload section), `degraded`, `dropped_for_budget`, `needs_llm`, `platform_ambiguous`. Optional: `stale_reason`, `llm_input`, `cache_corrupt`, `ignored_tags`, `skills` (`--show-skills`) and `explain` (`--explain`).

Subagents do not get copies of the payload. A caller passes the payload path, and a subagent runs `python3 scripts/cook_compile.py slice --payload <path> --section <header|rel>` to read only the sections it needs (contract: `refs/payload-reuse.md`). `cook_run.py --consumer <label>` tags the telemetry record so `--status` shows reuse against reinjection.

`--explain` adds one object: `loaded` (per file, why it loaded: route tag and matched alias, `_INDEX.md` file pattern or keyword, flag, P0, or "kept from the cached routing entry") and `dropped` (per sibling file in the loaded shelves, why not). It changes no other envelope field and not the payload.

The model returns the envelope (`payload`, `degraded`, `dropped_for_budget`) to the invoking agent, never the payload content. A non-empty `degraded` is a partial load; surviving sections are still delivered and P0 always loads.

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

The model does not parse these args. It passes the text after `/cook` to `cook_run.py --args '<text>'`; the script splits flags from prose (a token that starts with `--` is a flag until a bare `--`) and applies the rules below. `refs/protocol-explicit.md` holds the grammar for parsing by hand.

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
| global | Universal P0 rules that apply to every task; concern refs are loaded on top by cook. Includes `refs/security.md`, a general-purpose security standard; the security home for all stacks. |
| flutter | Flutter/Dart UI standards covering widgets, state management, navigation, architecture, performance, and testing. |
| dart | Dart 3.x language standards: null safety, patterns, sealed classes, records, class modifiers, naming, immutability, collections, async, and import organisation. |
| swift | Swift 6.2+ language standards: optionals, error handling, strict concurrency (actors, Sendable, @MainActor), value types, protocols/generics, ARC, naming, and access control. Language-only; pairs with ios and macos for platform concerns. |
| ios | iOS/iPadOS app development standards: SwiftUI app and scene lifecycle, navigation and sheets, iPad and foldable adaptivity, UI and accessibility, background work, push, Live Activities and widgets, privacy and permissions, sign-in and account deletion, signing and App Store distribution, and UI testing. Scoped to iOS/iPadOS only. |
| macos | macOS 26+ app development standards (Xcode 27): SwiftUI/AppKit app structure, scenes/windows, menu bar apps, App Sandbox/TCC, signing/notarization, distribution, persistence choice, localization, and HIG conventions. Scoped to macOS only (not iOS/iPadOS/watchOS/visionOS). |
| nextjs | Next.js 16.x App Router standards: RSC boundaries, server data access, async route APIs, Server Actions, rendering/cache strategy, and Pages Router awareness. |
| react | React 19.x + React Compiler standards: hook rules, component structure, prop typing, and boundary safety for non-Next.js projects. |
| css | Lightweight, principle-driven CSS presentation-layer standards — the SKILL favours judgment over rigid rules: six battle-tested principles (low specificity, scope by default, tokenize, Flexbox/Grid, platform-first, compose over override) + a minimal accessibility/security floor, with depth (architecture, layout, theming, performance, accessibility, tailwind, tooling, security) pushed to on-demand refs. Co-loads with framework shelves. |
| typescript | TypeScript 6.x language standards (7.x-compatible): type safety, narrowing, generics, modules, and async code. |
| nodejs | Node.js 24 LTS runtime standards: event-loop safety, streams/backpressure, process lifecycle, Buffer safety, runtime pinning, installs, env loading, and logging. |
| database | Database standards for PostgreSQL schema/migration/query design and Redis caching and cache invalidation. |
| supabase | Supabase platform standards: Row-Level Security, the anon/service_role key boundary, Postgres/Edge function security, Storage, Realtime, and the CLI migration workflow. Co-loads with database on Supabase Postgres work. |
| graphql | GraphQL schema design and resolver conventions: naming, nullability, types, input objects, mutations, queries, and operation structure. |

---

## Vocabulary

| File | Role |
|---|---|
| `vocab/intent-vocabulary.json` | Exhaustive list of valid intent labels. Classification is constrained to this set. |
| `vocab/tag-vocabulary.json` | Canonical tag set. Each tag carries a `routes_to` field (`concern:*` or `domain:*`) that drives routing. Tags not in this file are dropped at canonicalization. |

---

## Scripts

| Script | Role |
|---|---|
| `scripts/cook_run.py` | Single-call entry point. Runs lookup, classify, route, compile, cache write and telemetry in one process; owns `--args` parsing, `--resume`, `--show-skills` and `--explain`. |
| `scripts/cook_route.py` | Skill-list rules (auto routes with `_INDEX.md` pattern and keyword matching; explicit-flag path list) and the `explain` reasons. Shared with `verify/routing_parity.py`. |
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
- **Management flags** (Step 0, `refs/protocol-cook.md`) — `--init`, `--enable-telemetry`,
  `--disable-telemetry`, `--status` are intercepted before routing. Alone they
  run and terminate; combined with load args they run first, then the remaining
  args load normally. `--init` creates + enables the local store (idempotent).
- **Record step** (end of every run; `cook_run.py` does it itself) — best-effort `record` appends one entry per
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
- `refs/security.md`: General-purpose security rules (OWASP Top 10 quick-ref, parameterized queries, secret management, input validation). The security home for all stacks.
- `refs/auth.md`: Authentication and authorisation patterns.
- `refs/performance.md`: Performance workflow and profiling discipline.
- `refs/debug.md`: Scientific debugging method and instrumentation rules.
- `refs/cicd.md`: CI/CD pipeline and deployment configuration.
- `refs/crypto.md`: Approved algorithms and modes, key management and rotation, randomness, encryption at rest, TLS, and certificate hygiene.

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

- `refs/language-conventions.md`: Optionals, error handling, value types, protocols/generics, naming, access control, Codable.
- `refs/concurrency.md`: Swift 6 migration, actors and reentrancy, Sendable/sending, structured vs unstructured tasks, AsyncSequence/AsyncStream, continuation bridging, deinit isolation.
- `refs/memory-management.md`: ARC model, weak/unowned decisions, delegate and parent/child patterns, retain-cycle sources, Memory Graph Debugger.
- `refs/testing.md`: Swift Testing (@Test/#expect/#require, parameterized, traits), what stays XCTest, protocol-based fakes, migration mapping.
- `refs/tooling.md`: SwiftLint + swift-format, SPM/Package.resolved hygiene, Xcode build settings, CI ordering.
- `refs/performance.md`: Existential boxing vs generics, ARC traffic, string/collection costs, devirtualization, build-time hygiene, Instruments/OSSignposter/MetricKit.
- `refs/interop.md`: CoreFoundation ownership (Unmanaged), pointer lifetime, Obj-C nullability, @objc/dynamic discipline, block-based KVO.

### macos

- `refs/hig-conventions.md`: Human Interface Guidelines for Mac: Liquid Glass, toolbars, sidebars, `Table`, menus and keyboard shortcuts.
- `refs/architecture-and-state.md`: Observation framework internals, @State/@Bindable ownership, @Environment/@Entry DI, MVVM tradeoffs, SwiftData vs Core Data decision.
- `refs/windows-and-scenes.md`: Scene selection, window/menu-bar management, the Settings-from-accessory recipe, commands and focus/responder bridging, document apps.
- `refs/sandbox-and-tcc.md`: App Sandbox, entitlement reference, hardened runtime exceptions, Keychain, TCC grant flows, code-signing basics, XPC security boundaries.
- `refs/distribution.md`: Signing certificates, notarytool/stapling, MAS constraints, Sparkle 2, universal binaries, dmg/pkg packaging.
- `refs/performance-accessibility.md`: Instruments templates, main-thread/beachball hygiene, background work, launch-time optimization, VoiceOver, Dynamic Type/@ScaledMetric.
- `refs/localization.md`: String Catalogs, plural rules, FormatStyle, pseudo-localization, RTL, testing with -AppleLanguages.

### ios

- `refs/app-lifecycle-and-navigation.md`: App/scene lifecycle, the iOS 27 SDK UIScene mandate, scenePhase, NavigationStack paths, presentation, size classes, iPad and iPhone Duo adaptivity, state restoration, deep and universal links.
- `refs/ui-and-accessibility.md`: Dynamic Type, VoiceOver and assistive settings, Liquid Glass, buttons, bottom sheets, snackbar host pattern, lists and input, haptics, previews.
- `refs/background-and-notifications.md`: BGTaskScheduler task kinds, background URLSession, notification permission, APNs, Live Activities, WidgetKit, App Intents.
- `refs/privacy-and-permissions.md`: Usage strings and prompt timing, ATT, privacy manifests, Keychain and data protection, passkeys, Sign in with Apple, account deletion.
- `refs/distribution.md`: Upload requirements, CI signing with an App Store Connect API key, build and upload, TestFlight, App Review gotchas, release.
- `refs/testing.md`: XCUITest, accessibility audits, snapshot tests, device matrix, launch metrics.

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

- `refs/conventions.md`: Operation structure and naming conventions for queries, mutations and fragments.
- `refs/schema-design.md`: Type naming, nullability defaults, and field design rules.
- `refs/performance.md`: DataLoader usage, query complexity limits, and N+1 prevention.
- `refs/security.md`: Depth limits, introspection policy, and auth on resolvers.
- `refs/testing.md`: Schema and resolver testing conventions.
- `refs/tooling.md`: Code generation, linting, and GraphQL toolchain setup.
