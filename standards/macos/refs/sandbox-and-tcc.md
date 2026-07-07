# macOS Sandbox, Entitlements & TCC

## Implementation Workflow

1. **Enable App Sandbox** — Target → Signing & Capabilities → `+ Capability` → "App Sandbox". Writes `com.apple.security.app-sandbox: true` to the `.entitlements` file. Mandatory for Mac App Store; Apple-recommended even for Developer ID / direct distribution.
2. **Grant only the capabilities you use** — one entitlement per resource the app actually touches. Unused entitlements are flagged by App Review and needlessly widen the attack surface.
3. **Enable Hardened Runtime** — required for notarization; leave every exception checkbox off unless you have a specific, documented need.
4. **Store every secret in Keychain** — tokens, passwords, API keys. Never `UserDefaults`, never a plaintext file.
5. **Add exactly one usage-description string per TCC-gated resource you request**, matching the entitlement/API you actually call — mismatches are rejected by App Review and confuse users at the consent prompt.
6. **Isolate untrusted or privileged work in an XPC service** with an explicit code-signing requirement check on the caller — never trust a PID.

## App Sandbox

App Sandbox is OS-enforced access control: a sandboxed process is denied access to all filesystem locations except a small system allowlist and its own container, plus sandbox extensions granted dynamically (e.g. after the user picks a file in an Open panel).

- **Container**: `~/Library/Containers/<bundle-id>/Data/`. Standard "home directory" APIs are transparently redirected here — the app never sees the real `~`.
- Access user files only via user intent (`NSOpenPanel`/`fileImporter`, drag & drop); use the URL the panel returns — a self-derived path to the "same" file carries no sandbox extension.
- **Persisted access outside the container**: security-scoped bookmarks, backed by `com.apple.security.files.bookmarks.app-scope` (app-lifetime) or `.document-scope` entitlements. Bookmarks survive relaunch; a plain path string does not. Balance every `startAccessingSecurityScopedResource()` with a `stop`; re-create a bookmark when `bookmarkDataIsStale` is true.

### Entitlement reference (`.entitlements` XML plist)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.app-sandbox</key><true/>
    <key>com.apple.security.files.user-selected.read-only</key><true/>
    <key>com.apple.security.network.client</key><true/>
