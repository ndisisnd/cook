---
status: done
---

# Verification Run [7] — Flutter Skill Consolidation

> Migration plan for another agent to execute. The structural exemplars are **`dart`
> and `graphql`** (also `database`, `typescript`): one `SKILL.md` + `_INDEX.md` +
> flat `refs/`, with **no** leftover sub-skill folders. Collapse the 22-folder
> `flutter/` sprawl into that shape.
>
> **`react` is NOT an exemplar** — it is mid-migration, in the same incomplete state
> flutter is in now: it has the new `SKILL.md` + `refs/` but its 8 `react-*` sub-skill
> folders are still sitting in place (see verify-[5]). Use verify-[5] only as a
> *process* precedent for source→destination mapping. Do **not** copy react's
> end-state of leaving the old folders in `standards/`.
>
> **Nothing is deleted.** Every superseded file — all 22 old sub-skill folders and
> their contents (including the broken `REFERENCE.md` files and the per-skill
> `evals/`) — is **moved into `archive/flutter/`** at the repo root, preserving its
> original `flutter-<name>/...` path so it can be reviewed later before any deletion.
> This goes one step further than the dart/graphql exemplars (which deleted their old
> folders in place) by preserving the originals for review.

## 1. What Will Change

### Problem before

The Flutter standard is spread across **22 sub-skill folders**, each with its own
`SKILL.md`, a `refs/` folder, and an `evals/evals.json`. Unlike every other domain,
`flutter/` has **no top-level `SKILL.md`** — `_INDEX.md` routes straight into the
22 folders. Current footprint: 22 `SKILL.md` (1,218 lines), 39 topic refs + 9
`REFERENCE.md` (3,328 lines), 22 `evals.json`, 1 `_INDEX.md` = **93 files**.

Structural defects:

1. **No domain skill.** The exemplar domains (`dart`, `graphql`, `database`,
   `typescript`) each have one `SKILL.md` carrying always-on P0/P1 rules. Flutter
   has none, so a router must load multiple folders for ordinary work. (`react` has
   a top-level `SKILL.md` too, but is only partway through this same migration — its
   old `react-*` folders still linger, so it is not a clean model.)
2. **Broken `REFERENCE.md` index layer.** 9 `REFERENCE.md` files form a double-hop
   index (`SKILL → REFERENCE → ref`) that exists in no exemplar. **4 of 9 link to
   files that were never created** — dangling targets:
   - `auto-route-navigation/refs/REFERENCE.md` → `guards.md`, `nested-routes.md`
   - `dependency-injection/refs/REFERENCE.md` → `initialization.md`, `testing-mocks.md`
   - `error-handling/refs/REFERENCE.md` → `consumption.md`
   - `feature-based-clean-architecture/refs/REFERENCE.md` → `shared-core.md`, `modular-injection.md`
   - `security/refs/REFERENCE.md` → `secure-storage-impl.md`
3. **Orphaned refs.** Several refs are unreachable from any `SKILL.md` (only linked,
   if at all, through a broken `REFERENCE.md`): `design-system/refs/dls-modular-pattern.md`
   and `monolithic-pattern.md`, `layer-based-clean-architecture/refs/repository-mapping.md`.
4. **Duplicate / conflicting skills.** `flutter-navigation` (P1, go_router) and
   `flutter-go-router-navigation` (P0, go_router) cover the same library with
   contradictory priorities. `flutter-widgets`, `flutter-idiomatic-flutter`, and
   `flutter-performance` repeat the same UI rules (`const`, composition, the
   `_buildXxx` anti-pattern, `SizedBox.shrink`, `ListView.builder`).
5. **Per-skill evals in the shipped tree.** No exemplar ships `evals/evals.json`;
   they are agent-audit artifacts.
6. **Inconsistent naming.** `bloc_templates.md`, `mocking_standards.md` use
   snake_case while the rest is kebab-case.

### After

