---
last_reviewed: 2026-10-23
---

# iOS Signing & Distribution

Scope: signing, provisioning, CI builds, TestFlight, App Store Connect, App Review. Generic CI rules → `<SKILLS>/global/refs/cicd.md`; Swift build tooling → `<SKILLS>/swift/refs/tooling.md`.

## Upload Requirements (Oct 2026)

- SDK: uploads must be built with Xcode 26+ / iOS 26 SDK (since 2026-04-28). Expect the 27 SDK to become mandatory in spring 2027; Apple has not announced the date.
- Deployment target: iOS 13 or later (since 2026-09-09). Reported to rise to iOS 15 in April 2027.
- iOS 27 SDK builds need a launch screen key (`UILaunchScreen`, `UILaunchScreens`, `UILaunchStoryboardName`, or `UILaunchStoryboards`) or the upload fails with ITMS-90870 (TN3208). Local validation does not catch it.
- Set `ITSAppUsesNonExemptEncryption` in `Info.plist` so every build skips the export-compliance question. `NO` is correct only when the app uses no encryption beyond Apple's OS-provided HTTPS/TLS.

## Signing

- Local development: automatic signing.
- CI: an App Store Connect API key (`.p8`, Issuer ID, Key ID) stored as CI secrets. Use it with `xcodebuild -allowProvisioningUpdates -authenticationKeyPath … -authenticationKeyID … -authenticationKeyIssuerID …`, Xcode Cloud, or fastlane `match`.
- Never commit `.p12`, `.mobileprovision`, `.p8`, or Apple ID passwords. Never use an Apple ID with 2FA prompts in CI.
- Use a temporary keychain on CI runners and delete it after the job.
- Capabilities and entitlements change in one place (the target's Signing & Capabilities); review `.entitlements` diffs like code. Release builds never carry `get-task-allow`.
- App extensions (widgets, notification service) have their own bundle IDs and profiles under the app's ID prefix.

## Build & Upload

- Archive with `xcodebuild archive`, export with `xcodebuild -exportArchive` and an `ExportOptions.plist` (`method: app-store-connect`, `destination: upload`), or fastlane `upload_to_testflight`.
- Version (`CFBundleShortVersionString`) is the user-facing semver; build (`CFBundleVersion`) is a monotonically increasing number set by CI. Never bump build numbers by hand.
- Keep build settings in `.xcconfig` files, not in the project file, so diffs stay reviewable.
- Upload dSYMs to the crash reporter for every release build.

## TestFlight

- Internal testers (up to 100 team members) get builds after processing, with no review.
- External testers (up to 10,000) need a beta app review for the first build of each version.
- Builds expire after 90 days. Fill in "What to Test" for every external build.
- Use separate bundle IDs or a single app with a staging configuration — never ship a debug-only backend URL in an App Store build.

## App Review Gotchas

- 2.1 Completeness: provide a working demo account and notes for any gated feature. Remove placeholder content and dead buttons.
- 2.3 Metadata: screenshots show the real app on current devices; no prices or other platforms' names in metadata.
- 3.1 Payments: digital goods and features use In-App Purchase unless a storefront-specific exception applies (rules differ for the US and the EU). Check the current guideline text before adding external purchase links.
- 4.2 Minimum functionality: a wrapped website is rejected.
- 4.8 and 5.1.1: sign-in options and account deletion → `refs/privacy-and-permissions.md`.
- Keep the age-rating questionnaire, privacy nutrition label, and (for EU distribution) DSA trader status current. Stale answers block submission.

## Release

- Use phased release for production updates; pause it on a crash spike.
- Check that minimum OS and required device capabilities (`UIRequiredDeviceCapabilities`) did not change by accident between releases — raising them strands existing users.
