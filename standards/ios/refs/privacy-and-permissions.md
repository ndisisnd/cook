---
last_reviewed: 2026-10-23
---

# iOS Privacy, Permissions & Accounts

Scope: protected resources, tracking, privacy manifests, credential storage, sign-in, account deletion. Generic secret and auth policy → `<SKILLS>/global/refs/security.md`, `<SKILLS>/global/refs/auth.md`.

## Permission Prompts

- Every protected resource needs its usage string in `Info.plist`, or the app crashes on access. Common keys: `NSCameraUsageDescription`, `NSMicrophoneUsageDescription`, `NSPhotoLibraryUsageDescription`, `NSLocationWhenInUseUsageDescription`, `NSContactsUsageDescription`, `NSFaceIDUsageDescription`, `NSBluetoothAlwaysUsageDescription`, `NSLocalNetworkUsageDescription`, `NSUserTrackingUsageDescription`.
- Usage strings say what the app does with the data, in the user's language. "Needs access" alone gets rejected.
- Ask at the point of use, after the user taps the feature. Never batch prompts at launch.
- Prefer APIs that need no permission:
  - `PhotosPicker` / `PHPickerViewController` — no photo library permission.
  - `PasteButton` — no paste prompt.
  - Contacts picker or limited access (iOS 18+) instead of full contacts.
  - When-in-use location before Always; Always only with a clear feature need.
- On denial: degrade the feature, explain, and link to Settings (`UIApplication.openSettingsURLString`). Re-check status on `scenePhase == .active`.
- Never gate unrelated features on consent (App Review 5.1.1(iv)).

## App Tracking Transparency

- Tracking = linking user or device data with other companies' data for ads or measurement, or sharing it with data brokers. It includes the IDFA and any fingerprinting.
- Call `ATTrackingManager.requestTrackingAuthorization` only while the app is active; earlier calls fail silently.
- If not authorized, do not track by any means, including SDKs. Fingerprinting is forbidden regardless of consent.
- Never reward or block features based on the ATT answer.

## Privacy Manifest (`PrivacyInfo.xcprivacy`)

- Required for the app and every third-party SDK. Apple's list of commonly used SDKs must also ship signed.
- Declare every required-reason API with an approved reason code: `UserDefaults`, file timestamps, system boot time, disk space, active keyboards.
- Declare `NSPrivacyCollectedDataTypes`, `NSPrivacyTracking`, and `NSPrivacyTrackingDomains`. Tracking domains are blocked until the user allows tracking.
- Generate the aggregated privacy report from the archive (Xcode Organizer) and keep the App Store privacy label in sync with it.

## Credential Storage

- Tokens, passwords, and keys go in the Keychain. Never `UserDefaults`, plists, files, or the bundle.
- Accessibility class: `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` by default. Use `AfterFirstUnlockThisDeviceOnly` only when background tasks need the item. Never the deprecated `Always` classes.
- Gate high-value secrets with `SecAccessControl` (`.biometryCurrentSet` or `.userPresence`) and `LAContext`. Biometry unlocks a Keychain item; it is not a boolean check.
- Share credentials between app and extensions with a Keychain access group, not an App Group file.
- Sensitive files: `FileProtectionType.complete`. The default (`completeUntilFirstUserAuthentication`) is fine for non-sensitive data that background tasks read.
- Exclude caches and re-downloadable data from backup (`isExcludedFromBackup`).

## Sign-In

- Passkeys first for new account systems: `ASAuthorizationPlatformPublicKeyCredentialProvider`, the `webcredentials:` associated domain, and AutoFill-assisted requests.
- Password fields: correct `textContentType` (`.username`, `.password`, `.newPassword`) so Password AutoFill and strong-password generation work.
- Guideline 4.8: an app that offers third-party or social login must also offer an equivalent login option that limits data collection to name and email, lets users keep their email private, and does not track without consent. Sign in with Apple satisfies it.
- Sign in with Apple: check `getCredentialState(forUserID:)` on launch and observe revocation; sign the user out when revoked. Validate the identity token on the server.
- OAuth in the app: `ASWebAuthenticationSession` with PKCE. Never an embedded `WKWebView` for third-party sign-in.

## Account Deletion

- Apps that let users create an account must let them delete it in the app (5.1.1(v)). Make it easy to find, usually in Settings → Account.
- Deletion removes the account and its personal data, not just a deactivation. If legal retention applies, say what stays and why.
- Sign in with Apple accounts: call Apple's token revocation endpoint during deletion.
- Confirm the destructive step; then sign out and clear Keychain items, caches, and the App Group container.