A single `standards/flutter/SKILL.md` carries the always-on Flutter rules; **13
refs** hold topic/library deep-dives loaded conditionally; `_INDEX.md` is
regenerated to the dart/graphql format. The 22 old sub-skill folders are **moved
intact to `archive/flutter/`** (repo root) for later review. Result: under
`standards/flutter/` there are **15 active files** (1 SKILL + 1 _INDEX + 13 refs);
the 91 superseded files live under `archive/flutter/` with their original paths.

The structure matches the dart/graphql exemplar exactly: one skill invocation
(`flutter`) → read `SKILL.md` → pull only the matched refs → return.

### Archive location and why it sits outside `standards/`

The archive goes at **`archive/flutter/`** (repo root, sibling to `standards/` and
`verify/`) — **not** under `standards/flutter/`. `_INDEX.md` is "AUTO-GENERATED from
SKILL.md frontmatters", so any generator or router that globs
`standards/flutter/**/SKILL.md` would re-discover archived skills if they stayed
inside the standards tree. Moving them out of `standards/` guarantees cook's domain
detection and the index generator never pick them up, while keeping every file
available for review. Inside the archive, keep the original layout:

```
archive/flutter/
├── flutter-bloc-state-management/   (SKILL.md, refs/, evals/ — verbatim)
├── flutter-navigation/
├── ... all 22 folders, unchanged ...
└── flutter-widgets/
```

---

## 2. Target Structure

```
standards/flutter/
├── _INDEX.md                      # regenerated: File Match table → refs, Loading Instructions, Archived section
├── SKILL.md                       # NEW — universal Flutter P0/P1, always loaded
└── refs/                          # flat, topic deep-dives — load only what the task needs
    ├── state-management.md        # bloc + riverpod + getx
    ├── navigation.md              # go_router + auto_route + getx navigation
    ├── architecture.md            # feature-based + layer-based clean architecture
    ├── networking.md              # dio + retrofit + interceptors + token refresh
    ├── error-handling.md          # dartz Either/Failure detail + error mapping
    ├── dependency-injection.md    # get_it + injectable + modules
    ├── design-system.md           # DLS patterns: usage, modular, monolithic
    ├── localization.md            # easy_localization + sheet loader
    ├── notifications.md           # FCM + flutter_local_notifications
    ├── security.md                # OWASP, secure_storage, pinning, network security
    ├── concurrency.md             # isolates, compute()
    ├── cicd.md                    # github actions + fastlane + advanced workflow
    └── testing.md                 # unit/widget/integration/robot/mocking/keys (9 files merged)
```

### What goes inline in `SKILL.md` (always-on rules)

- **P0 — Design System Enforcement** *(principle only)*: no hardcoded colors,
  spacing, typography, borders; use tokens / theme. Detail → `refs/design-system.md`.
- **P0 — Error Handling** *(principle only)*: repositories return `Either<Failure, T>`;
  `on Type catch`, never bare catch. Detail → `refs/error-handling.md`.
- **P1 — Widgets** (from `flutter-widgets`): `StatelessWidget` default, `const`,
  theming via `Theme.of`, widget keys, ~80-line file limit, `ListView.builder`.
- **P1 — Idiomatic Flutter** (from `flutter-idiomatic-flutter`): composition over
  deep nesting, `context.mounted` after await, `spacing`/`Gap`/`SizedBox` over
  `Padding`, `SizedBox.shrink()` for empty UI, no `_buildXxx()` helpers.
- **P1 — Performance** (from `flutter-performance`): `const` leaves, `buildWhen`/
  `select`, `RepaintBoundary`, image cache sizing, dispose controllers, pagination.
- **Anti-Patterns**: consolidated from widgets + idiomatic + performance + the
  design-system and error-handling principles.
- **References**: 13 conditional refs, each with a load-trigger description (mirror
  the dart/graphql References section format).

---

