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

Target: iOS/iPadOS 18+ deployment, built with Xcode 27 and the iOS 27 SDK. Default load: this file only.

**Scope.** iOS/iPadOS app targets and their extensions (widgets, notification service, App Intents). Not watchOS/visionOS. `Info.plist`/`.entitlements` globs also match the macOS shelf; decide the platform first:
- iOS when `SDKROOT = iphoneos`, the file sits under `ios/`, or code imports `UIKit`/`ActivityKit`/`WidgetKit`.
- macOS when `SDKROOT = macosx` or code imports `AppKit` → `standards/macos/`. Multiplatform targets: apply each shelf to its own `#if os(...)` branch.

Pairs with: Swift rules → `standards/swift/`; universal → `standards/global/`; secrets → `global/refs/security.md`. Platform-neutral SwiftUI guidance lives on the macOS shelf (skip window/menu-bar parts): state and persistence → `<SKILLS>/macos/refs/architecture-and-state.md`; strings and formatting → `<SKILLS>/macos/refs/localization.md`.

In existing code, match conventions; propose deployment-target bumps, UIKit→SwiftUI migrations, and persistence changes as separate tasks.

## P0 — Platform Correctness

### Baseline (Oct 2026)
- Build with Xcode 27 / iOS 27 SDK. App Store Connect has rejected uploads built with anything older than Xcode 26 / iOS 26 SDK since 2026-04-28. SDK version ≠ deployment target.
- New apps: deployment target iOS 18 (covers 27, 26, 18). iOS 17 is the practical floor: it keeps `@Observable` and SwiftData but loses the `Tab` type, zoom transitions and control widgets. Gate newer APIs (Liquid Glass = iOS 26) with `if #available`.
- Three iOS 27 SDK rules break Xcode 26 builds:
  - UIScene lifecycle is mandatory. A UIKit app with no scene manifest fails to launch (SwiftUI `App` apps comply) → `refs/app-lifecycle-and-navigation.md`.
  - A launch screen is mandatory (`UILaunchScreen` or `UILaunchStoryboardName` in `Info.plist`). Missing → upload rejected with ITMS-90870.
  - `UIDesignRequiresCompatibility` is ignored; Liquid Glass is always on. Re-check screens and re-baseline snapshots.

### Lifecycle & Navigation
- SwiftUI lifecycle (`@main struct …: App`). `@UIApplicationDelegateAdaptor` only for APNs token callbacks, background URLSession events, and SDK setup that demands a delegate.
- React to `scenePhase` for save/pause work; never assume an app-level "terminate" callback runs.
- `NavigationStack` with value-typed paths and `navigationDestination(for:)`; one stack per tab. Never `NavigationView`.
- Deep and universal links route through one parser into the navigation path; never navigate from scattered `onOpenURL` handlers.

### Adaptivity
- Layout from size classes and available space, never `userInterfaceIdiom`, orientation, or `UIScreen.main.bounds`. iPad windows resize freely (`UIRequiresFullScreen` is deprecated). iPhone Duo (iOS 27.1) is the first iPhone with regular width × regular height → `refs/app-lifecycle-and-navigation.md`.

### UI & Accessibility
- Every screen works at the largest accessibility Dynamic Type size, with VoiceOver, and with Reduce Motion. Hit targets ≥ 44×44 pt.
- System components first (sheets with detents, `Button` roles, toolbars, `TabView`). No native snackbar/toast: use one overlay host at the root → `refs/ui-and-accessibility.md`.
- Never block the main actor with I/O or decoding.

### Background & Notifications
- `BGTaskScheduler` tasks may never run. Never put correctness-critical work only in a background task.
- Ask for notification permission in context, after the user sees value, or use provisional authorization → `refs/background-and-notifications.md`.

### Privacy & Accounts
- Every protected resource needs its `Info.plist` usage string; ask at point of use; degrade on denial; never gate features on consent (App Review 5.1.1).
- Ship `PrivacyInfo.xcprivacy` declaring every required-reason API; require one from every third-party SDK.
- Tokens and credentials go in the Keychain, never `UserDefaults` or files.
- Account creation requires in-app account deletion (5.1.1(v)). Third-party social login requires an equivalent privacy-preserving option such as Sign in with Apple (4.8) → `refs/privacy-and-permissions.md`.

### Distribution
- CI signs with an App Store Connect API key, never an Apple ID password. Signing assets never live in the repo → `refs/distribution.md`.

## Anti-Patterns

- Custom `ZStack` + offset sheets where `.sheet` + `.presentationDetents` works
- Custom glass, blur, or opaque backgrounds on system bars and sheets (fights Liquid Glass)
- A toast per screen; a toast as the only carrier of an actionable error
- `Thread.sleep` in UI tests instead of `waitForExistence`
- Manual build-number bumps; `.p12` files committed for CI

## References

- [app-lifecycle-and-navigation](refs/app-lifecycle-and-navigation.md) — scene lifecycle, UIScene mandate, NavigationStack, sheets, size classes, iPad/iPhone Duo, deep links
- [ui-and-accessibility](refs/ui-and-accessibility.md) — Dynamic Type, VoiceOver, haptics, keyboard, Liquid Glass, snackbars, `#Preview`
- [background-and-notifications](refs/background-and-notifications.md) — BGTaskScheduler, APNs, Live Activities, WidgetKit, App Intents
- [privacy-and-permissions](refs/privacy-and-permissions.md) — usage strings, ATT, privacy manifests, Keychain, Sign in with Apple, account deletion
- [distribution](refs/distribution.md) — signing, CI signing, TestFlight, App Review gotchas, versioning
- [testing](refs/testing.md) — iOS deltas over `swift/refs/testing.md`: XCUITest, accessibility audits, snapshots, device matrix
