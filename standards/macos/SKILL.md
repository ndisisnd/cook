---
name: macos
description: macOS app development standards — SwiftUI/AppKit app structure, scenes and windows, menu bar apps, sandboxing and TCC, signing and notarization, distribution, persistence, localization and formatting, and platform conventions (HIG, Liquid Glass, accessibility, undo). Scoped to macOS only — not iOS/iPadOS/watchOS/visionOS.
metadata:
  triggers:
    files:
      - '**/*.entitlements'
      - '**/Info.plist'
    keywords:
      - AppKit
      - NSWindow
      - NSStatusItem
      - MenuBarExtra
      - menu bar app
      - WindowGroup
      - DocumentGroup
      - Settings scene
      - SwiftUI
      - App Sandbox
      - entitlement
      - security-scoped
      - TCC
      - notarization
      - codesign
      - hardened runtime
      - Gatekeeper
      - Sparkle
      - XPC
      - SMAppService
      - NSPanel
      - Developer ID
      - Liquid Glass
      - Core Data
      - SwiftData
      - String Catalog
      - VoiceOver
      - App Intents
  targets: "macOS 26+ deployment · built with Xcode 27 / macOS 27 SDK · Swift 6.2+"
  last_reviewed: 2026-10-18
---

# macOS Standards

Target: macOS 26+ deployment for new apps, built with Xcode 27 and the macOS 27 SDK. Default load: this file only.

Applies to macOS app targets only — never iOS/iPadOS/watchOS/visionOS, even when `Info.plist`/entitlements globs match; iOS/iPadOS → `standards/ios/`. Swift language rules → `standards/swift/`; universal rules → `standards/global/`; secret policy → `global/refs/security.md`.

**Scope:** full force for new targets. In existing code, match conventions; propose migrations (persistence stack, deployment target, architecture slices) as separate tasks.

## P0 — Platform Correctness

### Platform Baseline (Oct 2026)
- Build with Xcode 27 / macOS 27 SDK. SDK version ≠ deployment target. App Store Connect has required Xcode 26+ for uploads since 2026-04-28.
- New apps: deployment target macOS 26 (Liquid Glass APIs, `Observations`). Go lower (15, or 14 as the `@Observable` floor) only for a stated user-base reason. Never bump an existing target as a side effect.
- Architectures: macOS 27 runs only on Apple silicon; macOS 26 is the last release for Intel Macs, and macOS 27 is the last with general Rosetta 2 support. Below a 27 deployment target `$(ARCHS_STANDARD)` is universal (arm64 + x86_64); at 27+ it is arm64-only — add `x86_64` to `ARCHS` explicitly to stay universal. Verify with `lipo -info` → `refs/distribution.md`.
- Ship a `PrivacyInfo.xcprivacy`, and require one from every third-party SDK.

### App Structure & Lifecycle
- SwiftUI lifecycle (`@main struct App: App`); never `@NSApplicationMain`, hand-written `main.swift`, or `NSApplication.main()` for new *app* code.
- `@NSApplicationDelegateAdaptor` only for what SwiftUI can't do; keep it thin. Dock reopen, URL schemes → `refs/windows-and-scenes.md`.
- AppKit bridging: SwiftUI-first; wrap only the missing control, never a whole screen; strict concurrency on (AppKit is `@MainActor`-only). Gaps → `refs/architecture-and-state.md`.

### Sandbox & File Access
- Sandbox on by default; narrowest entitlements (a missing entitlement means TCC never prompts).
- User files only via user intent (`NSOpenPanel`/`fileImporter`, drag & drop); persist via security-scoped bookmarks, balancing every `start`/`stop`.
- Secrets go in the Keychain — never `UserDefaults`, plists, or bundled files. Detail → `refs/sandbox-and-tcc.md`.

### Permissions (TCC)
- Request lazily at point of use with clear purpose strings; on denial degrade and deep-link to System Settings; never re-prompt in a loop.
- Grant paths (Full Disk Access has no prompt API), stable dev signing identity → `refs/sandbox-and-tcc.md`.

### Distribution
- Outside the App Store: Developer ID + hardened runtime + notarization is effectively mandatory (macOS 15+ removed the easy Gatekeeper bypass).
- Updates outside MAS: Sparkle 2 only — never in a MAS build. Mechanics → `refs/distribution.md`.

### User-Facing Text & Formatting
- All user-visible strings via String Catalog / `String(localized:)`; never concatenate sentence fragments; plurals via catalog variants. Detail → `refs/localization.md`.
- User-facing dates/numbers via `FormatStyle`/`.formatted()`; wire formats locale-independent (ISO 8601 / `en_US_POSIX`); never `String(format:)`.

### State & Data
- `@Observable` over `ObservableObject` on macOS 14+; inject via `@Environment(Type.self)`, not `@EnvironmentObject`. Ownership, Core Data concurrency, persistence choice → `refs/architecture-and-state.md`.
- `@AppStorage`/`UserDefaults` for small preferences only. Per-window UI state in `@SceneStorage`.

### Background Work & Helpers
- XPC for privilege separation and crash isolation; validate callers by code signature (audit token), never PID.
- Login items/agents/daemons via `SMAppService`; respect App Nap; don't poll where change notifications exist; tolerance on every timer → `refs/performance-accessibility.md`.

## P1 — Platform Conventions (HIG)

- Previews use the `#Preview` macro, never `PreviewProvider`.
- GCD/Combine rules → `standards/swift/refs/concurrency.md`.
- Windows/menus/documents, view hygiene, accessibility, Liquid Glass, undo, App Intents → see References.

## Anti-Patterns

- `NSApplicationDelegate` as a parallel architecture; AppKit calls off the main thread
- Long sync work or unbounded Core Data/SwiftData fetches on the main thread; `NSManagedObject` crossing actors
- `get-task-allow` in release entitlements; outside-in signing; `SMLoginItemSetEnabled`, `SMJobBless`, `altool`
- Hand-built Preferences window instead of `Settings` scene; mutating `NSMenu` where `.commands {}` works; mouse-only custom controls
- iOS-isms on Mac (no menu bar items, hidden navigation, touch-only affordances); assuming free Dynamic Type from `Font.TextStyle`; new Rosetta-dependent components

## References

- [architecture-and-state](refs/architecture-and-state.md) — AppKit bridging, Observation, DI, SwiftData vs Core Data
- [windows-and-scenes](refs/windows-and-scenes.md) — scenes/windows, menu bar apps, commands, documents
- [sandbox-and-tcc](refs/sandbox-and-tcc.md) — Sandbox, entitlements, Keychain, TCC, signing, XPC
- [distribution](refs/distribution.md) — notarization, MAS, Sparkle 2, universal binaries, dmg/pkg, CI
- [performance-accessibility](refs/performance-accessibility.md) — view hygiene, Instruments, `SMAppService`, VoiceOver
- [localization](refs/localization.md) — String Catalogs, plurals, `FormatStyle`, RTL
- [hig-conventions](refs/hig-conventions.md) — Liquid Glass, toolbar, sidebar, `Table`, Settings, undo, pasteboard, App Intents
