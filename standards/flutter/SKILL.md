---
name: flutter
description: Universal Flutter coding standards. Use when writing or reviewing any Flutter/Dart UI code — widgets, state management, navigation, architecture, performance, or testing.
metadata:
  triggers:
    files:
      - '**/*.dart'
    keywords:
      - Widget
      - StatelessWidget
      - const
      - build
      - Theme
      - SizedBox
      - ListView
---

# Flutter Standards

## P0 — Design System Enforcement (CRITICAL)

Zero tolerance for hardcoded design values.

Before any UI work, identify the project's Theme Archetype by checking `main.dart`:
- **Theme-Driven**: `VThemeData(...).toThemeData()` → use `Theme.of(context).textTheme`
- **Token-Driven**: Use static tokens (`VTypography.*`) only when no global theme bridge exists or when defining the theme itself

**Rules:**
- **Colors**: Use tokens (`VColors.*`, `AppColors.*`). Never `Color(0xFF...)` or `Colors.red`.
- **Spacing**: Use tokens (`VSpacing.*`). Never magic numbers like `16` or `24`.
- **Typography**: Prefer `Theme.of(context).textTheme.*` for adaptive UI. Use `VTypography.*` only for theme definitions. Never inline `TextStyle`.
- **Borders**: Use tokens (`VBorders.*`). Never raw `BorderRadius.circular(n)`.
- **Components**: Use DLS widgets (`VButton`) over raw Material widgets (`ElevatedButton`) when available.

Detail → `refs/design-system.md`

## P0 — Error Handling (CRITICAL)

- **Repositories return `Either<Failure, T>`** — no exceptions propagate to UI or BLoC.
- **Catch in Infrastructure only** — convert `DioException` / external errors to typed `Left(Failure)`.
- **Fold in BLoC** — `.fold(failure, success)` to emit states. No try/catch in BLoC.
- **Typed failures** — `@freezed` union failures (e.g., `UnauthorizedFailure`). Never `Left('string')`.
- **Crashlytics routing** — all `catch` blocks route via `AppLogger.error(...)` for observability.
- **`on Type catch`** — never bare `catch` without `on`.

Detail → `refs/error-handling.md`

## P1 — Widgets (OPERATIONAL)

- **State**: Use `StatelessWidget` by default. `StatefulWidget` only for local state/controllers.
- **Composition**: Extract UI into small, atomic `const` widgets.
- **Theming**: Use `Theme.of(context)`. No hardcoded colors.
- **Layout**: Use `Flex` + `Gap`/`SizedBox`.
- **Widget Keys**: All interactive elements must use keys from `widget_keys.dart`.
- **File Size**: If a UI file exceeds ~80 lines, extract sub-widgets into private classes.
- **Specialized**:
  - `SelectionArea`: For multi-widget text selection.
  - `InteractiveViewer`: For zoom/pan.
  - `ListWheelScrollView`: For pickers.
  - `IntrinsicWidth/Height`: Avoid unless strictly required; for overlays prefer `Stack + FractionallySizedBox`.
- **Large Lists**: Always use `ListView.builder`.

```dart
class AppButton extends StatelessWidget {
  final String label;
  final VoidCallback onPressed;
  const AppButton({super.key, required this.label, required this.onPressed});

  @override
  Widget build(BuildContext context) =>
      ElevatedButton(onPressed: onPressed, child: Text(label));
}
```

## P1 — Idiomatic Flutter (OPERATIONAL)

- **Async Gaps**: Check `if (context.mounted)` before using `BuildContext` after `await`.
- **Composition**: Extract complex UI into small widgets. Avoid deep nesting or large helper methods.
- **Spacing**:
  - Prefer `spacing` parameter on `Row`/`Column` (Flutter 3.10+) over inserting gaps between children.
  - Fallback: Use `Gap(n)` or `SizedBox` only when `spacing` cannot express the layout.
  - Empty UI: Use `const SizedBox.shrink()`.
  - Simple gaps: Prefer `Gap(n)` or `SizedBox` over `Padding`.
- **Container**: Use `ColoredBox`/`Padding`/`DecoratedBox` instead of `Container` where possible.
- **Themes**: Use extensions for `Theme.of(context)` access.
- **No `_buildXxx()` helpers**: Extract to `const StatelessWidget` for proper rebuild control.

## P1 — Performance (OPERATIONAL)

- **Rebuilds**: Use `const` widgets and `buildWhen` / `select` for granular updates.
- **Lists**: Always use `ListView.builder` for item recycling.
- **Heavy Tasks**: Use `compute()` or `Isolates` for parsing/logic.
- **Repaints**: Use `RepaintBoundary` for complex animations. Debug with `debugRepaintRainbowEnabled`.
- **Images**: Use `CachedNetworkImage` + `memCacheWidth`. Use `precachePicture` for SVGs. Always set `maxWidth`/`maxHeight`.
- **Keys**: Provide `ValueKey` for list items and stable IDs.
- **Resource Cleanup**: Dispose controllers/streams in `dispose()`.
- **Pagination**: Default to 20 items per page for network lists.
- **Build Purity**: Keep `build()` free of heavy work; move logic to BLoC/Application.

