# Cook Flag Reference

Complete list of every valid `/cook` flag. Generated from `vocab/tag-vocabulary.json` and `standards/*/refs/` at runtime — this file is a snapshot; the vocab and disk are the source of truth.

---

## Management

These flags do not load standards — they manage the optional telemetry log and
terminate (unless combined with load args, in which case telemetry runs first).
See [`refs/telemetry.md`](refs/telemetry.md).

| Flag | Action |
|---|---|
| `--init` | Initialise a **local** telemetry store for this repo (creates + enables); its cook calls then record locally instead of in the global store |
| `--enable-telemetry` | Turn on the usage log (local store if the repo is `--init`-ed, else global) |
| `--disable-telemetry` | Turn off the usage log; existing records are kept |
| `--status` | Print telemetry stats to the console (local or global, whichever is active) |

---

## Shelf

| Flag | Loads |
|---|---|
| `--global` | `standards/global/SKILL.md` + all 8 concern refs (P0 + full concern set) |

---

## Concerns

Each concern flag loads a single ref from `standards/global/refs/`. No P0 SKILL.md loads.

| Flag | Loads |
|---|---|
| `--api-design` | `standards/global/refs/api-design.md` |
| `--architecture` | `standards/global/refs/architecture.md` |
| `--auth` | `standards/global/refs/auth.md` |
| `--cicd` | `standards/global/refs/cicd.md` |
| `--debug` | `standards/global/refs/debug.md` |
| `--error-handling` | `standards/global/refs/error-handling.md` |
| `--performance` | `standards/global/refs/performance.md` |
| `--security` | `standards/global/refs/security.md` |

---

## Domains

A bare domain flag **alone** loads the full shelf: `standards/<domain>/SKILL.md` + all refs.  
A sub-ref flag (`--<domain>:<ref>`) **alone** loads only that one ref — no SKILL.md.  
Pairing a bare domain flag with one or more of its **own** sub-ref flags loads the SKILL.md floor + **only** the named refs (the full shelf is suppressed): `--react --react:hooks` → `standards/react/SKILL.md` + `standards/react/refs/hooks.md` only.

### `--css`

| Flag | Loads |
|---|---|
| `--css` | `standards/css/SKILL.md` + all refs |
| `--css:accessibility` | `standards/css/refs/accessibility.md` |
| `--css:architecture` | `standards/css/refs/architecture.md` |
| `--css:layout` | `standards/css/refs/layout.md` |
| `--css:performance` | `standards/css/refs/performance.md` |
| `--css:security` | `standards/css/refs/security.md` |
| `--css:tailwind` | `standards/css/refs/tailwind.md` |
| `--css:theming` | `standards/css/refs/theming.md` |
| `--css:tooling` | `standards/css/refs/tooling.md` |

### `--dart`

| Flag | Loads |
|---|---|
| `--dart` | `standards/dart/SKILL.md` + all refs |
| `--dart:testing` | `standards/dart/refs/testing.md` |
| `--dart:tooling` | `standards/dart/refs/tooling.md` |

### `--database`

| Flag | Loads |
|---|---|
| `--database` | `standards/database/SKILL.md` + all refs |
| `--database:postgresql-anti-patterns` | `standards/database/refs/postgresql-anti-patterns.md` |
| `--database:postgresql-best-practices` | `standards/database/refs/postgresql-best-practices.md` |
| `--database:postgresql-checklist` | `standards/database/refs/postgresql-checklist.md` |
| `--database:postgresql-implementation` | `standards/database/refs/postgresql-implementation.md` |
| `--database:redis-best-practices` | `standards/database/refs/redis-best-practices.md` |
| `--database:redis-checklist` | `standards/database/refs/redis-checklist.md` |
| `--database:sql-gotchas` | `standards/database/refs/sql-gotchas.md` |

### `--flutter`

| Flag | Loads |
|---|---|
| `--flutter` | `standards/flutter/SKILL.md` + all refs |
| `--flutter:architecture` | `standards/flutter/refs/architecture.md` |
| `--flutter:cicd` | `standards/flutter/refs/cicd.md` |
| `--flutter:concurrency` | `standards/flutter/refs/concurrency.md` |
| `--flutter:dependency-injection` | `standards/flutter/refs/dependency-injection.md` |
| `--flutter:design-system` | `standards/flutter/refs/design-system.md` |
| `--flutter:error-handling` | `standards/flutter/refs/error-handling.md` |
| `--flutter:localization` | `standards/flutter/refs/localization.md` |
| `--flutter:navigation` | `standards/flutter/refs/navigation.md` |
| `--flutter:networking` | `standards/flutter/refs/networking.md` |
| `--flutter:notifications` | `standards/flutter/refs/notifications.md` |
| `--flutter:security` | `standards/flutter/refs/security.md` |
| `--flutter:state-management` | `standards/flutter/refs/state-management.md` |
| `--flutter:testing` | `standards/flutter/refs/testing.md` |

### `--graphql`

