---
last_reviewed: 2026-10-23
---

# iOS Background Work & Notifications

Scope: background execution, transfers, push, local notifications, Live Activities, widgets, App Intents.

## Background Tasks

- The system decides when (and whether) background tasks run. Design every task to be skippable and idempotent.
- Pick the right kind:
  - `BGAppRefreshTask` — short refresh (about 30 s). SwiftUI: `.backgroundTask(.appRefresh("id"))`.
  - `BGProcessingTask` — minutes of deferrable work; set `requiresExternalPower` / `requiresNetworkConnectivity` when true.
  - `BGContinuedProcessingTask` (iOS 26+) — user-started work (export, upload) that continues after the user leaves, with system progress UI. Report progress or the system ends it.
  - Background `URLSession` — uploads and downloads that must finish while the app is suspended.
- List every identifier in `BGTaskSchedulerPermittedIdentifiers`. Register handlers before `didFinishLaunching` returns.
- Set an `expirationHandler` that cancels work and saves partial progress. Always call `setTaskCompleted(success:)`.
- Reschedule the next refresh inside the handler.
- Never use `beginBackgroundTask` as a general background mechanism. It buys seconds to finish work started in the foreground.

## Background URLSession

- `URLSessionConfiguration.background(withIdentifier:)`; file-based upload/download tasks only.
- Store the completion handler from `application(_:handleEventsForBackgroundURLSession:completionHandler:)` and call it after `urlSessionDidFinishEvents`.
- Recreate the session with the same identifier at launch to receive events.

## Notification Permission

- Ask in context: after the user enables a feature that needs it, never on first launch.
- Prefer `.provisional` authorization for low-stakes updates: delivers quietly with no prompt.
- On denial, show an in-app explanation with a link to `UIApplication.openNotificationSettingsURLString`. Never re-prompt in a loop.
- Set `UNUserNotificationCenter.current().delegate` before launch finishes, or taps on notifications that launched the app are lost.

## APNs (Remote Push)

- Server auth: token-based (`.p8` key + key ID + team ID). Not certificates.
- Send the device token to the server on every launch. Tokens change on reinstall, restore, and OS updates.
- Set `apns-push-type` on every request (`alert`, `background`, `liveactivity`, …). Use `apns-priority: 5` for background pushes.
- Silent pushes (`content-available: 1`) are throttled and never guaranteed. Do not use them for correctness-critical sync.
- Payload limit 4 KB. Send IDs, not content; fetch content in the app or in a Notification Service Extension.
- Notification Service Extension (`mutable-content: 1`) to decrypt or attach media; it has a short time budget, so always deliver the best-attempt content.
- `interruptionLevel`: `.timeSensitive` needs the capability and user setting; `.critical` needs an Apple entitlement. Do not abuse either.
- Group with `threadIdentifier`; add actions with `UNNotificationCategory`. Deep links from notifications use the shared URL parser.

## Live Activities (ActivityKit)

- `NSSupportsLiveActivities = YES` in the app's `Info.plist`. Check `ActivityAuthorizationInfo().areActivitiesEnabled` before starting.
- Content state stays small (4 KB limit). Send the full state with every update.
- Update from the server with `apns-push-type: liveactivity`. Push-to-start (iOS 17.2+) starts activities remotely.
- An activity lives at most 8 hours, then stays on the Lock Screen up to 4 more hours after it ends. Always end activities explicitly with a final state.
- Frequent updates (sports, rides) need `NSSupportsLiveActivitiesFrequentUpdates` and still face a system budget.

## Widgets (WidgetKit)

- Widgets render snapshots from a timeline; they do not run code continuously. Provide `placeholder`, `getSnapshot`, and a timeline with a sensible reload policy.
- The reload budget is limited (roughly dozens per day). Call `WidgetCenter.shared.reloadTimelines(ofKind:)` after data changes in the app instead of short timelines.
- Share data through an App Group container (`UserDefaults(suiteName:)` or a shared SwiftData/SQLite store). Never network-fetch inside the view.
- Interactive widgets (iOS 17+) use `Button`/`Toggle` with an `AppIntent`. Control widgets (iOS 18+) use `ControlWidget`.
- Support every family you declare, including Lock Screen accessory families and tinted/clear rendering modes.

## App Intents

- Expose key actions as `AppIntent`s and publish them with an `AppShortcutsProvider` (Siri, Spotlight, Shortcuts, Action button).
- Model content as `AppEntity` with an `EntityQuery`; keep the intent logic in shared code used by the app, widgets, and controls.
- Intents that change data return a result dialog and respect authentication (`authenticationPolicy`).
