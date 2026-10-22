---
last_reviewed: 2026-10-18
---

# Swift Tooling

## SwiftLint

- Config: `.swiftlint.yml` at the project root.
- Opt in: `force_unwrapping`, `implicitly_unwrapped_optional`, `weak_delegate`, `empty_count`, `first_where`, `contains_over_filter_count`, `fatal_error_message`, `unused_import`, `trailing_comma`. Disable `todo`. Line length warn 120 / error 200; cyclomatic complexity warn 15 / error 25.
- `force_cast` and `force_try` are on by default; `force_unwrapping` is opt-in — enable it, given this domain's stance on `!`.
- Analyzer rules (`unused_import`, `unused_declaration`) need the compiler log: run `swiftlint analyze` in CI, not the plain lint pass.
- CI: `swiftlint --strict`. Local: plain `swiftlint` plus a pre-commit hook on staged files.
- Review the diff after `swiftlint --fix` before committing.
- Every `// swiftlint:disable` (line or block) carries a comment saying why.

## swift-format

- Bundled with the toolchain since Xcode 16 / Swift 6: `swift format` (with a space) on the command line, or Editor → Structure → Format File with swift-format. The standalone binary is `swift-format`.
- Not run on save or build by default; wire it up explicitly (build phase, pre-commit hook, editor extension). Run it before the linter.
- Config: `.swift-format` (JSON) at the project root. `swift format lint` checks (`--strict`/`-s` fails on warnings); `swift format format -i` formats in place.
- Pick one formatting source of truth (typically swift-format). Use SwiftLint for what swift-format lacks: force-unwrap/cast detection, complexity, custom rules.

## Swift Package Manager

- Manifest shape: `// swift-tools-version: 6.0`, `platforms: [.iOS(.v17), .macOS(.v14)]`, `.package(url: "https://github.com/apple/swift-collections.git", .upToNextMajor(from: "1.1.0"))`.
- Commit `Package.resolved`. Prefer `.upToNextMajor(from:)` for version requirements — accepts backward-compatible fixes/features, blocks breaking major bumps. This is the recommended default. Apps may pin tighter (`upToNextMinor`/`exact`); libraries expose ranges.
- Use `.exact(_:)` only to pin around a known-bad version or reproduce a specific bug report.
- Never ship a package with a `.branch(_:)`/commit-based dependency — SwiftPM disallows it under a version-pinned parent and it breaks reproducible builds. Branch deps are for local multi-package development only; remove before tagging a release.
- Wrap third-party dependencies behind your own module. Prefer packages with privacy manifests and signing.
- `swift-tools-version` is the minimum toolchain to parse the manifest, not the language mode. Set the mode explicitly per target: `swiftSettings: [.swiftLanguageMode(.v6)]`.
- Upcoming-feature flags per target for incremental migration: `.enableUpcomingFeature("ExistentialAny")`, `"StrictConcurrency"` (pre-6.0 tools), `"NonisolatedNonsendingByDefault"` (6.2+ Approachable Concurrency).

## Xcode Build Settings

- **Swift Language Version**: set to 6 deliberately per target.
- **Strict Concurrency Checking** (Swift 5 mode only): use Complete as the migration target before switching to Swift 6 mode.
- **Default Actor Isolation** (Xcode 26 / Swift 6.2+): `MainActor` or `nonisolated`. Know the project's setting before reasoning about a bare declaration (`refs/concurrency.md`).
- **Treat Warnings as Errors**: on in CI at minimum.
- Keep `#if DEBUG` conditional compilation minimal and centralized — scattered debug-only branches rot because release builds and CI rarely exercise them.
- `os.Logger`: one static logger per category, shared app subsystem. Interpolation is private by default; mark `.public` only when provably non-sensitive.

## CI Considerations

- Pin the Xcode version explicitly (`DEVELOPER_DIR` / `xcode-select` / an `xcodebuild -version` check); never trust "latest" on `macos-latest` or any runner image.
- `swift test` for pure packages; `xcodebuild test -scheme ... -destination ...` for app targets needing a simulator.
- Cache `.build` and `~/.cache/org.swift.swiftpm` between runs, keyed on the `Package.resolved` hash.
- Order, fail fast: lint (`swiftlint --strict` / `swift format lint`), build, unit/Swift Testing, then UI/XCTest last or on a separate runner.
- Multi-platform packages: matrix the destinations; one platform build does not prove portability.
