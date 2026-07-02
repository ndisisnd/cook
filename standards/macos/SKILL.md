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

Default load: this file only. Pull refs only when the task needs that depth.

macos owns macOS app targets only: scenes/windows, AppKit/SwiftUI platform behavior, sandboxing/TCC, distribution, persistence choice, user-facing text, and HIG conventions. Do not apply these rules to iOS/iPadOS/watchOS/visionOS targets even when `Info.plist`/entitlements globs match. Swift language rules live in `standards/swift/`; universal rules in `standards/global/`; secret policy in `global/refs/security.md` (this file covers only the Mac mechanics).

**Scope:** these rules apply in full to new targets and modules. In existing code, match established conventions; propose migrations (persistence stack, deployment target, architecture slices) as separate explicit tasks — never as a side effect of a feature change.

## Priority: P0 — Platform Correctness

### Platform Baseline (2026)
- Ship universal 2 (arm64 + x86_64) while the deployment target spans Intel-capable macOS; never add new components that require Rosetta. Going arm64-only is a deliberate deployment-target decision, not a build-setting default. Verify shipped architectures with `lipo -info` — don't trust the build setting alone. Detail → `refs/distribution.md`.
- Build with the current Xcode/SDK — required for Liquid Glass and current-OS behavior. SDK version ≠ deployment target.
- New apps: minimum deployment macOS 15 by default; 14 is the practical floor (below it you lose `@Observable` and modern scene APIs). Never bump an existing app's target as a side effect.

### App Structure & Lifecycle
- SwiftUI lifecycle (`@main struct App: App`); never `@NSApplicationMain`, a hand-written `main.swift`, or manual `NSApplication.main()` for new *app* code (non-app bundles — XPC services, CLI tools, login-item helpers — legitimately differ).
- `@NSApplicationDelegateAdaptor` only for what SwiftUI can't do: `applicationDidFinishLaunching` pre-UI setup, `applicationShouldTerminateAfterLastWindowClosed`, Dock-icon reopen, Apple events beyond simple URL opens, `NSStatusItem` setup. Keep the delegate a thin bridge, not a parallel architecture.
- **Known gap**: `applicationShouldHandleReopen(_:hasVisibleWindows:)` never fires in a pure SwiftUI-lifecycle app, even with the adaptor. If Dock-click-to-reopen must show a window, use `applicationWillBecomeActive(_:)` — but guard on a visible-window check, since it fires on *every* activation (Cmd-Tab, alert dismissal), not just Dock reopen.
- Use `.onOpenURL { }` for custom URL schemes; drop to raw `NSAppleEventManager` only for Apple Event classes beyond a simple GET-URL.
- AppKit is main-thread-only and `@MainActor`-isolated in current SDKs — keep strict concurrency on so the compiler enforces it inside `NSViewRepresentable`/`Coordinator` bridge code.

**AppKit bridging** — default to SwiftUI; drop to AppKit only for a specific missing capability, wrapping just that control — never rewrite a whole screen. Confirmed gaps still needing an escape hatch (re-verify each WWDC, SwiftUI closes them): rich/attributed text editing (`NSTextView`), custom/multi-target status-bar items (`NSStatusItem` + `NSHostingView`), outline/tree views (`NSOutlineView`), PDF display (`PDFView`), full titlebar/traffic-light chrome, and trackpad gesture recognizers. Wrap AppKit with `NSViewRepresentable`/`NSViewControllerRepresentable`; host SwiftUI with `NSHostingController`/`NSHostingView`; keep the boundary thin.

```swift
struct RichTextView: NSViewRepresentable {
    @Binding var text: NSAttributedString
    func makeNSView(context: Context) -> NSTextView {
        let view = NSTextView(); view.delegate = context.coordinator; return view
    }
    func updateNSView(_ view: NSTextView, context: Context) {
        if view.attributedString() != text { view.textStorage?.setAttributedString(text) }
    }
    func makeCoordinator() -> Coordinator { Coordinator(self) }
    final class Coordinator: NSObject, NSTextViewDelegate {
        let parent: RichTextView
        init(_ parent: RichTextView) { self.parent = parent }
        func textDidChange(_ n: Notification) {
            guard let v = n.object as? NSTextView else { return }
            parent.text = v.attributedString()
        }
    }
}
```

### Sandbox & File Access
- Sandbox on by default (mandatory for Mac App Store; Apple-recommended even for Developer ID); request the narrowest entitlements — a missing entitlement means TCC never even prompts.
- Access user files only via user intent (`NSOpenPanel`/`fileImporter`, drag & drop); use the URL the panel returns — a self-derived path to the "same" file carries no sandbox extension.
- Persist access with security-scoped bookmarks; balance every `startAccessingSecurityScopedResource()` with `stop`; re-create stale bookmarks. Detail → `refs/sandbox-and-tcc.md`.
- Secrets go in the Keychain — never `UserDefaults`, plists, or bundled files.

