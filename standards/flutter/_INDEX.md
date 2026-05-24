<!-- AUTO-GENERATED from SKILL.md frontmatters — do not edit manually -->
# flutter Skills Index

## File Match (auto-check against the file you are editing)

| Skill | File pattern | Keywords |
| ----- | ------------ | -------- |
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

> Load `<SKILLS>/flutter/SKILL.md` for any `.dart` file — it covers universal Flutter P0/P1 rules (design system, error handling, widgets, idiomatic patterns, performance).
> Load `<SKILLS>/flutter/refs/state-management.md` when touching BLoC, Cubit, Riverpod, or GetX state files.
> Load `<SKILLS>/flutter/refs/navigation.md` when touching router, navigation, or app_pages files.
> Load `<SKILLS>/flutter/refs/architecture.md` when working in `lib/features/`, `lib/domain/`, `lib/infrastructure/`, or `lib/application/`.
> Load `<SKILLS>/flutter/refs/networking.md` when touching data sources, API clients, or Dio/Retrofit files.
> Load `<SKILLS>/flutter/refs/error-handling.md` when working with Either, Failure, or dartz in domain/infrastructure layers.
> Load `<SKILLS>/flutter/refs/dependency-injection.md` when touching injection.dart, locator.dart, or injectable annotations.
> Load `<SKILLS>/flutter/refs/design-system.md` when working in theme, colors, or DLS token files.
> Load `<SKILLS>/flutter/refs/localization.md` when touching translation JSON/CSV assets or easy_localization.
> Load `<SKILLS>/flutter/refs/notifications.md` when touching FCM, firebase_messaging, or flutter_local_notifications.
> Load `<SKILLS>/flutter/refs/security.md` when touching secure_storage, pinning, obfuscation, or OWASP concerns.
> Load `<SKILLS>/flutter/refs/concurrency.md` when touching isolate, compute, or background worker files.
> Load `<SKILLS>/flutter/refs/cicd.md` when touching GitHub Actions workflows or Fastlane files. A Flutter CI/CD task also loads the vendor-neutral `concern:cicd` (`<SKILLS>/global/refs/cicd.md`) alongside it — concerns load on top of the matched domain.
> Load `<SKILLS>/flutter/refs/testing.md` when writing or reviewing any test, robot, integration test, or widget key file.

## Archived

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
