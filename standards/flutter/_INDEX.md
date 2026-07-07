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
