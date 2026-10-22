---
last_reviewed: 2026-10-23
---

# iOS Testing

Scope: iOS deltas only. Unit tests, Swift Testing, fakes, and XCTest migration → `<SKILLS>/swift/refs/testing.md`.

## Split

- Unit and integration tests: Swift Testing (`@Test`, `#expect`). Most coverage lives here.
- UI tests: XCUITest (XCTest). Swift Testing does not drive UI. Keep UI tests to critical flows: sign-in, purchase, onboarding, the main task.
- Run both through an Xcode test plan (`.xctestplan`) with named configurations (locale, Dynamic Type, region).

## XCUITest

- Query by `accessibilityIdentifier`, never by visible text or element index. Identifiers are stable; labels get localized.
- Launch per test with `launchArguments` / `launchEnvironment` for test mode: in-memory store, stubbed network, fixed clock, animations off.
- Wait with `waitForExistence(timeout:)` or expectations. Never `sleep`.
- Page objects: one type per screen exposing actions (`signIn(email:password:)`), so tests read as flows.
- System alerts (permissions): pre-grant with `xcrun simctl privacy <device> grant <service> <bundle-id>`, or handle them with `addUIInterruptionMonitor`.
- Each test owns its data and resets it on launch. No order dependence between tests.

## Accessibility Audits

- Call `try app.performAccessibilityAudit()` on each key screen in UI tests. It catches missing labels, small hit targets, contrast, and clipped Dynamic Type.
- Suppress a finding only with a filter closure that names the issue type and element, plus a comment explaining why.

## Snapshot Tests

- Pin device, OS, scale, appearance, and Dynamic Type size per snapshot. Record on one CI image.
- Cover light/dark, the largest accessibility size, and a right-to-left locale for core screens.
- The first iOS 27 SDK build changes every screen (Liquid Glass is forced on). Re-record all snapshots in one dedicated change before reviewing feature diffs.

## Device Matrix

Run UI and snapshot suites on at least:

- Smallest supported iPhone and largest iPhone.
- iPad in a resized window (not only full screen) — Split View and Stage Manager widths.
- iPhone Duo inner display (Xcode 27.1 simulator, Device Hub) when the app supports iOS 27.1.
- Oldest supported iOS version on one simulator, so `#available` fallbacks execute.

## Performance & Launch

- Measure cold launch with `XCTApplicationLaunchMetric` and fail on regression. Use `XCTOSSignpostMetric` for custom intervals.
- Watch hangs and launch time in Xcode Organizer and MetricKit after release.
