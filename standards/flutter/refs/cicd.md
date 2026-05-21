# Flutter CI/CD Standards

**Priority: P1 (HIGH)**

## Core Pipeline Steps

1. **Environment Setup**: Use stable Flutter channel. Cache dependencies (pub, gradle, cocoapods).
2. **Static Analysis**: Enforce `flutter analyze` and `dart format`. Fail on any warning in strict mode.
3. **Testing**: Run unit, widget, and integration tests. Upload coverage reports (e.g., Codecov).
4. **Build**:
   - **Android**: Build App Bundle (`.aab`) for Play Store.
   - **iOS**: Sign and build `.ipa` (requires macOS runner).
5. **Deployment (CD)**: Automated upload to TestFlight/Play Console using standard tools (Fastlane, Codemagic).

## Best Practices

- **Timeout Limits**: Always set `timeout-minutes` (e.g., 30m) to save costs on hung jobs.
- **Fail Fast**: Run Analyze/Format _before_ Tests/Builds.
- **Secrets**: Never commit keys. Use GitHub Secrets or secure vaults for `keystore.jks` and `.p8` certs.
- **Versioning**: Automate version bumping based on git tags or semantic version scripts.

## Anti-Patterns

- **No secrets in repo**: Store `keystore.jks`, `.p8`, and `.env` in GitHub Secrets.
- **No uncapped jobs**: Always set `timeout-minutes` to save runner minutes.
- **No manual versioning**: Automate `pubspec.yaml` versioning via git tags or scripts.
- **No late analysis**: Run `flutter analyze` before builds/tests for fast failure.

---

## GitHub Actions

### Standard Workflow (`flutter-ci.yml`)

```yaml
name: Flutter CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    name: Build & Test
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Java
        uses: actions/setup-java@v4
        with:
          distribution: 'zulu'
          java-version: '17'

      - name: Set up Flutter
        uses: subosito/flutter-action@v2
        with:
          channel: 'stable'
          cache: true

      - name: Install dependencies
        run: flutter pub get

      - name: Format check
        run: dart format --output=none --set-exit-if-changed .

      - name: Analyze
        run: flutter analyze

      - name: Run tests
        run: flutter test --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: coverage/lcov.info
          token: ${{ secrets.CODECOV_TOKEN }}
```

### Advanced Large-Scale Workflow (`main.yml`)

For large projects, use parallel jobs and aggressive caching to fail fast.

```yaml
name: Production CI

on: [push, pull_request]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  # 1. SETUP: Install & Cache Dependencies
  setup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          channel: 'stable'
          cache: true
      - name: Install Dependencies
        run: flutter pub get

  # 2. QUALITY: Static Analysis & Formatting (Runs parallel to Test)
  quality:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
      - run: flutter pub get
      - name: Verify Formatting
        run: dart format --output=none --set-exit-if-changed .
      - name: Static Analysis
        run: flutter analyze --fatal-infos

  # 3. TEST: Unit & Widget Tests
  test:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
      - run: flutter pub get
      - name: Run Tests
        run: flutter test --coverage --concurrency=4
      - name: Upload Coverage
        uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
```

**Key Optimizations:**
1. **Concurrency Group**: `cancel-in-progress: true` stops old runs when new code is pushed, saving minutes.
2. **Parallel Jobs**: `quality` and `test` trigger at the same time. If formatting fails, you don't wait for tests.
3. **Fatal Infos**: Treat info-level logic hints as failures for higher quality enforcement.

---

## Fastlane Standards

Automates signing, build versioning, flavors, and multi-channel distribution.

### Prerequisites

1. **Versioning**: Use `flutter_version` or `cider` to sync Fastlane with `pubspec.yaml`.
2. **Firebase**: Install plugin: `bundle exec fastlane add_plugin firebase_app_distribution`.
3. **Flavors**: Ensure your Flutter app is set up with Flavors (e.g., `dev`, `prod` schemes).

### Android (`android/fastlane/Fastfile`)

```ruby
default_platform(:android)

platform :android do
  def load_version
    require 'yaml'
    pubspec = YAML.load_file("../../pubspec.yaml")
    return pubspec['version'].split('+') # Returns [version, build]
  end

  desc "Deploy Staging to Firebase"
  lane :staging do
    version_name, version_code = load_version

    gradle(
      task: "assemble",
      flavor: "Dev",
      build_type: "Release",
      properties: {
        "android.injected.version.code" => version_code,
        "android.injected.version.name" => version_name
      }
    )

    firebase_app_distribution(
      app: ENV["FIREBASE_APP_ID_ANDROID_DEV"],
      groups: "qa-team",
      release_notes: "Staging Build v#{version_name} (#{version_code})"
    )
  end

  desc "Deploy Production to Play Store"
  lane :prod do
    version_name, version_code = load_version

    gradle(
      task: "bundle",
      flavor: "Prod",
      build_type: "Release",
      properties: {
        "android.injected.version.code" => version_code,
        "android.injected.version.name" => version_name
      }
    )

    upload_to_play_store(
      track: "internal",
      json_key: ENV["PLAY_STORE_JSON_KEY_FILE"],
      skip_upload_metadata: true,
      skip_upload_images: true,
      skip_upload_screenshots: true
    )
  end
end
```

### iOS (`ios/fastlane/Fastfile`)

```ruby
default_platform(:ios)

platform :ios do
  before_all do
    setup_ci if ENV['CI']
  end

  desc "Deploy Staging to Firebase (AdHoc)"
  lane :staging do
    match(type: "adhoc", app_identifier: "com.example.app.dev", readonly: is_ci)

    build_app(
      scheme: "Dev",
      export_method: "ad-hoc",
      include_bitcode: false
    )

    firebase_app_distribution(
      app: ENV["FIREBASE_APP_ID_IOS_DEV"],
      groups: "qa-team"
    )
  end

  desc "Deploy Production to TestFlight"
  lane :prod do
    match(type: "appstore", app_identifier: "com.example.app", readonly: is_ci)

    build_app(
      scheme: "Prod",
      export_method: "app-store"
    )

    upload_to_testflight(
      skip_waiting_for_build_processing: true
    )
  end
end
```

### Setup Checklist

1. **Google Play Key**: Define `PLAY_STORE_JSON_KEY_FILE`.
2. **Match Repo**: Ensure `git_url` in `Matchfile` points to your private cert repo.
3. **Firebase CLI**: Ensure firebase-tools is installed or the plugin authenticated via `FIREBASE_TOKEN`.