## 3. Source → Destination Mapping (no content lost)

Read every source file in full and carry forward every meaningful rule, example,
and anti-pattern. Where a library has its own section in a merged ref (state
management, navigation, architecture), keep each library's content under its own
heading so a reader consuming one library is not forced through the others.

| Source file | Destination |
|---|---|
| **State management** | |
| `flutter-bloc-state-management/SKILL.md` | `refs/state-management.md` § BLoC/Cubit |
| `flutter-bloc-state-management/refs/bloc_templates.md` | `refs/state-management.md` § BLoC/Cubit (templates) |
| `flutter-riverpod-state-management/SKILL.md` | `refs/state-management.md` § Riverpod |
| `flutter-riverpod-state-management/refs/implementation.md` | `refs/state-management.md` § Riverpod |
| `flutter-getx-state-management/SKILL.md` | `refs/state-management.md` § GetX |
| `flutter-getx-state-management/refs/controller-example.md` | `refs/state-management.md` § GetX |
| **Navigation** (resolve the P1↔P0 conflict — treat go_router as one section) | |
| `flutter-navigation/SKILL.md` | `refs/navigation.md` § go_router (merge w/ below) |
| `flutter-navigation/refs/implementation.md` | `refs/navigation.md` § go_router |
| `flutter-navigation/refs/routing-patterns.md` | `refs/navigation.md` § go_router |
| `flutter-go-router-navigation/SKILL.md` | `refs/navigation.md` § go_router |
| `flutter-go-router-navigation/refs/typed-routes.md` | `refs/navigation.md` § go_router |
| `flutter-auto-route-navigation/SKILL.md` | `refs/navigation.md` § auto_route |
| `flutter-auto-route-navigation/refs/implementation.md` | `refs/navigation.md` § auto_route |
| `flutter-auto-route-navigation/refs/router-config.md` | `refs/navigation.md` § auto_route |
| `flutter-auto-route-navigation/refs/REFERENCE.md` | **Archived** (broken index — no content carried; dangling `guards.md`, `nested-routes.md`) |
| `flutter-getx-navigation/SKILL.md` | `refs/navigation.md` § GetX |
| `flutter-getx-navigation/refs/app-pages.md` | `refs/navigation.md` § GetX |
| `flutter-getx-navigation/refs/middleware-example.md` | `refs/navigation.md` § GetX |
| **Architecture** | |
| `flutter-feature-based-clean-architecture/SKILL.md` | `refs/architecture.md` § Feature-based |
| `flutter-feature-based-clean-architecture/refs/folder-structure.md` | `refs/architecture.md` § Feature-based |
| `flutter-feature-based-clean-architecture/refs/implementation.md` | `refs/architecture.md` § Feature-based |
| `flutter-feature-based-clean-architecture/refs/REFERENCE.md` | **Archived** (broken index — no content carried; dangling `shared-core.md`, `modular-injection.md`) |
| `flutter-layer-based-clean-architecture/SKILL.md` | `refs/architecture.md` § Layer-based |
| `flutter-layer-based-clean-architecture/refs/REFERENCE.md` | `refs/architecture.md` § Layer-based (real content: DTO→entity mapping, keep) |
| `flutter-layer-based-clean-architecture/refs/repository-mapping.md` | `refs/architecture.md` § Layer-based (currently orphaned) |
| **Networking** | |
| `flutter-retrofit-networking/SKILL.md` | `refs/networking.md` |
| `flutter-retrofit-networking/refs/implementation.md` | `refs/networking.md` |
| `flutter-retrofit-networking/refs/token-refresh.md` | `refs/networking.md` |
| `flutter-retrofit-networking/refs/REFERENCE.md` | **Archived** (index only — no content carried) |
| **Error handling** | |
| `flutter-error-handling/SKILL.md` | `SKILL.md` (P0 principle) + `refs/error-handling.md` (detail) |
| `flutter-error-handling/refs/error-mapping.md` | `refs/error-handling.md` |
| `flutter-error-handling/refs/implementation.md` | `refs/error-handling.md` |
| `flutter-error-handling/refs/REFERENCE.md` | **Archived** (broken index — no content carried; dangling `consumption.md`) |
| **Dependency injection** | |
| `flutter-dependency-injection/SKILL.md` | `refs/dependency-injection.md` |
| `flutter-dependency-injection/refs/modules.md` | `refs/dependency-injection.md` |
| `flutter-dependency-injection/refs/implementation.md` | `refs/dependency-injection.md` |
| `flutter-dependency-injection/refs/REFERENCE.md` | **Archived** (broken index — no content carried; dangling `initialization.md`, `testing-mocks.md`) |
| **Design system** | |
| `flutter-design-system/SKILL.md` | `SKILL.md` (P0 principle) + `refs/design-system.md` (detail) |
| `flutter-design-system/refs/usage.md` | `refs/design-system.md` |
| `flutter-design-system/refs/dls-modular-pattern.md` | `refs/design-system.md` (currently orphaned) |
| `flutter-design-system/refs/monolithic-pattern.md` | `refs/design-system.md` (currently orphaned) |
| **Localization** | |
| `flutter-localization/SKILL.md` | `refs/localization.md` |
| `flutter-localization/refs/sheet-loader.md` | `refs/localization.md` |
| `flutter-localization/refs/implementation.md` | `refs/localization.md` |
| `flutter-localization/refs/REFERENCE.md` | **Archived** (index only — no content carried) |
| **Notifications** | |
| `flutter-notifications/SKILL.md` | `refs/notifications.md` |
| `flutter-notifications/refs/implementation.md` | `refs/notifications.md` |
| **Security** | |
| `flutter-security/SKILL.md` | `refs/security.md` |
| `flutter-security/refs/network-security.md` | `refs/security.md` |
| `flutter-security/refs/implementation.md` | `refs/security.md` |
| `flutter-security/refs/REFERENCE.md` | **Archived** (broken index — no content carried; dangling `secure-storage-impl.md`) |
| **Concurrency** | |
| `flutter-concurrency/SKILL.md` | `refs/concurrency.md` |
| `flutter-concurrency/refs/isolate-examples.md` | `refs/concurrency.md` |
| **CI/CD** | |
| `flutter-cicd/SKILL.md` | `refs/cicd.md` |
| `flutter-cicd/refs/github-actions.md` | `refs/cicd.md` |
| `flutter-cicd/refs/fastlane.md` | `refs/cicd.md` |
| `flutter-cicd/refs/advanced-workflow.md` | `refs/cicd.md` |
| **Testing** (9 files → 1, use headings per topic) | |
| `flutter-testing/SKILL.md` | `refs/testing.md` (core rules at top) |
| `flutter-testing/refs/unit-testing.md` | `refs/testing.md` § Unit |
| `flutter-testing/refs/widget-testing.md` | `refs/testing.md` § Widget |
| `flutter-testing/refs/integration-testing.md` | `refs/testing.md` § Integration |
| `flutter-testing/refs/robot-pattern.md` | `refs/testing.md` § Robot pattern |
| `flutter-testing/refs/mocking_standards.md` | `refs/testing.md` § Mocking |
| `flutter-testing/refs/bloc-testing.md` | `refs/testing.md` § BLoC tests |
| `flutter-testing/refs/test-organization.md` | `refs/testing.md` § Organization |
| `flutter-testing/refs/widget-keys.md` | `refs/testing.md` § Widget keys |
| `flutter-testing/refs/REFERENCE.md` | Use its (intact) index to structure `refs/testing.md` headings; the file itself is then archived with its folder |
| **UI core → SKILL.md** | |
| `flutter-widgets/SKILL.md` | `SKILL.md` P1 Widgets |
| `flutter-idiomatic-flutter/SKILL.md` | `SKILL.md` P1 Idiomatic Flutter |
| `flutter-performance/SKILL.md` | `SKILL.md` P1 Performance |
| **Evals** | |
| All 22 `flutter-*/evals/evals.json` | **No content carried** — exemplars ship no per-skill evals; archived with their folders for review |

