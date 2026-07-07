<!-- AUTO-GENERATED from SKILL.md frontmatters — do not edit manually -->
# macos Skills Index

## File Match (auto-check against the file you are editing)

| Skill | File pattern | Keywords |
| ----- | ------------ | -------- |
| **macos** | `**/*.entitlements`, `**/Info.plist` | AppKit, NSWindow, NSStatusItem, MenuBarExtra, menu bar app, WindowGroup, DocumentGroup, Settings scene, SwiftUI, App Sandbox, entitlement, security-scoped, TCC, notarization, codesign, hardened runtime, Gatekeeper, Sparkle, XPC, SMAppService, NSPanel, Developer ID, Liquid Glass, Core Data, SwiftData, String Catalog, VoiceOver, App Intents |
| macos → architecture-and-state ref | `**/*Model.swift`, `**/*Store.swift`, `**/*ViewModel.swift`, `**/*Service.swift` | @Observable, @Bindable, ObservableObject, SwiftData, Core Data, @Environment, MVVM, NSViewRepresentable |
| macos → windows-and-scenes ref | — | WindowGroup, MenuBarExtra, NSStatusItem, NSPanel, openWindow, Commands, FocusedValue, DocumentGroup, activation policy, NSApplicationDelegateAdaptor |
| macos → sandbox-and-tcc ref | `**/*.entitlements`, `**/Info.plist` | App Sandbox, entitlement, Keychain, TCC, hardened runtime, XPC, security-scoped |
| macos → distribution ref | `**/*.entitlements`, `**/ExportOptions.plist`, `**/fastlane/**`, `**/*.xcconfig` | codesign, notarytool, staple, Developer ID, Sparkle, dmg, pkg, universal binary |
| macos → performance-accessibility ref | — | Instruments, Time Profiler, beachball, VoiceOver, accessibilityLabel, Dynamic Type, App Nap, AnyView, ForEach identity |
| macos → localization ref | `**/*.xcstrings` | String Catalog, localized, plural, locale, FormatStyle, DateFormatter |
| macos → hig-conventions ref | — | Liquid Glass, NSGlassEffectView, dark mode, SF Symbols, draggable, Transferable, NSUndoManager, pasteboard, App Intents |

> Load `<SKILLS>/macos/SKILL.md` for macOS app targets — it covers platform correctness (P0) and HIG conventions (P1).
> Scoped to macOS only. Do not apply to iOS/iPadOS/watchOS/visionOS even when `Info.plist`/`.entitlements` globs match.
> Swift language rules live in `<SKILLS>/swift/`; universal rules in `<SKILLS>/global/`.
