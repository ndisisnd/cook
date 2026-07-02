# Swift Tooling

## SwiftLint

- Install via Swift Package Manager plugin (build-time linting, no separate binary to manage), Homebrew (`brew install swiftlint`), or Mint.
- Config file: `.swiftlint.yml` at the project root.

```yaml
# .swiftlint.yml
disabled_rules:
  - todo
opt_in_rules:
  - force_unwrapping
  - implicitly_unwrapped_optional
  - weak_delegate
  - empty_count
  - first_where
  - contains_over_filter_count
  - fatal_error_message
  - unused_import
  - trailing_comma
included:
  - Sources
excluded:
  - .build
  - Tests/Fixtures

line_length:
  warning: 120
  error: 200
cyclomatic_complexity:
  warning: 15
  error: 25
identifier_name:
  min_length: 2
  excluded: [id, x, y]
```

- `force_cast` and `force_try` are enabled by default; `force_unwrapping` is opt-in — turn it on deliberately given this domain's stance on `!`.
- Analyzer rules (`unused_import`, `unused_declaration`) require the compiler log — run them via `swiftlint analyze` in CI, not the plain lint pass.
- Run `swiftlint --strict` in CI (treats warnings as failures); run plain `swiftlint` locally for iterative feedback. Wire a pre-commit hook on staged files.
- `swiftlint --fix` auto-corrects the mechanical subset of rules; review the diff before committing — some fixes (e.g., `trailing_comma`) are safe, others (opinionated reordering) deserve a human look.
- Justify every `// swiftlint:disable:next <rule>` (or block `disable`/`enable` pair) with a same-line or preceding comment explaining why the rule doesn't apply — an unexplained disable is a smell for the next reader, and CI treats violations as errors.

## swift-format

- Included in the toolchain since Xcode 16 / Swift 6 — no separate install. Invoke via **Editor → Structure → Format File with swift-format** in Xcode, or `swift format` (with a space) from the command line for the toolchain-bundled copy; the standalone open-source binary (installed separately) is invoked as `swift-format`.
- Not wired up as an automatic on-save or on-build formatter by default — set that up explicitly (a build phase script, a pre-commit hook, or an editor extension) if you want it enforced. Run the formatter **before** the linter.
- Config file: `.swift-format` (JSON) at the project root. `swift format lint` checks without modifying (add `--strict`/`-s` to fail on warnings); `swift format format -i` (or `--in-place`) formats in place.
- SwiftLint and swift-format overlap on some style rules (spacing, brace placement) — pick one as the formatting source of truth (typically swift-format) and use SwiftLint primarily for rules it does that swift-format doesn't (force-unwrap/force-cast detection, cyclomatic complexity, custom project rules).

## Swift Package Manager

- `Package.swift` conventions:
```swift
// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "Feature",
    platforms: [.iOS(.v17), .macOS(.v14)],
    products: [
        .library(name: "Feature", targets: ["Feature"]),
    ],
    dependencies: [
        .package(url: "https://github.com/apple/swift-collections.git", .upToNextMajor(from: "1.1.0")),
    ],
    targets: [
        .target(name: "Feature", dependencies: [
            .product(name: "Collections", package: "swift-collections"),
        ]),
        .testTarget(name: "FeatureTests", dependencies: ["Feature"]),
    ]
)
```
- Commit `Package.resolved`. Prefer `.upToNextMajor(from:)` for version requirements — accepts backward-compatible fixes/features, blocks breaking major bumps. This is the recommended default. Apps may pin tighter (`upToNextMinor`/`exact`); libraries expose ranges.
- Use `.exact(_:)` only to pin around a known-bad version or reproduce a specific bug report.
- Never ship a package with a `.branch(_:)`/commit-based dependency — SwiftPM disallows adding a branch-pinned package as a dependency of a version-pinned one, and it breaks reproducible builds. Branch dependencies are for local multi-package development only; remove before tagging a release.
- Wrap third-party dependencies behind your own module so a swap is a one-file change. Prefer packages that ship privacy manifests and are signed.
- `swift-tools-version` sets the **minimum SwiftPM/toolchain version** required to parse the manifest — it is not the same as a target's Swift language mode. Set the language mode explicitly per target with `swiftLanguageMode(.v6)` (or `swiftSettings: [.swiftLanguageMode(.v6)]`) rather than assuming the tools version implies it.
- Enable upcoming-feature flags per target as an incremental migration path: `.enableUpcomingFeature("ExistentialAny")`, `.enableUpcomingFeature("StrictConcurrency")` (pre-6.0 tools), `.enableUpcomingFeature("NonisolatedNonsendingByDefault")` (6.2+ Approachable Concurrency), etc.

## Xcode Build Settings

- **Swift Language Version** — set to 6 deliberately per target, not left on the default forever.
- **Strict Concurrency Checking** (Swift 5 mode only) — Minimal / Targeted / Complete; use Complete as the migration target before flipping the target to Swift 6 mode outright.
- **Default Actor Isolation** (Xcode 26 / Swift 6.2+) — `MainActor` or `nonisolated`; know which your project is set to before reasoning about a bare declaration's isolation (see `refs/concurrency.md`).
- **Treat Warnings as Errors** — enable in CI configurations at minimum; a warning-tolerant CI build lets `Sendable`/deprecation warnings silently accumulate.
- Keep `DEBUG`/`RELEASE` conditional compilation (`#if DEBUG`) minimal and centralized — scattered debug-only branches rot quietly since they aren't exercised by release builds or (often) by CI.
- `os.Logger`: one static logger per category sharing the app subsystem; interpolation is private by default — mark a value `.public` only when it's provably non-sensitive.

## CI Considerations

- Use `macos-latest` (or a pinned macOS version for reproducibility) as the runner; Swift/Xcode versions drift with the runner image, so pin the Xcode version explicitly (`DEVELOPER_DIR` / `xcode-select` / an `xcodebuild -version` check) rather than trusting "latest."
- `swift test` for pure SwiftPM packages; `xcodebuild test -scheme ... -destination ...` (piped through `xcbeautify`) for app targets/workspaces that need a simulator.
- Cache `.build` (SwiftPM) and `~/.cache/org.swift.swiftpm` between CI runs, keyed on the `Package.resolved` hash, to avoid re-resolving/re-fetching dependencies on every job.
- Run in this order, failing fast: (1) `swiftlint --strict` / `swift format lint`, (2) build, (3) unit/Swift Testing suite, (4) UI/XCTest suite (slowest — run last or in parallel on a separate runner).
- For multi-platform packages, matrix the destination rather than assuming a single platform build proves portability.

## Anti-Patterns

- `.branch(_:)` or commit-pinned dependency shipped in a tagged release
- Assuming `swift-tools-version` sets the Swift language mode for concurrency checking
- SwiftLint and swift-format both fighting over the same formatting rules with conflicting configs
- `swiftlint --fix` applied and committed without reviewing the diff
- Unexplained `// swiftlint:disable` with no comment justifying it
- CI without `--strict`/warnings-as-errors, letting lint/compiler warnings accumulate silently
- CI trusting an unpinned "latest" Xcode/Swift version for reproducible builds
- UI/performance XCTest suites run first in CI, slowing feedback on every commit
