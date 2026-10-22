---
name: ios
description: iOS/iPadOS app development standards — SwiftUI app and scene lifecycle, navigation and sheets, iPad and foldable adaptivity, UI components, accessibility, background work, push, Live Activities and widgets, privacy and permissions, account sign-in, signing and App Store distribution, and UI testing. Scoped to iOS/iPadOS only — not macOS/watchOS/visionOS.
metadata:
  triggers:
    files:
      - '**/Info.plist'
      - '**/*.entitlements'
      - '**/PrivacyInfo.xcprivacy'
    keywords:
      - iOS
      - iPadOS
      - iPhone
      - iPad
      - UIKit
      - UIApplication
      - UIScene
      - SceneDelegate
      - scenePhase
      - presentationDetents
      - size class
      - universal link
      - BGTaskScheduler
      - APNs
      - Live Activity
      - WidgetKit
      - App Tracking Transparency
      - Sign in with Apple
      - TestFlight
      - provisioning profile
      - XCUITest
  targets: "iOS/iPadOS 18+ deployment · built with Xcode 27 / iOS 27 SDK (App Store minimum: Xcode 26 / iOS 26 SDK) · Swift 6.2+"
  last_reviewed: 2026-10-23
---

# iOS Standards

Target: iOS/iPadOS 18+ deployment, built with Xcode 27 and the iOS 27 SDK.

Default load: this file only; pull refs only when needed.

**Scope.** Applies to iOS/iPadOS app targets and their extensions (widgets, notification service, App Intents). Not watchOS/visionOS. `Info.plist`/`.entitlements` globs also match the macOS shelf; decide the platform first:
- iOS when `SDKROOT = iphoneos`, the file sits under an `ios/` folder, or code imports `UIKit`/`ActivityKit`/`WidgetKit`.
- macOS when `SDKROOT = macosx` or code imports `AppKit` → `standards/macos/` instead. Multiplatform targets: apply each shelf to its own `#if os(...)` branch.

Pairs with: Swift language rules → `standards/swift/`; universal rules → `standards/global/`; secret policy → `global/refs/security.md`. Platform-neutral SwiftUI guidance lives on the macOS shelf — apply it and skip the window/menu-bar parts: state and persistence → `<SKILLS>/macos/refs/architecture-and-state.md`; strings and formatting → `<SKILLS>/macos/refs/localization.md`.

In existing code, match established conventions; propose deployment-target bumps, UIKit→SwiftUI migrations, and persistence changes as separate tasks, never as a side effect.

## P0 — Platform Correctness

### Baseline (Oct 2026)
- Build with Xcode 27 / iOS 27 SDK. App Store Connect has rejected uploads built with anything older than Xcode 26 / iOS 26 SDK since 2026-04-28. SDK version ≠ deployment target.
- New apps: deployment target iOS 18 (covers 27, 26, 18). iOS 17 is the practical floor: it keeps `@Observable` and SwiftData but loses the `Tab` type, zoom transitions and control widgets. Gate newer APIs (Liquid Glass = iOS 26) with `if #available`.
- Three iOS 27 SDK rules break builds that worked on Xcode 26:
  - UIScene lifecycle is mandatory. A UIKit app with no scene manifest fails to launch. SwiftUI `App` apps already comply. Detail → `refs/app-lifecycle-and-navigation.md`.
  - A launch screen is mandatory (`UILaunchScreen` or `UILaunchStoryboardName` in `Info.plist`). Missing → upload rejected with ITMS-90870.
  - `UIDesignRequiresCompatibility` is ignored; Liquid Glass is always on. Re-check every screen and re-baseline snapshots.

### Lifecycle & Navigation
- SwiftUI lifecycle (`@main struct …: App`). `@UIApplicationDelegateAdaptor` only for APNs token callbacks, background URLSession events, and SDK setup that demands a delegate.
- React to `scenePhase` for save/pause work; never assume an app-level "terminate" callback runs.
- `NavigationStack` with value-typed paths and `navigationDestination(for:)`; one stack per tab. Never `NavigationView`.
- Deep links and universal links route through one parser into the navigation path; never navigate from scattered `onOpenURL` handlers.