### Permissions (TCC)
- Request lazily, at the moment of use, with clear purpose strings; on denial degrade gracefully and deep-link to System Settings; never re-prompt loop.
- Know the grant paths: Accessibility / Screen Recording — you trigger the prompt but the user completes the grant in System Settings; Automation — the first-Apple-event consent dialog *is* the grant; Full Disk Access / Input Monitoring — no prompt API exists, detect and deep-link only.
- Use a stable dev signing identity — TCC grants key to the signature; ad-hoc signing resets them every build. Detail → `refs/sandbox-and-tcc.md`.

### Distribution
- Outside the App Store: Developer ID + hardened runtime + notarization is effectively mandatory (macOS 15+ removed the easy Gatekeeper bypass).
- Sign inside-out with `--options runtime --timestamp`; strip `get-task-allow` from release builds; staple the ticket (apps in zips: staple the `.app`, re-zip with `ditto`). Detail → `refs/distribution.md`.
- Updates outside MAS: Sparkle 2 with EdDSA-signed appcasts; sandboxed apps need the installer XPC service plus the mach-lookup exception entitlements. Never ship Sparkle in a MAS build.
- Signing assets never live in the repo; CI signs with an App Store Connect API key — never Apple ID credentials.

### User-Facing Text & Formatting
- All user-visible strings via String Catalog / `String(localized:)` with comment context; never build sentences by concatenating fragments; plurals via catalog plural variants, not `count == 1 ? ... : ...`. Detail → `refs/localization.md`.
- User-facing dates/numbers via `FormatStyle`/`.formatted()` (locale-aware); fixed-format wire dates via ISO 8601 or an `en_US_POSIX`-pinned formatter; never `String(format:)` for user-facing numbers.
- Formatters are expensive — cache them; never create one inside a view body or row builder.

### State & Data
- `@Observable` over `ObservableObject` on macOS 14+. Inject shared services with `@Environment(Type.self)` / `.environment(_:)`, not `@EnvironmentObject`. Keep `@Observable` `init()` side-effect-free (a `@State` initializer can re-run across view rebuilds).
- Core Data: contexts are confined — access only inside `perform`/`performAndWait`; never pass `NSManagedObject` across actor boundaries (pass `NSManagedObjectID` or value snapshots).
- Persistence decision: Core Data (+ CloudKit) or GRDB when you need robust migrations, mature sync, or large datasets; SwiftData is acceptable for simpler local-first stores on recent targets — custom migration stages exist but are fragile. Existing SwiftData codebases stay unless migration is the explicit task. Detail → `refs/architecture-and-state.md`.
- `@AppStorage`/`UserDefaults` for small preferences only. Per-window UI state in `@SceneStorage`; scenes don't share `@State`.

### Background Work & Helpers
- Login items, agents, and daemons register via `SMAppService`; users can revoke in System Settings — design for it. Prefer a user-level launch agent over a daemon unless root/pre-login is required; constrain launchd plists with launch constraints.
- XPC for privilege separation and crash isolation; validate the connecting client's code signature (audit token / code-signing requirement), never its PID. Detail → `refs/sandbox-and-tcc.md`.
- Respect App Nap: `NSBackgroundActivityScheduler` for deferrable work, `ProcessInfo.beginActivity` for user-visible long work, tolerance on every timer. Don't poll where change notifications exist (KVO, notifications, FSEvents); notification-less external resources may poll with backoff. Detail → `refs/performance-accessibility.md`.

---

## Priority: P1 — Platform Conventions (HIG)