> **All sources are archived, not deleted.** The "Destination" column says where each
> file's *content* lands. After the content is carried forward, the entire original
> `flutter-<name>/` folder — every `SKILL.md`, `refs/` file, and `evals/` file,
> including the index-only and broken `REFERENCE.md` files — is moved verbatim to
> `archive/flutter/<name>/`. Rows marked "no content carried" mean nothing was merged
> from that file (it was a pure or broken index); the file is still preserved in the
> archive for review.

---

## 4. Execution Steps

1. **Create `standards/flutter/SKILL.md`** with frontmatter (`name: flutter`,
   description, `metadata.triggers.files: ['**/*.dart']` + keywords) and the inline
   P0/P1 sections from §2, plus a References section listing all 13 refs with
   load-trigger descriptions. Match the dart/graphql `SKILL.md` shape.

2. **Create the 13 `refs/*.md` files** per the §3 mapping. Read each source in
   full; carry forward every rule, code example, and anti-pattern. Use per-library
   headings inside `state-management.md`, `navigation.md`, and `architecture.md`.

3. **Resolve known conflicts/orphans while merging:**
   - Navigation: merge `flutter-navigation` and `flutter-go-router-navigation`
     into one go_router section; drop the P1/P0 priority contradiction (state the
     priority once).
   - Re-link the orphaned refs (`dls-modular-pattern`, `monolithic-pattern`,
     `repository-mapping`) so they live inside their merged ref.
   - Normalize naming: content from `bloc_templates.md` and `mocking_standards.md`
     lands in kebab-cased destinations.