### Adaptivity
- Layout from size classes and available space, never `userInterfaceIdiom`, orientation, or `UIScreen.main.bounds`. iPad windows resize freely (`UIRequiresFullScreen` is deprecated). iPhone Duo (iOS 27.1) puts regular width × regular height on an iPhone for the first time. Detail → `refs/app-lifecycle-and-navigation.md`.

### UI & Accessibility
- Every screen works at the largest accessibility Dynamic Type size, with VoiceOver, and with Reduce Motion. Hit targets ≥ 44×44 pt.
- System components first (sheets with detents, `Button` with roles, toolbars, `TabView`). There is no native snackbar or toast; use one overlay host at the root. Pattern → `refs/ui-and-accessibility.md`.
- Never block the main actor with I/O or decoding.

### Background & Notifications
- Background execution is opportunistic: `BGTaskScheduler` tasks may never run. Never put correctness-critical work only in a background task.
- Ask for notification permission in context, after the user sees value, or use provisional authorization. Detail → `refs/background-and-notifications.md`.

### Privacy & Accounts
- Every protected resource needs its `Info.plist` usage string; ask at point of use; degrade on denial; never gate features on consent (App Review 5.1.1).
- Ship `PrivacyInfo.xcprivacy` declaring every required-reason API, and require one from every third-party SDK.
- Tokens and credentials go in the Keychain, never `UserDefaults` or files.
- Account creation requires in-app account deletion (5.1.1(v)). Third-party social login requires an equivalent privacy-preserving option such as Sign in with Apple (4.8). Detail → `refs/privacy-and-permissions.md`.

### Distribution
- CI signs with an App Store Connect API key, never an Apple ID password. Signing assets never live in the repo. Detail → `refs/distribution.md`.

## Anti-Patterns

- UIKit `AppDelegate`-only lifecycle (no scene manifest) or no launch screen, built with the iOS 27 SDK
- `NavigationView`; `NavigationLink(isActive:)`; navigation state spread across `@State` booleans
- Layout branches on `userInterfaceIdiom`, orientation, or `UIScreen.main`; fixed frame heights that clip Dynamic Type
- Custom sheets built from `ZStack` + offset where `.sheet` + `.presentationDetents` works
- A toast per screen; toasts as the only carrier of an error that needs action
- Custom glass, blur, or opaque backgrounds layered on system bars and sheets (fights Liquid Glass)
- Permission prompts at first launch; re-prompt loops; features locked behind ATT or notification consent
- Secrets in `UserDefaults`, plists, or the bundle
- Long work in `App.init` or `application(_:didFinishLaunchingWithOptions:)`
- `Thread.sleep` / fixed delays in UI tests instead of `waitForExistence`
- Apple ID credentials or `.p12` files committed for CI; manual build-number bumps

## References

- [app-lifecycle-and-navigation](refs/app-lifecycle-and-navigation.md) — App/scene lifecycle, UIScene mandate, scenePhase, NavigationStack paths, sheets, size classes, iPad/iPhone Duo adaptivity, state restoration, deep and universal links
- [ui-and-accessibility](refs/ui-and-accessibility.md) — Dynamic Type, VoiceOver, Reduce Motion, haptics, safe areas and keyboard, Liquid Glass, buttons, bottom sheets, snackbars, `#Preview`
- [background-and-notifications](refs/background-and-notifications.md) — BGTaskScheduler, background URLSession, APNs, UNUserNotificationCenter, Live Activities, WidgetKit, App Intents
- [privacy-and-permissions](refs/privacy-and-permissions.md) — usage strings, prompt timing, ATT, privacy manifests, Keychain, data protection, Sign in with Apple, passkeys, account deletion
- [distribution](refs/distribution.md) — signing and provisioning, CI signing, TestFlight, App Store Connect upload, App Review gotchas, versioning
- [testing](refs/testing.md) — iOS deltas over `swift/refs/testing.md`: XCUITest, launch arguments, accessibility audits, snapshot tests, device matrix
