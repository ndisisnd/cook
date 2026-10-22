<!-- Hand-maintained routing index. Keep in sync with SKILL.md frontmatter. -->
# ios Skills Index

## File Match (auto-check against the file you are editing)

| Skill | File pattern | Keywords |
| ----- | ------------ | -------- |
| **ios** | `**/Info.plist`, `**/*.entitlements`, `**/PrivacyInfo.xcprivacy` | iPadOS, iPhone, iPad, UIKit, UIApplication, UIScene, SceneDelegate, scenePhase, presentationDetents, size class, universal link, BGTaskScheduler, APNs, Live Activity, WidgetKit, App Tracking Transparency, Sign in with Apple, TestFlight, provisioning profile, XCUITest |
| ios → app-lifecycle-and-navigation ref | `**/*App.swift`, `**/SceneDelegate.swift`, `**/AppDelegate.swift` | UIScene, UISceneDelegate, UIApplicationDelegateAdaptor, scenePhase, NavigationStack, presentationDetents, size class, horizontalSizeClass, iPhone Duo, UIRequiresFullScreen, universal link, apple-app-site-association |
| ios → ui-and-accessibility ref | — | Dynamic Type, VoiceOver, Liquid Glass, glassEffect, UIDesignRequiresCompatibility, presentationDetents, sensoryFeedback, PhotosPicker, pasteboard, ReservedRegion |
| ios → background-and-notifications ref | `**/*Widget*.swift`, `**/NotificationService.swift` | BGTaskScheduler, BGAppRefreshTask, BGProcessingTask, BGContinuedProcessingTask, APNs, UNUserNotificationCenter, Notification Service Extension, Live Activity, ActivityKit, WidgetKit, App Intents, AppIntent |
| ios → privacy-and-permissions ref | `**/Info.plist`, `**/PrivacyInfo.xcprivacy`, `**/*.entitlements` | privacy manifest, App Tracking Transparency, ATTrackingManager, IDFA, Keychain, Sign in with Apple, ASWebAuthenticationSession |
| ios → distribution ref | `**/ExportOptions.plist`, `**/fastlane/**`, `**/*.xcconfig` | TestFlight, App Store Connect, provisioning profile, mobileprovision, ITMS-90870, UILaunchScreen |
| ios → testing ref | `**/*UITests/**`, `**/*.xctestplan` | XCUITest, XCUIApplication, performAccessibilityAudit |

> Load `<SKILLS>/ios/SKILL.md` for iOS/iPadOS app targets — it covers platform correctness (P0) and anti-patterns.
> Scoped to iOS/iPadOS only. `Info.plist`/`.entitlements` globs also match macOS; decide the platform from `SDKROOT` or the `ios/` folder first.
> Swift language rules live in `<SKILLS>/swift/`; platform-neutral SwiftUI state and localization in `<SKILLS>/macos/refs/architecture-and-state.md` and `<SKILLS>/macos/refs/localization.md`; universal rules in `<SKILLS>/global/`.