4. **Regenerate `standards/flutter/_INDEX.md`** to the dart/graphql format:
   - Header comment `<!-- AUTO-GENERATED ... do not edit manually -->`
   - **File Match** table: bold `flutter` row + one `flutter → <ref>` row per ref
     (file pattern + keywords). Use the table proposed in §6.
   - **Loading Instructions** block (`Load <SKILLS>/flutter/SKILL.md` + per-ref load
     conditions).
   - **Archived** section: a short note that the 22 superseded sub-skills were moved
     to `archive/flutter/` (repo root) pending review, with the source→destination
     mapping table from §3 reproduced so a reviewer can trace where each one's content
     went. (This replaces the "Deprecated (pending removal)" section seen in dart's
     `_INDEX.md`, since the folders no longer sit under `standards/flutter/` at all —
     they are out-of-tree in `archive/flutter/`.)

5. **Update `cook/SKILL.md`** so Flutter routes like the other consolidated
   domains:
   - Step 6 domain table row for Flutter already points at
     `standards/flutter/_INDEX.md` — confirm wording still holds.
   - The `_INDEX.md` loading line `Load matched skills: <SKILLS>/flutter/<skill>/SKILL.md`
     is replaced by the new `_INDEX.md` (which points at `SKILL.md` + refs), so no
     stale "load the sub-skill folder" instruction remains anywhere.

6. **Move — do not delete — the 22 `flutter-*/` folders to `archive/flutter/`.**
   - Create `archive/flutter/` at the repo root (sibling to `standards/` and
     `verify/`).
   - `git mv` each `standards/flutter/flutter-<name>/` to
     `archive/flutter/flutter-<name>/`, preserving the folder verbatim (SKILL.md,
     refs/, evals/). Using `git mv` keeps history and makes the move reviewable in
     the diff.
   - After the move, `standards/flutter/` contains only `SKILL.md`, `_INDEX.md`, and
     `refs/` — no `flutter-*/` subfolders remain.
   - Deletion of `archive/flutter/` is a separate, later decision after review.

