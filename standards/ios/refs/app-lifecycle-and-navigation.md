---
last_reviewed: 2026-10-23
---

# iOS App Lifecycle & Navigation

Scope: app and scene lifecycle, navigation, presentation, adaptivity, restoration, links. SwiftUI state ownership and Observation → `<SKILLS>/macos/refs/architecture-and-state.md` (platform-neutral parts).

## Lifecycle

- One `@main struct …: App` with `WindowGroup`. No `main.swift`, no `@UIApplicationMain`.
- `@UIApplicationDelegateAdaptor` is a thin bridge for: `didRegisterForRemoteNotificationsWithDeviceToken`, `handleEventsForBackgroundURLSession`, and third-party SDK setup that demands a delegate. Business logic lives elsewhere.
- Keep `App.init` and `didFinishLaunching` cheap: register background tasks, set notification delegate, then return. Defer everything else until after first frame.
- Read `@Environment(\.scenePhase)`:
  - `.background` → persist unsaved state, stop timers, end non-essential work.
  - `.inactive` → transient (app switcher, Control Center); do not tear down here.
  - `.active` → refresh stale data; re-check permissions the user may have changed in Settings.
- There is no reliable termination callback. Save on `.background`, not on "quit".
- On iPad, several scenes of the same app can run at once. Scene-level `@State`/`@SceneStorage` is per window; app-wide state lives in an object injected through `.environment`.

### UIScene mandate (iOS 27 SDK)

- Apps built with the iOS 27 SDK must adopt the scene-based lifecycle or they fail to launch. The check depends on the SDK, not the device OS.
- SwiftUI `App` apps already comply. UIKit apps need `UIApplicationSceneManifest` in `Info.plist` and a `UIWindowSceneDelegate`.
- Adoption means a manifest with at least one scene configuration, or `application(_:configurationForConnecting:options:)` on the app delegate. A manifest holding only `UIApplicationSupportsMultipleScenes` does not count.
- Multiple-window support is not required: `UIApplicationSupportsMultipleScenes = NO` is fine. `UIApplicationDelegate` is not deprecated; it keeps process-level events. Move UI logic to the scene delegate (TN3187).
- Cross-platform shells (Flutter 3.47+, Expo SDK 57, Capacitor 8.5) ship their own scene migration. Upgrade the framework rather than hand-patching the generated host app.
- When migrating, move URL handling, universal links, quick actions, and `UIScreen.main` lookups to scene APIs (`scene(_:openURLContexts:)`, `scene(_:continue:)`, `windowScene.screen`).

## Navigation

- `NavigationStack(path:)` driven by a value-typed path owned by a router object or the root view. `navigationDestination(for:)` once per destination type, attached inside the stack, never inside a lazy container.
- Route values are small `Hashable` enums or IDs, never view models or views.
- Each tab owns its own stack and path. Re-selecting the active tab pops to root.
- `NavigationSplitView` for list-detail content that should become two or three columns on iPad; it collapses to a stack in compact width automatically.
- Never `NavigationView` or `NavigationLink(isActive:)` / `NavigationLink(tag:selection:)` (deprecated).
- Tabs: `TabView` with the `Tab` type (iOS 18+). Use `Tab(role: .search)` for search. `.tabViewStyle(.sidebarAdaptable)` turns tabs into a sidebar on iPad.

```swift
enum Route: Hashable, Codable {
    case recipe(Recipe.ID), settings
    init?(url: URL) { /* validate host/path, map to a case */ return nil }
}

@Observable final class Router {
    var path: [Route] = []
    func open(_ url: URL) { if let r = Route(url: url) { path = [r] } }
}

struct RootView: View {
    @State private var router = Router()
    var body: some View {
        NavigationStack(path: $router.path) {
            HomeView()
                .navigationDestination(for: Route.self) { route in
                    switch route {
                    case .recipe(let id): RecipeView(id: id)
                    case .settings: SettingsView()
                    }
                }
        }
        .environment(router)
        .onOpenURL { router.open($0) }
    }
}
```

## Presentation

- Item-driven: `.sheet(item:)` / `.fullScreenCover(item:)` with an `Identifiable` value, not a Bool plus a separate optional.
- One presentation source per view. Do not present a second sheet while one is visible; dismiss, then present from `onDismiss` or a state change.
- Dismiss from inside with `@Environment(\.dismiss)`. Do not pass `isPresented` bindings down several levels.
- `.interactiveDismissDisabled(hasUnsavedChanges)` plus a confirmation, never a silent loss of input.
- `fullScreenCover` only for immersive or blocking flows (onboarding, camera, sign-in that gates the app). Everything else is a sheet.
- Bottom sheet detents, background interaction and styling → `refs/ui-and-accessibility.md`.
- `.navigationTransition(.zoom(sourceID:in:))` with `.matchedTransitionSource(id:in:)` for card-to-detail transitions (iOS 18+).

## Adaptivity (iPad, resizable windows, foldables)

- Read `@Environment(\.horizontalSizeClass)` / `verticalSizeClass`, or measure with `ViewThatFits`, `containerRelativeFrame`, or `onGeometryChange`. Never branch layout on `UIDevice.current.userInterfaceIdiom`, interface orientation, or `UIScreen.main.bounds`.
- iPadOS 26+ windows resize freely, and the iOS 27 SDK extends continuous resizing to iPhone. `UIRequiresFullScreen` is deprecated; remove it. Every layout must survive any width from compact iPhone to full iPad.
- iPhone Duo (iOS 27.1): the outer display behaves like a standard iPhone (compact/regular portrait, compact/compact landscape). The inner display reports regular/regular — the first iPhone to do so. Build with the iOS 27.1 SDK to use the full inner display. Do not build per-pose layouts.
- Custom chrome near system UI on iPhone Duo: reserve space with `ReservedRegion` (SwiftUI) / `UIViewReservedRegion` (UIKit) instead of hard-coded insets.
- Prefer standard containers (`TabView`, `NavigationSplitView`, toolbars). They adapt to size changes automatically; custom bars do not.
- Size-class changes rebuild views. Keep state above the branch so it survives the switch.

## State Restoration

- `@SceneStorage` for small per-scene UI state: selected tab, scroll anchor ID, draft text. Not for model data or secrets.
- Persist the navigation path as `[Route]` with `Codable` routes, or `NavigationPath.codable` (`NavigationPath.CodableRepresentation`). Decode failures fall back to root, never crash.
- Restore after data loads. A restored `.recipe(id)` whose record was deleted shows a not-found state, not a crash.

## Deep Links & Universal Links

- Prefer universal links (`https`) over custom URL schemes; schemes are not owned and can be hijacked.
- Universal links need the Associated Domains entitlement (`applinks:example.com`) and an `apple-app-site-association` file at `https://example.com/.well-known/` served as JSON over HTTPS without redirects.
- In SwiftUI both universal links and scheme URLs arrive in `.onOpenURL`. Handle it once at the root and parse into `Route` values.
- Treat every incoming URL as untrusted input. Validate host, path, and parameters. Never execute actions (purchase, delete, sign-out) from a link without user confirmation.
- Links that need auth: store the pending route, complete sign-in, then navigate.
- Quick actions, Spotlight, and widget taps reuse the same parser.