```dart
BlocBuilder<UserBloc, UserState>(
  buildWhen: (p, c) => p.id != c.id,
  builder: (context, state) => Text(state.name),
)
```

## Anti-Patterns

- **No hardcoded colors/spacing**: `Color(0xFF...)`, `Colors.red`, `SizedBox(height: 10)` are forbidden.
- **No inline `TextStyle`**: Use `theme.textTheme.*` or design tokens.
- **No setState for server state**: Server or shared state belongs in BLoC.
- **No widget file over 80 lines without extraction**.
- **No inline Key strings**: All keys must be constants defined in `widget_keys.dart`.
- **No `_buildXxx()` helper methods**: Extract to `const StatelessWidget` private class.
- **No manual widget repetition**: When 3+ sibling widgets differ only in data, map over a list.
- **No BuildContext after await without mounted check**.
- **No root `setState()`**: Use `BlocBuilder` with `buildWhen` or `context.select()`.
- **No heavy work in `build()`**: Move sorting/filtering/heavy logic to BLoC or `compute()`.
- **No non-`const` leaf nodes**: Apply `const` to all static widgets.
- **No large `Column` lists**: Use `ListView.builder`.
- **No try/catch in BLoC**: BLoC receives `Either` and folds.
- **No plain string failures**: Define typed `@freezed` Failure subclasses.
- **No silent catch blocks**: Always log and propagate.
- **No direct controller access in widget**: Use BLoC or Signals to decouple UI from state.

## References

Load only what the current task requires:

- [state-management](refs/state-management.md) — BLoC/Cubit, Riverpod, or GetX state; files matching `**_bloc.dart`, `**_cubit.dart`, `**_provider.dart`, `**_notifier.dart`, `**_controller.dart`; keywords: Bloc, Cubit, Riverpod, GetX, Obx, AsyncValue, ref.watch
- [navigation](refs/navigation.md) — routing with go_router, auto_route, or GetX; files matching `**/*router*.dart`, `**/app_pages.dart`, `**/main.dart`; keywords: GoRouter, AutoRoute, GetPage, Navigator, deep link, redirect
- [architecture](refs/architecture.md) — feature-based or layer-based clean architecture; files under `lib/features/**`, `lib/domain/**`, `lib/infrastructure/**`, `lib/application/**`; keywords: feature, domain, infrastructure, DTO, mapper, Either
- [networking](refs/networking.md) — Dio/Retrofit HTTP clients and interceptors; files under `**/data_sources/**`, `**/api/**`; keywords: Dio, Retrofit, RestClient, Interceptor, token refresh
- [error-handling](refs/error-handling.md) — Either/Failure detail and API error mapping; files under `lib/domain/**`, `lib/infrastructure/**`; keywords: Either, fold, Left, Right, Failure, dartz
- [dependency-injection](refs/dependency-injection.md) — get_it + injectable setup; files matching `**/injection.dart`, `**/locator.dart`; keywords: GetIt, injectable, singleton, module
- [design-system](refs/design-system.md) — DLS token usage, modular and monolithic patterns; files under `**/theme/**`, `**/*_theme.dart`, `**/*_colors.dart`; keywords: ThemeData, ColorScheme, AppColors, design token
- [localization](refs/localization.md) — easy_localization with CSV/JSON; files under `**/translations/*.json`, `**/langs/*.csv`; keywords: localization, tr(), easy_localization
- [notifications](refs/notifications.md) — FCM + flutter_local_notifications; files matching `**/*notification*.dart`; keywords: FCM, FirebaseMessaging, push
- [security](refs/security.md) — OWASP Mobile, secure storage, pinning, obfuscation; files under `lib/infrastructure/**`, `pubspec.yaml`; keywords: secure_storage, pinning, jailbreak, OWASP, PII
- [concurrency](refs/concurrency.md) — isolates and compute() for heavy tasks; files matching `**/*isolate*.dart`, `**/*worker*.dart`; keywords: Isolate, compute, ReceivePort, background
- [cicd](refs/cicd.md) — GitHub Actions and Fastlane pipelines; files under `.github/workflows/**.yml`, `fastlane/**`; keywords: ci, cd, pipeline, deploy, workflow
- [testing](refs/testing.md) — unit, widget, integration, robot pattern, mocking, bloc tests, widget keys; files under `**/test/**.dart`, `**/integration_test/**.dart`, `**/robots/**.dart`; keywords: test, patrol, robot, blocTest, mocktail, WidgetKeys