</dict>
</plist>
```

| Key | Gates |
|---|---|
| `com.apple.security.app-sandbox` | Enables App Sandbox itself |
| `com.apple.security.files.user-selected.read-only` / `.read-write` | Files the user picked via an Open/Save panel or drag-and-drop |
| `com.apple.security.files.downloads.read-only` / `.read-write` | Downloads folder access |
| `com.apple.security.files.bookmarks.app-scope` / `.document-scope` | Persisted (security-scoped bookmark) access across relaunch |
| `com.apple.security.network.client` / `.network.server` | Outgoing connections / listening for incoming |
| `com.apple.security.device.camera` | Camera capture |
| `com.apple.security.device.microphone` / `.audio-input` | Microphone / Core Audio input — split by **capability path**: `.microphone` from App Sandbox's Hardware section, `.audio-input` from Hardened Runtime's Resource Access. Sandboxed + hardened apps commonly need **both** |
| `com.apple.security.device.usb` / `.bluetooth` | USB / Bluetooth device access |
| `com.apple.security.personal-information.addressbook` / `.calendars` / `.location` / `.photos-library` | Contacts / Calendars / Location / Photos |
| `com.apple.security.print` | Printing |
| `com.apple.security.automation.apple-events` | Sending Apple Events to other apps — pairs with `NSAppleEventsUsageDescription` |
| `com.apple.security.application-groups` | Shared **files/prefs** container (does **not** share Keychain items) |
| `keychain-access-groups` | Explicit Keychain-item sharing across app/extensions/helper tools |

`com.apple.security.accessibility` is **not** a real public entitlement — the Accessibility API permission is TCC-only (see below), not entitlement-gated.

## Hardened Runtime

A set of `com.apple.security.cs.*` runtime protections plus a default posture that requires no entitlement — you only add entitlements to punch exceptions into it. Works alongside SIP to block code injection, DYLD hijacking, and process-memory tampering.

- **Required for notarization.** Default restrictions: blocks arbitrary code injection, ignores `DYLD_*` env vars, disallows unsigned/self-modifying executable memory, restricts debugger attachment.
- **Exception entitlements and their tradeoffs**:
  - `com.apple.security.cs.allow-jit` — permits JIT-mapped executable pages (script/JS engines); weakens W^X for that region.
  - `com.apple.security.cs.allow-unsigned-executable-memory` — allows unsigned/self-modifying code pages; broadly increases injection surface. Avoid.
  - `com.apple.security.cs.allow-dyld-environment-variables` — honors `DYLD_INSERT_LIBRARIES`; reopens classic dylib injection.
  - `com.apple.security.cs.disable-library-validation` — lets your process load frameworks not signed by your Team ID. Needed for legitimate plugin hosts; also lets any signed code load in. Generally disallowed for Mac App Store builds.
  - `com.apple.security.cs.disable-executable-page-protection` — disables W^X entirely. Strongly discouraged.
  - `com.apple.security.get-task-allow` — marks the build debuggable. **Must never ship in a release/notarized build**; the notary service rejects it automatically, and well-implemented XPC services reject callers carrying it.

## Keychain Services (mandatory for secrets — hard rule)

Keychain is the only Apple-sanctioned place for secrets on macOS: encrypted, access-controlled, hardware-backed where available. `UserDefaults` is an **unencrypted plaintext plist** inside the container with no access control — never use it for a password, token, or API key. Arbitrary files have the same plaintext problem.

- **Core API** (`Security` framework): `SecItemAdd`, `SecItemCopyMatching`, `SecItemUpdate`, `SecItemDelete`, driven by query/attribute dictionaries.
```swift
let query: [String: Any] = [
    kSecClass as String: kSecClassGenericPassword,
    kSecAttrAccount as String: "auth_token",
    kSecValueData as String: tokenData,
    kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
]
SecItemDelete(query as CFDictionary) // clear any existing item first
let status = SecItemAdd(query as CFDictionary, nil)
```
- Community wrappers (e.g. KeychainAccess) are common to avoid `CFDictionary` boilerplate — a convenience layer, not a different security model.
- **`kSecAttrAccessible` recommendation**: `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` for most app secrets — no iCloud sync/backup, no access while locked. Use an `AfterFirstUnlock` variant only when a background/daemon process must read the secret while locked. Never leave it unset or use the deprecated `Always` variants.
- **Sharing across app + extensions/helpers**: add the same `keychain-access-groups` string to every target — distinct from `com.apple.security.application-groups`, which shares files/prefs, not Keychain items.

## TCC / Privacy Permissions

Two distinct grant mechanisms exist — know which one a resource uses.

- Know the grant paths: Accessibility / Screen Recording — you trigger the prompt but the user completes the grant in System Settings; Automation — the first-Apple-event consent dialog *is* the grant; Full Disk Access / Input Monitoring — no prompt API exists, detect and deep-link only.

**"Both" category** — Info.plist usage-description string *and* (when sandboxed) an entitlement *and* a standard per-app TCC consent dialog your code can trigger on first access:

| Resource | Info.plist key | Entitlement |
|---|---|---|
| Camera | `NSCameraUsageDescription` | `com.apple.security.device.camera` |
| Microphone | `NSMicrophoneUsageDescription` | `.device.microphone` / `.audio-input` |
| Contacts | `NSContactsUsageDescription` | `.personal-information.addressbook` |
| Calendars | `NSCalendarsUsageDescription` (+ `NSCalendarsFullAccessUsageDescription`) | `.personal-information.calendars` |
| Location | `NSLocationUsageDescription` | `.personal-information.location` |
| Photos | `NSPhotoLibraryUsageDescription` | `.personal-information.photos-library` |
| Bluetooth | `NSBluetoothAlwaysUsageDescription` | `.device.bluetooth` |
| Automation | `NSAppleEventsUsageDescription` | `.automation.apple-events` |

**"System Settings only" category** — no public entitlement, no Info.plist key, no dialog your code can trigger. The user manually enables the app in System Settings → Privacy & Security; your code can only detect denial and deep-link there via an `x-apple.systempreferences:` URL:

- **Full Disk Access** — internally `kTCCServiceSystemPolicyAllFiles`.
- **Accessibility API** — check with `AXIsProcessTrusted()`/`AXIsProcessTrustedWithOptions(_:)`.
- **Screen Recording** — gates ScreenCaptureKit.
- **Input Monitoring** — internally `kTCCServiceListenEvent`, checked via `IOHIDCheckAccess`.

Use a **stable dev signing identity** — TCC grants are keyed to the code signature/Team ID + bundle ID, so ad-hoc signing resets them every build. `tccutil reset <service>` clears a grant during development.

## Code Signing Basics

- Codesigning proves **identity** (which Team ID built the bundle) and **integrity** (unmodified since signing). Entitlements are embedded in the code-signature blob, not a separate loose file read at runtime.
- **Apple Development** — local run/debug only. **Developer ID Application** — direct/outside-MAS distribution (what Gatekeeper checks). MAS apps sign with **Apple Distribution**. (Full matrix in `refs/distribution.md`.)
- **Re-signing breaks apps**: macOS compares bundle hashes against the signature at launch. Any post-sign modification (ad-hoc re-signing, hand-editing a signed bundle) invalidates it and can silently reset TCC grants.
- **Gatekeeper at launch is distinct from notarization**: it triggers only on files carrying the `com.apple.quarantine` xattr (browser download, AirDrop). Un-quarantined apps (built locally, copied via `cp`) skip the gate regardless of notarization status.

## XPC Service Security Boundaries

Split work into a separate XPC service for **privilege separation** — isolate a component that needs elevated rights, parses untrusted input, or carries different entitlements, so a compromise there doesn't hand over the whole app's privileges.

- **Core API**: `NSXPCListener`/`NSXPCListenerDelegate` (service side), `NSXPCConnection` (client), `NSXPCInterface` (declares the allowed selector surface — treat it like an ACL, expose the minimum).
- **Validate the caller, not the PID.** A PID is reusable/spoofable after the original process exits. Use the connection's audit token to build a `SecTask` and call `SecTaskValidateForRequirement`, or on macOS 13+ use `NSXPCConnection.setCodeSigningRequirement(_:)` (lightweight variant `xpc_connection_set_peer_lightweight_code_requirement` on macOS 14.4+). Pin the requirement to Team ID + bundle ID (+ minimum version), not "any Apple-signed binary."
- **Reject risky callers explicitly**: refuse callers lacking Hardened Runtime or carrying `.cs.disable-library-validation`, `.cs.allow-dyld-environment-variables`, or `get-task-allow` — those make the *client* injectable, defeating the isolation boundary from the other side.
- Client and service should be built and signed under the same Team ID unless there's a specific cross-vendor trust reason.

## Anti-Patterns

- Disabling App Sandbox without a documented, reviewed reason
- Requesting an entitlement for a capability the app doesn't use
- Secrets in `UserDefaults` or any plaintext file
- Shipping `get-task-allow` in any release/notarized build; shipping `.cs.allow-unsigned-executable-memory` / `.cs.disable-library-validation` without a specific documented need
- An Info.plist usage-description string with no matching entitlement/API call, or vice versa
- Assuming Full Disk Access / Accessibility / Screen Recording / Input Monitoring can be granted programmatically
- Trusting an XPC caller's PID instead of its audit token / code-signing requirement
- Re-signing an already-signed bundle (invalidates the signature and TCC grants)
- `kSecAttrAccessibleAlways` (deprecated) or omitting `kSecAttrAccessible`
- Sharing Keychain items via `application-groups` (shares files/prefs, not Keychain) instead of `keychain-access-groups`
