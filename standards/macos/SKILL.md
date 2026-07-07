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
---

# macOS Standards

Default load: this file only; pull refs only when needed.

Applies to macOS app targets only — never iOS/iPadOS/watchOS/visionOS, even when `Info.plist`/entitlements globs match. Swift language rules → `standards/swift/`; universal rules → `standards/global/`; secret policy → `global/refs/security.md`.

**Scope:** full force for new targets and modules. In existing code, match established conventions; propose migrations (persistence stack, deployment target, architecture slices) as separate explicit tasks, never as a side effect.

## P0 — Platform Correctness

### Platform Baseline (2026)
- Ship universal 2 (arm64 + x86_64) while the deployment target spans Intel-capable macOS; verify with `lipo -info`. arm64-only is a deliberate decision → `refs/distribution.md`.
- Build with the current Xcode/SDK — required for Liquid Glass and current-OS behavior. SDK version ≠ deployment target.
- New apps: minimum deployment macOS 15 default; 14 is the practical floor (loses `@Observable`, modern scene APIs). Never bump an existing target as a side effect.

### App Structure & Lifecycle
- SwiftUI lifecycle (`@main struct App: App`); never `@NSApplicationMain`, hand-written `main.swift`, or `NSApplication.main()` for new *app* code (non-app bundles legitimately differ).
- `@NSApplicationDelegateAdaptor` only for what SwiftUI can't do; keep it a thin bridge. Scope, Dock-reopen gap, URL schemes → `refs/windows-and-scenes.md`.
- AppKit bridging: SwiftUI-first; wrap only the missing control, never a whole screen; strict concurrency on (AppKit is `@MainActor`-only). Gaps + pattern → `refs/architecture-and-state.md`.

### Sandbox & File Access
- Sandbox on by default; narrowest entitlements — a missing entitlement means TCC never even prompts. Detail → `refs/sandbox-and-tcc.md`.
- User files only via user intent (`NSOpenPanel`/`fileImporter`, drag & drop); persist with security-scoped bookmarks, balancing every `start`/`stop`.
- Secrets go in the Keychain — never `UserDefaults`, plists, or bundled files.

### Permissions (TCC)
- Request lazily at point of use with clear purpose strings; on denial degrade gracefully and deep-link to System Settings; never re-prompt loop.
- Per-resource grant paths (some have no prompt API) + stable-dev-signing-identity rule → `refs/sandbox-and-tcc.md`.

### Distribution
- Outside the App Store: Developer ID + hardened runtime + notarization is effectively mandatory (macOS 15+ removed the easy Gatekeeper bypass). Signing/stapling/CI mechanics → `refs/distribution.md`.
- Updates outside MAS: Sparkle 2 only — never in a MAS build. Setup → `refs/distribution.md`.

### User-Facing Text & Formatting
- All user-visible strings via String Catalog / `String(localized:)`; never concatenate sentence fragments; plurals via catalog variants. Detail → `refs/localization.md`.
- User-facing dates/numbers via `FormatStyle`/`.formatted()` (locale-aware, cached); wire formats locale-independent (ISO 8601 / `en_US_POSIX`); never `String(format:)`.

### State & Data
- `@Observable` over `ObservableObject` on macOS 14+; inject via `@Environment(Type.self)`, not `@EnvironmentObject`. Ownership/init gotchas, Core Data concurrency, persistence choice → `refs/architecture-and-state.md`.
- `@AppStorage`/`UserDefaults` for small preferences only. Per-window UI state in `@SceneStorage`; scenes don't share `@State`.

### Background Work & Helpers
- XPC for privilege separation and crash isolation; validate callers by code signature (audit token), never PID. Detail → `refs/sandbox-and-tcc.md`.
- Login items/agents/daemons via `SMAppService`; respect App Nap; don't poll where change notifications exist; tolerance on every timer. Detail → `refs/performance-accessibility.md`.

## P1 — Platform Conventions (HIG)

Load from refs: windows/scenes/menus/documents → `refs/windows-and-scenes.md`; SwiftUI view hygiene + accessibility → `refs/performance-accessibility.md`; Liquid Glass appearance, undo, pasteboard, App Intents → `refs/hig-conventions.md`.

## Anti-Patterns

- `@NSApplicationMain`/hand-written `main.swift` for a new app; `NSApplicationDelegate` as a parallel architecture
- New `ObservableObject`/`@Published`/Combine view models for new code; `@EnvironmentObject` for an `@Observable` type
- AppKit calls off the main thread; disabling strict concurrency to silence them
- Rewriting an entire screen in AppKit to work around one missing control — wrap just that control
- Synchronous file I/O or long work on the main thread (beachballs); unbounded synchronous Core Data/SwiftData fetch on the main context
- Assuming `NSOpenPanel` access persists across relaunch; unbalanced bookmark `start`/`stop`
- Secrets in `UserDefaults` or bundled plists
- Un-notarized Developer ID builds; `get-task-allow` in release entitlements; outside-in signing; Sparkle in a MAS build
- Unretained `NSStatusItem` or window controllers (silently vanish)
- Re-prompt loops for denied TCC permissions; attempting to "prompt" for Full Disk Access (no API exists)
- Hardcoded English strings; sentence-building by concatenation; `String(format:)` for user-facing numbers; `DateFormatter` allocated inside `body`
- `NSManagedObject` crossing actor boundaries; `viewContext` used for background work
- Unstable `ForEach` identity; `AnyView` in hot hierarchies
- Polling where change notifications exist; timers without tolerance; heavy work in `applicationDidFinishLaunching`/`App.init`
- Trusting an XPC caller by PID instead of its audit token / code-signing requirement
- Deprecated APIs: `SMLoginItemSetEnabled`, `SMJobBless`, `altool`
- Hand-building a Preferences window instead of the `Settings` scene; mutating `NSMenu` where `.commands {}` works; mouse-only custom controls
- iOS-isms on Mac: no menu bar items, hidden navigation, touch-only affordances; assuming free Dynamic Type from `Font.TextStyle`
- Colors that ignore dark mode or contrast; UI untested under Reduce Transparency; new Rosetta-dependent components

## References

- [architecture-and-state](refs/architecture-and-state.md) — AppKit bridging + gap list, Observation, `@State`/`@Bindable` ownership, DI, MVVM, SwiftData vs Core Data
- [windows-and-scenes](refs/windows-and-scenes.md) — scenes/windows, delegate adaptor + Dock-reopen gap, menu bar apps, commands/keyboard, focus, document apps
- [sandbox-and-tcc](refs/sandbox-and-tcc.md) — App Sandbox, entitlements, hardened runtime, Keychain, TCC grant flows, code signing, XPC security
- [distribution](refs/distribution.md) — certificates, `notarytool`/stapling, MAS constraints, Sparkle 2, universal binaries, dmg/pkg, CI signing
- [performance-accessibility](refs/performance-accessibility.md) — view hygiene, Instruments, main-thread/beachball, background work + `SMAppService`/App Nap, launch time, VoiceOver, `@ScaledMetric`
- [localization](refs/localization.md) — String Catalogs, plurals, `FormatStyle`, formatter caching, pseudo-localization, RTL
- [hig-conventions](refs/hig-conventions.md) — Liquid Glass appearance, dark-mode colors, SF Symbols, drag & drop/`Transferable`, undo, pasteboard, App Intents