| Flag | Loads |
|---|---|
| `--graphql` | `standards/graphql/SKILL.md` + all refs |
| `--graphql:performance` | `standards/graphql/refs/performance.md` |
| `--graphql:schema-design` | `standards/graphql/refs/schema-design.md` |
| `--graphql:security` | `standards/graphql/refs/security.md` |
| `--graphql:testing` | `standards/graphql/refs/testing.md` |
| `--graphql:tooling` | `standards/graphql/refs/tooling.md` |

### `--macos`

| Flag | Loads |
|---|---|
| `--macos` | `standards/macos/SKILL.md` + all refs |
| `--macos:architecture-and-state` | `standards/macos/refs/architecture-and-state.md` |
| `--macos:distribution` | `standards/macos/refs/distribution.md` |
| `--macos:localization` | `standards/macos/refs/localization.md` |
| `--macos:performance-accessibility` | `standards/macos/refs/performance-accessibility.md` |
| `--macos:sandbox-and-tcc` | `standards/macos/refs/sandbox-and-tcc.md` |
| `--macos:windows-and-scenes` | `standards/macos/refs/windows-and-scenes.md` |

### `--nextjs`

| Flag | Loads |
|---|---|
| `--nextjs` | `standards/nextjs/SKILL.md` + all refs |
| `--nextjs:app-router` | `standards/nextjs/refs/app-router.md` |
| `--nextjs:architecture` | `standards/nextjs/refs/architecture.md` |
| `--nextjs:data-fetching` | `standards/nextjs/refs/data-fetching.md` |
| `--nextjs:i18n` | `standards/nextjs/refs/i18n.md` |
| `--nextjs:pages-router` | `standards/nextjs/refs/pages-router.md` |
| `--nextjs:rendering-and-caching` | `standards/nextjs/refs/rendering-and-caching.md` |
| `--nextjs:security` | `standards/nextjs/refs/security.md` |
| `--nextjs:server-actions` | `standards/nextjs/refs/server-actions.md` |
| `--nextjs:server-components` | `standards/nextjs/refs/server-components.md` |
| `--nextjs:state-management` | `standards/nextjs/refs/state-management.md` |
| `--nextjs:styling-and-optimization` | `standards/nextjs/refs/styling-and-optimization.md` |
| `--nextjs:testing` | `standards/nextjs/refs/testing.md` |
| `--nextjs:tooling` | `standards/nextjs/refs/tooling.md` |

### `--nodejs`

| Flag | Loads |
|---|---|
| `--nodejs` | `standards/nodejs/SKILL.md` + all refs |
| `--nodejs:async-errors` | `standards/nodejs/refs/async-errors.md` |
| `--nodejs:runtime-safety` | `standards/nodejs/refs/runtime-safety.md` |
| `--nodejs:testing` | `standards/nodejs/refs/testing.md` |
| `--nodejs:tooling` | `standards/nodejs/refs/tooling.md` |

### `--react`

| Flag | Loads |
|---|---|
| `--react` | `standards/react/SKILL.md` + all refs |
| `--react:component-patterns` | `standards/react/refs/component-patterns.md` |
| `--react:hooks` | `standards/react/refs/hooks.md` |
| `--react:performance` | `standards/react/refs/performance.md` |
| `--react:security` | `standards/react/refs/security.md` |
| `--react:state-management` | `standards/react/refs/state-management.md` |
| `--react:testing` | `standards/react/refs/testing.md` |
| `--react:tooling` | `standards/react/refs/tooling.md` |

### `--supabase`

| Flag | Loads |
|---|---|
| `--supabase` | `standards/supabase/SKILL.md` + all refs |
| `--supabase:checklist` | `standards/supabase/refs/checklist.md` |
| `--supabase:database-functions` | `standards/supabase/refs/database-functions.md` |
| `--supabase:edge-functions` | `standards/supabase/refs/edge-functions.md` |
| `--supabase:keys-and-clients` | `standards/supabase/refs/keys-and-clients.md` |
| `--supabase:migrations` | `standards/supabase/refs/migrations.md` |
| `--supabase:rls` | `standards/supabase/refs/rls.md` |

### `--swift`

| Flag | Loads |
|---|---|
| `--swift` | `standards/swift/SKILL.md` + all refs |
| `--swift:concurrency` | `standards/swift/refs/concurrency.md` |
| `--swift:interop` | `standards/swift/refs/interop.md` |
| `--swift:memory-management` | `standards/swift/refs/memory-management.md` |
| `--swift:performance` | `standards/swift/refs/performance.md` |
| `--swift:testing` | `standards/swift/refs/testing.md` |
| `--swift:tooling` | `standards/swift/refs/tooling.md` |

### `--typescript`

| Flag | Loads |
|---|---|
| `--typescript` | `standards/typescript/SKILL.md` + all refs |
| `--typescript:security` | `standards/typescript/refs/security.md` |
| `--typescript:testing` | `standards/typescript/refs/testing.md` |
| `--typescript:tooling` | `standards/typescript/refs/tooling.md` |
