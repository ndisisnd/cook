# Archived-content provenance

Migration-history tables extracted from `standards/*/_INDEX.md` (they were
dead weight in the LLM's routing read path). Each section records where a
domain's pre-consolidation sub-skill content was merged, so a reviewer can
verify no rules were lost.

## flutter

The 22 sub-skill folders that previously lived under `standards/flutter/` have been moved to `archive/flutter/` at the repo root (outside `standards/`) pending review. They are preserved verbatim — each original `SKILL.md`, `refs/`, and `evals/` directory is intact under its original `flutter-<name>/` path.

Their content has been merged into `SKILL.md` and the `refs/` files above. The table below traces each source to its destination so a reviewer can verify no rules were lost.

| Source (under `archive/flutter/`) | Destination |
|---|---|
| `flutter-bloc-state-management/SKILL.md` | `refs/state-management.md` § BLoC/Cubit |
| `flutter-bloc-state-management/refs/bloc_templates.md` | `refs/state-management.md` § BLoC/Cubit (templates) |
| `flutter-riverpod-state-management/SKILL.md` | `refs/state-management.md` § Riverpod |
| `flutter-riverpod-state-management/refs/implementation.md` | `refs/state-management.md` § Riverpod |
| `flutter-getx-state-management/SKILL.md` | `refs/state-management.md` § GetX |
| `flutter-getx-state-management/refs/controller-example.md` | `refs/state-management.md` § GetX |
| `flutter-navigation/SKILL.md` | `refs/navigation.md` § go_router |
| `flutter-navigation/refs/implementation.md` | `refs/navigation.md` § go_router |
| `flutter-navigation/refs/routing-patterns.md` | `refs/navigation.md` § go_router |
| `flutter-go-router-navigation/SKILL.md` | `refs/navigation.md` § go_router (merged) |
| `flutter-go-router-navigation/refs/typed-routes.md` | `refs/navigation.md` § go_router |
| `flutter-auto-route-navigation/SKILL.md` | `refs/navigation.md` § auto_route |
| `flutter-auto-route-navigation/refs/implementation.md` | `refs/navigation.md` § auto_route |
| `flutter-auto-route-navigation/refs/router-config.md` | `refs/navigation.md` § auto_route |
| `flutter-auto-route-navigation/refs/REFERENCE.md` | **Archived** — broken index (dangling `guards.md`, `nested-routes.md`); no content carried |
| `flutter-getx-navigation/SKILL.md` | `refs/navigation.md` § GetX |
| `flutter-getx-navigation/refs/app-pages.md` | `refs/navigation.md` § GetX |
| `flutter-getx-navigation/refs/middleware-example.md` | `refs/navigation.md` § GetX |
| `flutter-feature-based-clean-architecture/SKILL.md` | `refs/architecture.md` § Feature-based |
| `flutter-feature-based-clean-architecture/refs/folder-structure.md` | `refs/architecture.md` § Feature-based |
| `flutter-feature-based-clean-architecture/refs/implementation.md` | `refs/architecture.md` § Feature-based |
| `flutter-feature-based-clean-architecture/refs/REFERENCE.md` | **Archived** — broken index (dangling `shared-core.md`, `modular-injection.md`); no content carried |
| `flutter-layer-based-clean-architecture/SKILL.md` | `refs/architecture.md` § Layer-based |
| `flutter-layer-based-clean-architecture/refs/REFERENCE.md` | `refs/architecture.md` § Layer-based (real content: DTO→entity mapping, carried) |
| `flutter-layer-based-clean-architecture/refs/repository-mapping.md` | `refs/architecture.md` § Layer-based (previously orphaned, now carried) |
| `flutter-retrofit-networking/SKILL.md` | `refs/networking.md` |
| `flutter-retrofit-networking/refs/implementation.md` | `refs/networking.md` |
| `flutter-retrofit-networking/refs/token-refresh.md` | `refs/networking.md` |
| `flutter-retrofit-networking/refs/REFERENCE.md` | **Archived** — index only; no content carried |
| `flutter-error-handling/SKILL.md` | `SKILL.md` (P0 principle) + `refs/error-handling.md` (detail) |
| `flutter-error-handling/refs/error-mapping.md` | `refs/error-handling.md` |
| `flutter-error-handling/refs/implementation.md` | `refs/error-handling.md` |
| `flutter-error-handling/refs/REFERENCE.md` | **Archived** — broken index (dangling `consumption.md`); no content carried |
| `flutter-dependency-injection/SKILL.md` | `refs/dependency-injection.md` |
| `flutter-dependency-injection/refs/modules.md` | `refs/dependency-injection.md` |
| `flutter-dependency-injection/refs/implementation.md` | `refs/dependency-injection.md` |
| `flutter-dependency-injection/refs/REFERENCE.md` | **Archived** — broken index (dangling `initialization.md`, `testing-mocks.md`); no content carried |
| `flutter-design-system/SKILL.md` | `SKILL.md` (P0 principle) + `refs/design-system.md` (detail) |
| `flutter-design-system/refs/usage.md` | `refs/design-system.md` |
| `flutter-design-system/refs/dls-modular-pattern.md` | `refs/design-system.md` § Modular DLS (previously orphaned, now carried) |
| `flutter-design-system/refs/monolithic-pattern.md` | `refs/design-system.md` § Monolithic DLS (previously orphaned, now carried) |
| `flutter-localization/SKILL.md` | `refs/localization.md` |
| `flutter-localization/refs/sheet-loader.md` | `refs/localization.md` |
| `flutter-localization/refs/implementation.md` | `refs/localization.md` |
| `flutter-localization/refs/REFERENCE.md` | **Archived** — index only; no content carried |
| `flutter-notifications/SKILL.md` | `refs/notifications.md` |
| `flutter-notifications/refs/implementation.md` | `refs/notifications.md` |
| `flutter-security/SKILL.md` | `refs/security.md` |
| `flutter-security/refs/network-security.md` | `refs/security.md` |
| `flutter-security/refs/implementation.md` | `refs/security.md` |
| `flutter-security/refs/REFERENCE.md` | **Archived** — broken index (dangling `secure-storage-impl.md`); no content carried |
| `flutter-concurrency/SKILL.md` | `refs/concurrency.md` |
| `flutter-concurrency/refs/isolate-examples.md` | `refs/concurrency.md` |
| `flutter-cicd/SKILL.md` | `refs/cicd.md` |
| `flutter-cicd/refs/github-actions.md` | `refs/cicd.md` |
| `flutter-cicd/refs/fastlane.md` | `refs/cicd.md` |
| `flutter-cicd/refs/advanced-workflow.md` | `refs/cicd.md` |
| `flutter-testing/SKILL.md` | `refs/testing.md` (core rules) |
| `flutter-testing/refs/unit-testing.md` | `refs/testing.md` § Unit |
| `flutter-testing/refs/widget-testing.md` | `refs/testing.md` § Widget |
| `flutter-testing/refs/integration-testing.md` | `refs/testing.md` § Integration |
| `flutter-testing/refs/robot-pattern.md` | `refs/testing.md` § Robot pattern |
| `flutter-testing/refs/mocking_standards.md` | `refs/testing.md` § Mocking |
| `flutter-testing/refs/bloc-testing.md` | `refs/testing.md` § BLoC tests |
| `flutter-testing/refs/test-organization.md` | `refs/testing.md` § Organization |
| `flutter-testing/refs/widget-keys.md` | `refs/testing.md` § Widget keys |
| `flutter-testing/refs/REFERENCE.md` | Used to structure `refs/testing.md` headings; then archived |
| `flutter-widgets/SKILL.md` | `SKILL.md` P1 Widgets |
| `flutter-idiomatic-flutter/SKILL.md` | `SKILL.md` P1 Idiomatic Flutter |
| `flutter-performance/SKILL.md` | `SKILL.md` P1 Performance |
| All 22 `flutter-*/evals/evals.json` | **No content carried** — exemplars ship no per-skill evals; preserved in `archive/flutter/` |

## nextjs

The 18 sub-skill folders that previously lived under `standards/nextjs/` have been moved to `archive/nextjs/` at the repo root. They are preserved verbatim - each original `SKILL.md`, `refs/`, and `evals/` directory is intact under its original `nextjs-<name>/` path.

Their content has been merged into `SKILL.md` and the `refs/` files above. The table below traces each source to its destination so a reviewer can verify no rules were lost.

| Source (under `archive/nextjs/`) | Destination |
|---|---|
| `nextjs-server-components/SKILL.md` | `SKILL.md` P0 Server & Client Components |
| `nextjs-server-components/refs/example.md` | `refs/server-components.md` |
| `nextjs-server-components/refs/composition-security.md` | `refs/server-components.md` |
| `nextjs-architecture/refs/RSC_BOUNDARIES.md` | `refs/server-components.md` - single RSC boundary home |
| `nextjs-data-fetching/SKILL.md` | `SKILL.md` P0 Data Fetching & Access + `refs/data-fetching.md` |
| `nextjs-data-fetching/refs/usage-examples.md` | `refs/data-fetching.md` |
| `nextjs-data-access-layer/SKILL.md` | `SKILL.md` P0 Data Fetching & Access + `refs/data-fetching.md` |
| `nextjs-data-access-layer/refs/implementation.md` | `refs/data-fetching.md` DAL section |
| `nextjs-data-access-layer/refs/patterns.md` | `refs/data-fetching.md` DAL patterns - previously orphaned, carried |
| `nextjs-app-router/SKILL.md` | `SKILL.md` P0 App Router Conventions + `refs/app-router.md` |
| `nextjs-app-router/refs/implementation.md` | `refs/app-router.md` |
| `nextjs-app-router/refs/SELF_HOSTING.md` | `refs/app-router.md` Self-Hosting section |
| `nextjs-rendering/SKILL.md` | `SKILL.md` P1 Rendering & Caching + `refs/rendering-and-caching.md` |
| `nextjs-rendering/refs/strategy-matrix.md` | `refs/rendering-and-caching.md` Strategy Matrix |
| `nextjs-rendering/refs/implementation.md` | `refs/rendering-and-caching.md` Strategy Guide |
| `nextjs-rendering/refs/implementation-details.md` | `refs/rendering-and-caching.md` Strategy Guide |
| `nextjs-rendering/refs/scaling-patterns.md` | `refs/rendering-and-caching.md` Static Shell / Waterfalls / ISR + Streaming |
| `nextjs-rendering/refs/SUSPENSE_BAILOUT.md` | `refs/rendering-and-caching.md` Suspense Bailout Rules - previously orphaned, carried |
| `nextjs-caching/SKILL.md` | `SKILL.md` P1 Rendering & Caching + `refs/rendering-and-caching.md` |
| `nextjs-caching/refs/implementation.md` | `refs/rendering-and-caching.md` Cache Layers / Invalidation |
| `nextjs-caching/refs/CACHE_COMPONENTS.md` | `refs/rendering-and-caching.md` Cache Components / PPR |
| `nextjs-authentication/SKILL.md` | `SKILL.md` P0 Security & Auth + `refs/security.md` |
| `nextjs-authentication/refs/implementation.md` | `refs/security.md` Token Storage / Middleware |
| `nextjs-authentication/refs/auth-implementation.md` | `refs/security.md` Token Storage / Session Reads / Middleware |
| `nextjs-security/SKILL.md` | `SKILL.md` P0 Security & Auth + `refs/security.md` |
| `nextjs-security/refs/implementation.md` | `refs/security.md` Server Action Validation / Data Boundary |
| `nextjs-pages-router/SKILL.md` | `refs/pages-router.md` |
| `nextjs-pages-router/refs/implementation.md` | `refs/pages-router.md` |
| `nextjs-pages-router/refs/server-side-props.md` | `refs/pages-router.md` |
| `nextjs-pages-router/refs/feature-sliced-design-pages.md` | `refs/pages-router.md` Feature-Sliced Design section - previously orphaned, carried |
| `nextjs-server-actions/SKILL.md` | `SKILL.md` P1 Server Actions + `refs/server-actions.md` |
| `nextjs-server-actions/refs/secure-actions.md` | `refs/server-actions.md` + cross-reference to `refs/security.md` |
| `nextjs-optimization/SKILL.md` | `refs/styling-and-optimization.md` Optimization sections |
| `nextjs-optimization/refs/example.md` | `refs/styling-and-optimization.md` Image / Font / Metadata examples |
| `nextjs-styling/SKILL.md` | `refs/styling-and-optimization.md` Styling sections |
| `nextjs-styling/refs/implementation.md` | `refs/styling-and-optimization.md` Tailwind `cn()` section |
| `nextjs-styling/refs/scss.md` | `refs/styling-and-optimization.md` SCSS Modules section |
| `nextjs-styling/refs/ant-design.md` | `refs/styling-and-optimization.md` Ant Design section |
| `nextjs-styling/refs/tailwind.md` | `refs/styling-and-optimization.md` Tailwind / Font section |
| `nextjs-testing/SKILL.md` | `refs/testing.md` |
| `nextjs-testing/refs/implementation.md` | `refs/testing.md` |
| `nextjs-architecture/SKILL.md` | `refs/architecture.md` |
| `nextjs-architecture/refs/implementation.md` | `refs/architecture.md` |
| `nextjs-architecture/refs/fsd-structure.md` | `refs/architecture.md` FSD Structure |
| `nextjs-architecture/refs/BUNDLING.md` | `refs/architecture.md` Bundling section |
| `nextjs-architecture/refs/RUNTIME_SELECTION.md` | `refs/architecture.md` Runtime Selection section |
| `nextjs-architecture/refs/DEBUG_TRICKS.md` | `refs/architecture.md` Debugging section |
| `nextjs-i18n/SKILL.md` | `refs/i18n.md` |
| `nextjs-i18n/refs/implementation.md` | `refs/i18n.md` Routing / Middleware |
| `nextjs-i18n/refs/next-intl.md` | `refs/i18n.md` next-intl section |
| `nextjs-i18n/refs/react-intl.md` | `refs/i18n.md` react-intl section |
| `nextjs-state-management/SKILL.md` | `refs/state-management.md` |
| `nextjs-state-management/refs/implementation.md` | `refs/state-management.md` URL / Server / Zustand examples |
| `nextjs-state-management/refs/redux.md` | `refs/state-management.md` Redux sections |
| `nextjs-state-management/refs/zustand.md` | `refs/state-management.md` Zustand sections |
| `nextjs-state-management/refs/url-state.md` | `refs/state-management.md` URL State sections |
| `nextjs-tooling/SKILL.md` | `refs/tooling.md` |
| `nextjs-tooling/refs/implementation.md` | `refs/tooling.md` Build / Docker / Env sections |
| `nextjs-upgrade/SKILL.md` | `refs/tooling.md` Upgrade Protocol |
| `nextjs-upgrade/refs/example.md` | `refs/tooling.md` Upgrade dependency commands |
| All 18 `nextjs-*/evals/evals.json` | No content carried - eval artifacts preserved verbatim in `archive/nextjs/` |

## react

The following sub-skill folders have been merged into `SKILL.md` and `refs/`, then archived under `archive/react/` as non-loadable source trace:

- `archive/react/react-component-patterns/` → merged into `refs/component-patterns.md`
- `archive/react/react-hooks/` → merged into `SKILL.md` and `refs/hooks.md`
- `archive/react/react-performance/` → merged into `refs/performance.md`
- `archive/react/react-security/` → merged into `refs/security.md`
- `archive/react/react-state-management/` → merged into `refs/state-management.md`
- `archive/react/react-testing/` → merged into `refs/testing.md`
- `archive/react/react-tooling/` → merged into `refs/tooling.md`
- `archive/react/react-typescript/` → merged into `SKILL.md` and `refs/component-patterns.md`

## dart

The following sub-skill folders have been merged into `SKILL.md` and `refs/`:

- `dart-language/` → merged into `SKILL.md` (P0 section)
- `dart-best-practices/` → merged into `SKILL.md` (P1 section)
- `dart-tooling/` → superseded by `refs/tooling.md`