### Windows & Scenes
- Pick the right scene: `WindowGroup` (multi-instance), `Window` (single-instance), `Settings` (auto-wires ⌘, and the "Settings…" item — don't hand-build one), `MenuBarExtra` (status bar), `DocumentGroup` (document apps — read `refs/windows-and-scenes.md` before using).
- Open/close via `openWindow`/`dismissWindow` environment actions; data-driven windows via `WindowGroup(for:)`. Use macOS 15+ scene modifiers (`defaultLaunchBehavior`, `restorationBehavior`, `windowResizability`) where the floor allows — gate with `#available` on a 14 floor. Rely on automatic window restoration; disable per-scene for About-style windows.
- Menu bar apps: `MenuBarExtra` (`.window` style for popover content); `NSStatusItem` + `NSPanel` only for non-activating panels or custom positioning; retain the status item strongly. Opening Settings from an `.accessory` app needs the activation-policy recipe → `refs/windows-and-scenes.md`.
- Own programmatic windows with an `NSWindowController`; don't toggle `isReleasedWhenClosed` to paper over close crashes.

### Menus & Keyboard
- Full menu bar (App/File/Edit/View/Window/Help); every feature reachable from it. Build with the `Commands` API (`CommandGroup`/`CommandMenu`); never mutate `NSMenu` directly unless bridging legacy AppKit. Feed focused-window context via `@FocusedValue`/`.focusedSceneValue`.
- Primary actions get keyboard shortcuts; respect standard ones (⌘, ⌘W ⌘Q ⌘N). Attach `.keyboardShortcut` to the same action used in-window; don't duplicate. Label the item "Settings…", not "Preferences…". Every custom control needs a full keyboard path.

### Documents
- `DocumentGroup` + `FileDocument` for value-type documents (auto-wires Open/Save/Recents). `ReferenceFileDocument` only for reference-semantic models — load-test large-document save latency (saves have been observed on the main thread). Drop to `NSDocument` for custom undo/autosave/versioning or complex file packages. Detail → `refs/windows-and-scenes.md`.

### SwiftUI Views
- `body` is pure: no side effects, no per-evaluation allocations (formatters are the classic offender).
- `@State` is `private`. `List`/`ForEach` identity must be stable — unstable `Identifiable` ids are the top list correctness and performance bug.
- Avoid `AnyView` in hot hierarchies. Scale path: `List` → `Table` → lazy stacks → `NSTableView`/`NSCollectionView` when thousands of rows need cell reuse. Detail → `refs/performance-accessibility.md`.

### Appearance (Liquid Glass)
- Standard controls adopt Liquid Glass automatically on the current SDK; custom-drawn chrome does not — audit every screen after an SDK bump. AppKit: content goes inside `NSGlassEffectView.contentView`, never behind glass as a sibling.
- Colors from the asset catalog with dark-mode and increased-contrast variants; semantic system colors for standard chrome; SF Symbols for iconography; no hardcoded pixel sizes.
- Drag & drop wherever content moves (`draggable`/`dropDestination` + `Transferable`).

### Accessibility
- Verify UI under Reduce Transparency and Increase Contrast (glass materials especially); honor Reduce Motion for custom animation.
- Custom controls implement the accessibility protocol — role, value, actions — not just a label. Full keyboard navigation. Run Accessibility Inspector audits per screen and wire `performAccessibilityAudit` into CI. Don't assume iOS-style Dynamic Type; back custom sizing with `@ScaledMetric`. Detail → `refs/performance-accessibility.md`.

### Undo, Pasteboard & Intents
- Content-mutating user actions register undo (`NSUndoManager` scoped per document/window, weak targets); ⌘Z/⇧⌘Z must work.
- Copy/paste for any selectable content, via the same `Transferable` types as drag & drop.
- Expose key app actions as App Intents — Shortcuts, Spotlight, and Apple Intelligence surface through them.

---

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

---

## References

Load only what the current task requires:

- [architecture-and-state](refs/architecture-and-state.md) — Observation framework internals, `@State`/`@Bindable`/ownership, `@Environment`/`@Entry` DI, MVVM tradeoffs, when Combine still fits, SwiftData vs Core Data decision; files matching `**/*Model.swift`, `**/*Store.swift`, `**/*ViewModel.swift`, `**/*Service.swift`; keywords: @Observable, @Bindable, ObservableObject, SwiftData, Core Data, @Environment, MVVM
- [windows-and-scenes](refs/windows-and-scenes.md) — scene selection, window management APIs, menu bar apps incl. the Settings-from-accessory recipe, commands and focus/responder bridging, document apps (`FileDocument`/`NSDocument`); keywords: WindowGroup, MenuBarExtra, NSStatusItem, NSPanel, openWindow, Commands, FocusedValue, DocumentGroup, activation policy
- [sandbox-and-tcc](refs/sandbox-and-tcc.md) — App Sandbox, entitlement reference, hardened runtime exceptions, Keychain, TCC grant flows, code-signing basics, XPC security boundaries; files matching `**/*.entitlements`, `**/Info.plist`; keywords: App Sandbox, entitlement, Keychain, TCC, hardened runtime, XPC, security-scoped
- [distribution](refs/distribution.md) — signing certificates, `notarytool`/stapling, MAS submission constraints, Sparkle 2 setup, universal binaries, dmg/pkg packaging, CI signing; files matching `**/*.entitlements`, `**/ExportOptions.plist`, `**/fastlane/**`, `**/*.xcconfig`; keywords: codesign, notarytool, staple, Developer ID, Sparkle, dmg, pkg, universal binary
- [performance-accessibility](refs/performance-accessibility.md) — Instruments templates, main-thread/beachball hygiene, background work (Task vs OperationQueue vs XPC), launch-time optimization, VoiceOver, Dynamic Type/`@ScaledMetric`; keywords: Instruments, Time Profiler, beachball, VoiceOver, accessibilityLabel, Dynamic Type, App Nap
- [localization](refs/localization.md) — String Catalogs, plural rules, `FormatStyle`, pseudo-localization, RTL, testing with `-AppleLanguages`; files matching `**/*.xcstrings`; keywords: String Catalog, localized, plural, locale, FormatStyle, DateFormatter