7. **Update `CHANGELOG.md`** (per repo workflow) describing the Flutter
   consolidation and the archive move.

---

## 5. Success Criteria

### Structure
- [ ] `standards/flutter/SKILL.md` exists, non-empty, with valid frontmatter (`name: flutter`)
- [ ] `standards/flutter/_INDEX.md` references the single skill + refs (not sub-skill folders)
- [ ] Exactly these 13 refs exist under `standards/flutter/refs/`: `state-management`, `navigation`, `architecture`, `networking`, `error-handling`, `dependency-injection`, `design-system`, `localization`, `notifications`, `security`, `concurrency`, `cicd`, `testing`
- [ ] No `REFERENCE.md` exists anywhere under `standards/flutter/refs/`
- [ ] No new files use snake_case names

### SKILL.md content
- [ ] P0 design-system principle present (no hardcoded color/spacing/typography), with detail deferred to `refs/design-system.md`
- [ ] P0 error-handling principle present (`Either<Failure, T>`, `on Type catch`), detail deferred to `refs/error-handling.md`
- [ ] P1 Widgets section (StatelessWidget default, const, theming, keys, file-size, ListView.builder)
- [ ] P1 Idiomatic section (composition, `context.mounted`, spacing/Gap, SizedBox.shrink, no `_buildXxx`)
- [ ] P1 Performance section (const leaves, buildWhen/select, RepaintBoundary, image sizing, dispose, pagination)
- [ ] Anti-Patterns section consolidating widgets + idiomatic + performance
- [ ] References section lists all 13 refs, each with a trigger description

### Refs — coverage (no library section dropped)
- [ ] `state-management.md` has distinct BLoC, Riverpod, and GetX sections
- [ ] `navigation.md` has go_router, auto_route, and GetX sections; go_router appears once (no duplicate skill, no priority conflict)
- [ ] `architecture.md` has feature-based and layer-based sections; includes the DTO→entity mapping and repository-mapping content
- [ ] `networking.md` includes token-refresh interceptor content
- [ ] `design-system.md` includes usage + modular-pattern + monolithic-pattern (the previously orphaned files)
- [ ] `testing.md` covers unit, widget, integration, robot pattern, mocking, bloc tests, organization, and widget keys
- [ ] `cicd.md` covers GitHub Actions, Fastlane, and advanced workflow
- [ ] `concurrency.md`, `localization.md`, `notifications.md`, `security.md`, `dependency-injection.md`, `error-handling.md` each carry their source SKILL + refs content

### _INDEX.md
- [ ] AUTO-GENERATED header comment present
- [ ] File Match table: one bold `flutter` row + one `flutter → <ref>` row per ref
- [ ] Loading Instructions block present
- [ ] Archived section points to `archive/flutter/` and reproduces the source→destination mapping

### Archive
- [ ] `archive/flutter/` exists at the repo root (outside `standards/`)
- [ ] All 22 `flutter-<name>/` folders are present under `archive/flutter/`, verbatim (SKILL.md, refs/, evals/ intact)
- [ ] No `flutter-*/` subfolders remain under `standards/flutter/`
- [ ] The move used `git mv` (history preserved; nothing deleted)

### cook routing
- [ ] `cook/SKILL.md` contains no instruction to load `flutter/<skill>/SKILL.md` sub-folders
- [ ] Flutter domain row resolves to `standards/flutter/_INDEX.md` → `SKILL.md` + refs

### No unintended changes / no loss
- [ ] No source file was deleted — every superseded file is either merged into a ref/SKILL or present in `archive/flutter/`
- [ ] No changes to `standards/dart/`, `graphql/`, `database/`, `typescript/`, `react/`, `nextjs/`, `global/`, or `review/`
- [ ] `CHANGELOG.md` updated

---

## 6. Proposed `_INDEX.md` File Match Table

