# Dart Tooling

## Analysis & Linting

Use `analysis_options.yaml` to enforce project-wide rules.

```yaml
# analysis_options.yaml
include: package:flutter_lints/flutter.yaml

analyzer:
  errors:
    todo: ignore
    missing_required_param: error

linter:
  rules:
    - prefer_single_quotes
    - unawaited_futures
    - require_trailing_commas
    - always_use_package_imports
```

- Run `dart analyze` for pure Dart packages; `flutter analyze --fatal-infos --fatal-warnings` for Flutter apps. Don't mix them.
- Run `dart fix --apply` to auto-apply mechanical lint fixes after updating `analysis_options.yaml`.

## Formatting

- `dart format . --line-length 80` (default). Configurable — some teams use 120. Set once and enforce consistently.
- Run on every commit via pre-commit hook.

## DCM (Dart Code Metrics)

- Use for cyclomatic complexity enforcement (max 15) and structural metrics.
- Run: `dart run dart_code_metrics:metrics analyze lib`
- Note: advanced DCM rules require a commercial license. The base open-source package covers most teams' needs — check before relying on paid rules in CI.

## Build Runner

Always use `--delete-conflicting-outputs` to avoid stale generated file conflicts:

```sh
dart run build_runner build --delete-conflicting-outputs
dart run build_runner watch --delete-conflicting-outputs
```

## Package Management (`pubspec.yaml`)

- Use caret constraints: `^1.0.0`. Avoid exact pins unless reproducing a specific bug.
- Set `publish_to: none` for app packages (not library packages).
- Run `dart pub outdated` regularly to surface available upgrades.
- Run `dart pub upgrade` to apply non-breaking upgrades within constraints.

```yaml
# pubspec.yaml (app package)
publish_to: none

environment:
  sdk: '>=3.0.0 <4.0.0'

dependencies:
  flutter:
    sdk: flutter

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^4.0.0
```

## Coverage

```sh
flutter test --coverage
genhtml coverage/lcov.info -o coverage/html
```

Or for pure Dart:

```sh
dart test --coverage=coverage
dart pub run coverage:format_coverage --lcov --in=coverage --out=coverage/lcov.info
```

## CI Pipeline

All PRs must pass these steps in order — fail fast:

1. `dart analyze` / `flutter analyze --fatal-infos --fatal-warnings`
2. `dart format . --set-exit-if-changed`
3. `dart run dart_code_metrics:metrics analyze lib`
4. `flutter test` / `dart test`

Never run `flutter build` before `flutter analyze`.

## DevTools

Use Dart DevTools (`dart devtools`) for heap profiling, CPU timeline tracing, and widget inspection. Open automatically with `flutter run` in debug mode or launch manually via `dart devtools`.

## Pre-commit (lefthook)

Keep `lefthook.yml` in sync with the CI steps above:

```yaml
# lefthook.yml
pre-commit:
  commands:
    analyze:
      run: flutter analyze --fatal-infos --fatal-warnings
    format:
      run: dart format . --set-exit-if-changed
    metrics:
      run: dart run dart_code_metrics:metrics analyze lib
```

## Anti-Patterns

- `build_runner` without `--delete-conflicting-outputs`
- `flutter build` before `flutter analyze`
- `// ignore:` comment without an explanation of why
- Skipping `dart format` in pre-commit
- Mixing `dart analyze` and `flutter analyze` in the wrong project type
- Exact version pins without a comment explaining why
