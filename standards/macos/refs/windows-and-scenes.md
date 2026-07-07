# macOS Windows, Scenes, Commands & Documents

## Core Rules

### Windows & Scenes
- Pick the right scene: `WindowGroup` (multi-instance), `Window` (single-instance), `Settings` (auto-wires ⌘, and the "Settings…" item — don't hand-build one), `MenuBarExtra` (status bar), `DocumentGroup` (document apps — read the Document-Based Apps section below before using).
- Open/close via `openWindow`/`dismissWindow` environment actions; data-driven windows via `WindowGroup(for:)`. Use macOS 15+ scene modifiers (`defaultLaunchBehavior`, `restorationBehavior`, `windowResizability`) where the floor allows — gate with `#available` on a 14 floor. Rely on automatic window restoration; disable per-scene for About-style windows.
- Menu bar apps: `MenuBarExtra` (`.window` style for popover content); `NSStatusItem` + `NSPanel` only for non-activating panels or custom positioning; retain the status item strongly. Opening Settings from an `.accessory` app needs the activation-policy recipe → Menu Bar Apps section below.
- Own programmatic windows with an `NSWindowController`; don't toggle `isReleasedWhenClosed` to paper over close crashes.

### Menus & Keyboard
- Full menu bar (App/File/Edit/View/Window/Help); every feature reachable from it. Build with the `Commands` API (`CommandGroup`/`CommandMenu`); never mutate `NSMenu` directly unless bridging legacy AppKit. Feed focused-window context via `@FocusedValue`/`.focusedSceneValue`.
- Primary actions get keyboard shortcuts; respect standard ones (⌘, ⌘W ⌘Q ⌘N). Attach `.keyboardShortcut` to the same action used in-window; don't duplicate. Label the item "Settings…", not "Preferences…". Every custom control needs a full keyboard path.

### Documents
- `DocumentGroup` + `FileDocument` for value-type documents (auto-wires Open/Save/Recents). `ReferenceFileDocument` only for reference-semantic models — load-test large-document save latency (saves have been observed on the main thread). Drop to `NSDocument` for custom undo/autosave/versioning or complex file packages. Detail → Document-Based Apps section below.

## App Lifecycle & Delegate Adaptor

- `@NSApplicationDelegateAdaptor` only for what SwiftUI can't do: `applicationDidFinishLaunching` pre-UI setup, `applicationShouldTerminateAfterLastWindowClosed`, Dock-icon reopen, Apple events beyond simple URL opens, `NSStatusItem` setup. Keep the delegate a thin bridge, not a parallel architecture.
- Use `.onOpenURL { }` for custom URL schemes; drop to raw `NSAppleEventManager` only for Apple Event classes beyond a simple GET-URL.
- **Known gap**: `applicationShouldHandleReopen(_:hasVisibleWindows:)` never fires in a pure SwiftUI-lifecycle app, even with the adaptor. If Dock-click-to-reopen must show a window, use `applicationWillBecomeActive(_:)` — but guard on a visible-window check, since it fires on *every* activation (Cmd-Tab, alert dismissal), not just Dock reopen.

## Scene Selection

| Scene | Use for |
|---|---|
| `WindowGroup` | Multi-instance windows (user can open several); the default document-like window |
| `Window` | A true singleton scene — one inspector, one utility window that should never duplicate |
| `Settings` | Auto-wires `⌘,` and the "Settings…" app-menu item. Never hand-build a Preferences window |
| `MenuBarExtra` | A status-bar item |
| `DocumentGroup` | Document apps — auto-wires Open/Save/Recents (see Documents below) |

- Open/close programmatically with the `openWindow` / `dismissWindow` environment actions. Data-driven windows: `WindowGroup(for: SomeID.self)` + `openWindow(value:)`.
- `.defaultSize(_:)` / `.defaultWindowPlacement(_:)` set initial geometry. `.windowResizability(.contentSize)` constrains resizing to the content's intrinsic size range.
- Window state restoration is automatic across relaunch — opt out per-scene with `.restorationBehavior(...)` only with a reason (e.g. an About window).
- Use macOS 15+ scene modifiers (`defaultLaunchBehavior`, `restorationBehavior`) where the deployment floor allows; gate with `#available` on a 14 floor.
- Own a programmatic `NSWindow` with an `NSWindowController`; don't toggle `isReleasedWhenClosed` to paper over a close crash — fix the ownership instead. Retain any `NSStatusItem` strongly or it silently vanishes.
- Note: `pushWindow` is visionOS-only — it has no macOS equivalent.

## Menu Bar Apps

- `MenuBarExtra` with the `.window` style hosts arbitrary popover content. Use `NSStatusItem` + `NSPanel`/`NSHostingView` directly only for non-activating panels, custom positioning, richly-formatted labels, or distinguishing a right-click from a left-click (which `MenuBarExtra` can't).
- **Opening Settings from an `.accessory` (menu-bar-only) app** needs an activation-policy recipe, because an accessory app has no normal app activation:
  1. Before the Settings scene can show, flip the activation policy to `.regular` (`NSApp.setActivationPolicy(.regular)`) and `NSApp.activate(ignoringOtherApps:)`.
  2. Open Settings (send the `showSettingsWindow:`/`showPreferencesWindow:` action, or use `@Environment(\.openSettings)` on macOS 14+).
  3. When the Settings window closes, flip the policy back to `.accessory` so the app returns to menu-bar-only.
  - Decouple the trigger from the window lifecycle via `NotificationCenter` rather than reaching across view layers; hide any stray blank window before Settings appears.

## Commands & Keyboard

- Build app menus with `.commands { }` on the `Scene`, using `CommandGroup(replacing:/before:/after:, addition:)` and `CommandMenu("Title") { }`. Never mutate `NSMenu` directly unless bridging a pre-existing legacy AppKit menu.

```swift
WindowGroup { ContentView() }
    .commands {
        CommandGroup(replacing: .newItem) { Button("New Document") { /* ... */ } }
        CommandMenu("Format") { Button("Bold") { }.keyboardShortcut("b") }
    }
```

- Attach `.keyboardShortcut(_:modifiers:)` to the same `Button`/action used in-window — don't duplicate a shortcut between a menu command and an in-view control.
- Respect standard shortcuts: `⌘,` (Settings), `⌘W`, `⌘Q`, `⌘N`, `⌘Z`/`⇧⌘Z` (undo/redo). Every feature must be reachable from the full menu bar (App/File/Edit/View/Window/Help); every custom control needs a full keyboard path — never ship a mouse-only control.

## Focus & Responder Bridging

- `@FocusState` / `@FocusState<T>` for in-view focus (text fields, custom controls).
- Wire menu-item enablement/state to the focused document or selection with:
  - `@FocusedValue` / `.focusedValue(_:)` — view-scoped, read-only.
  - `@FocusedBinding` / `.focusedSceneValue(_:)` — scene-scoped, mutable.
- This is the SwiftUI equivalent of the AppKit responder chain and the standard pattern for document-aware commands (Delete, Undo, Save) — a menu `Button` reads `@FocusedValue` to know which document it acts on. Drop to `NSEvent`/first-responder APIs only for gaps SwiftUI focus can't express.

## Document-Based Apps

- `DocumentGroup` + `FileDocument` for straightforward **value-type** documents — auto-wires Open, Save, and Recents. Declare your `UTType`s and register them as exported/imported content types in the target.
- Use `ReferenceFileDocument` only for reference-semantic/shared-mutable document models — and **load-test large-document save latency** (`ReferenceFileDocument` saves have been observed on the main thread; treat large saves as a beachball risk).
- Drop to `NSDocument`/`NSDocumentController` (the full AppKit document architecture) for per-document undo-manager customization beyond SwiftUI's defaults, custom autosave/versioning policy, multi-representation documents, or complex file-package handling. SwiftUI's document story is intentionally lightweight and currently underpowered for non-trivial document requirements.
- Register content-mutating actions with an `NSUndoManager` scoped per document/window (weak targets); use `NSFileCoordinator` when a file may be edited by another process. Autosave-in-place and dirty-state tracking are expected of a well-behaved document app.

## Anti-Patterns

- Using `WindowGroup` where only one instance should ever exist (use `Window`)
- Hand-building a Preferences window/menu item instead of the `Settings` scene
- Mutating `NSMenu` directly where `.commands { }` expresses the same menu
- Unretained `NSStatusItem` or `NSWindowController` (they silently disappear)
- Toggling `isReleasedWhenClosed` to mask a close crash instead of fixing ownership
- Duplicating a keyboard shortcut between a menu command and an in-view control
- `ReferenceFileDocument` for a value-type document, or shipping large-document saves without latency-testing them
- Mouse-only custom controls with no keyboard path