| Skill | File pattern | Keywords |
|---|---|---|
| **flutter** | `**/*.dart` | Widget, StatelessWidget, const, build, Theme, SizedBox, ListView |
| flutter → state-management | `**_bloc.dart`, `**_cubit.dart`, `**_provider.dart`, `**_notifier.dart`, `**_controller.dart` | Bloc, Cubit, Riverpod, GetX, Obx, AsyncValue, ref.watch |
| flutter → navigation | `**/*router*.dart`, `**/app_pages.dart`, `**/main.dart` | GoRouter, AutoRoute, GetPage, Navigator, deep link, redirect |
| flutter → architecture | `lib/features/**`, `lib/domain/**`, `lib/infrastructure/**`, `lib/application/**` | feature, domain, infrastructure, DTO, mapper, Either |
| flutter → networking | `**/data_sources/**`, `**/api/**` | Dio, Retrofit, RestClient, Interceptor, token refresh |
| flutter → error-handling | `lib/domain/**`, `lib/infrastructure/**` | Either, fold, Left, Right, Failure, dartz |
| flutter → dependency-injection | `**/injection.dart`, `**/locator.dart` | GetIt, injectable, singleton, module |
| flutter → design-system | `**/theme/**`, `**/*_theme.dart`, `**/*_colors.dart` | ThemeData, ColorScheme, AppColors, design token |
| flutter → localization | `**/translations/*.json`, `**/langs/*.csv` | localization, tr(), easy_localization |
| flutter → notifications | `**/*notification*.dart` | FCM, FirebaseMessaging, push |
| flutter → security | `lib/infrastructure/**`, `pubspec.yaml` | secure_storage, pinning, jailbreak, OWASP, PII |
| flutter → concurrency | `**/*isolate*.dart`, `**/*worker*.dart` | Isolate, compute, ReceivePort, background |
| flutter → cicd | `.github/workflows/**.yml`, `fastlane/**` | ci, cd, pipeline, deploy, workflow |
| flutter → testing | `**/test/**.dart`, `**/integration_test/**.dart`, `**/robots/**.dart` | test, patrol, robot, blocTest, mocktail, WidgetKeys |

---

## 7. Verification Notes for the Executing Agent

After building, verify in this order:

1. Read `standards/flutter/SKILL.md` top to bottom; confirm it covers the design-system
   and error-handling principles plus the three P1 UI sections without depending on a
   ref for its core rules. Confirm the References section lists all 13 refs.
2. Read each ref and confirm its scope matches its `_INDEX.md` trigger — no overlap
   between refs, nothing that belongs inline in `SKILL.md`.
3. Confirm `_INDEX.md` routes to `SKILL.md` + refs and that its Archived section points
   to `archive/flutter/`.
4. Confirm all 22 folders now live under `archive/flutter/` (none remain under
   `standards/flutter/`) and that `cook/SKILL.md` no longer tells the router to load
   `flutter/<skill>/SKILL.md`.

### Source coverage audit (run last — no rule lost)

For **every** source file in the §3 mapping, read it in full and confirm each
meaningful rule, code example, and anti-pattern was either:

- carried forward into its destination (`SKILL.md` or the named ref), or
- deliberately dropped with a clear reason (duplicated elsewhere, superseded, or
  too implementation-specific).

For any gap — content present in a source but absent from its destination — flag it
explicitly with the source file, the missing content, and the recommended
destination. **Do not pass a check when content is missing.** Pay special attention
to:

- The 4 broken `REFERENCE.md` files — confirm nothing was merged from them (they are
  indexes; the dangling targets never existed), and that they are preserved under
  `archive/flutter/` rather than discarded.
- The 3 previously-orphaned refs — confirm they actually landed in their merged ref.
- The navigation merge — confirm go_router guidance from both `flutter-navigation`
  and `flutter-go-router-navigation` is present and not contradictory.
- The testing merge — confirm all 8 topic refs survived as sections.
