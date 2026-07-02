# macOS Distribution

## Implementation Workflow

1. **Pick the right certificate pair** for the distribution channel before anything else (table below) — signing with the wrong cert type is the most common first failure.
2. **Enable Hardened Runtime** (see `refs/sandbox-and-tcc.md`) — required before notarization will succeed.
3. **Sign inside-out**: every nested executable, framework, and helper tool must be individually signed before the outer bundle. Signing the outer bundle first and forgetting nested binaries is the top notarization-rejection cause.
4. **Notarize with `notarytool`** (Developer ID builds only — MAS builds are not notarized; App Review is the trust gate there).
5. **Staple the ticket** to whatever the user actually downloads (`.dmg`/`.pkg`), and optionally the inner `.app`.
6. **Package**: `.dmg` for a simple drag-to-Applications app, `.pkg` when you need install scripts or system-level install locations.

## Code Signing Certificates

| Certificate | Use |
|---|---|
| **Apple Development** | Local run/debug on your own registered devices. Not distribution-relevant. |
| **Developer ID Application** | Signs `.app` bundles for direct/outside-MAS distribution. Required (with notarization) for Gatekeeper trust. |
| **Developer ID Installer** | Signs `.pkg` installers for outside-MAS distribution. Use `productsign`, not `codesign`. |
| **Apple Distribution** | Signs `.app` bundles for Mac App Store submission (older docs: "3rd Party Mac Developer Application"). |
| **Mac Installer Distribution** | Signs `.pkg` installers submitted *to* the Mac App Store (older name: "3rd Party Mac Developer Installer"). |

Rule of thumb: **Developer ID pair** (Application + Installer) = outside MAS. **Apple Distribution + Mac Installer Distribution** = inside MAS.

## Notarization with `notarytool`

`altool` is dead for notarization — Apple's notary service stopped accepting `altool` (and Xcode 13-or-earlier) submissions on **November 1, 2023**. Already-notarized software keeps running; only new submissions are blocked. `xcrun notarytool`, shipped since Xcode 13, is the sole supported path. Full migration guidance: Apple TN3147.

```bash
# One-time credential setup (stored in Keychain), either form:
xcrun notarytool store-credentials "AC_PROFILE" \
  --apple-id "dev@example.com" --team-id TEAMID1234 --password "app-specific-password"
# or with an App Store Connect API key (preferred for CI):
xcrun notarytool store-credentials "AC_PROFILE" \
  --key AuthKey.p8 --key-id KEYID1234 --issuer ISSUERUUID

# Submit and block until Apple returns a verdict
xcrun notarytool submit MyApp.dmg --keychain-profile "AC_PROFILE" --wait

# Inspect past submissions / pull the diagnostic log for a rejection
xcrun notarytool history --keychain-profile "AC_PROFILE"
xcrun notarytool log <submission-id> --keychain-profile "AC_PROFILE"
```

**Common rejection causes**: missing/disabled Hardened Runtime; unsigned nested binaries, frameworks, or dylibs; invalid or missing entitlements (e.g. undeclared `com.apple.security.cs.allow-jit`); Info.plist/signature format mismatches.

## Stapling

```bash
xcrun stapler staple MyApp.dmg
```
Attaches the notarization ticket directly to the `.app`, `.dmg`, or `.pkg` so Gatekeeper can verify it **offline**, without a live call to Apple's servers. Run only after `notarytool submit --wait` reports "Accepted." Staple the outer container users actually download; optionally also staple the inner `.app`. `stapler` **cannot** staple a `.zip` — unzip, staple the contained `.app`, then re-zip with `ditto -c -k --keepParent`.

## Mac App Store Submission Constraints

- **App Sandbox is mandatory** for every MAS submission. Non-MAS distribution has no such requirement, though Apple recommends it.
- `com.apple.security.cs.disable-library-validation` is generally disallowed for MAS — it undermines the sandbox trust model. Combining sandbox with hardened-runtime exception entitlements is a common rejection trigger.
- **Sparkle-style self-updating is disallowed in MAS builds** (Review Guideline 2.4.5(vii)) — MAS apps use StoreKit/the App Store's own update mechanism. The standard pattern is two build configurations: one with Sparkle for direct distribution, one without for the Store.
- **MAS apps do not need notarization** — App Review is the trust/security gate. The Catalina-era notarization requirement carves out the Mac App Store.
- Upload MAS builds via **Xcode Organizer**, **Transporter**, or **Xcode Cloud** — not `notarytool`.
- Standard App Review constraints also apply: receipt validation for IAP, no private API usage, no sandbox-bypassing dynamic code loading, background-execution limits.

## Sparkle Framework (Direct-Distribution Auto-Updates)

Sparkle 2.x is the current, actively maintained major version.

- **Mechanism**: the app polls an **appcast** (RSS/XML feed) declared via the `SUFeedURL` Info.plist key; the feed lists versions, download URLs, and signatures over HTTPS. Sparkle verifies the signature before installing.
- **Signing**: Sparkle 2 uses **EdDSA (Ed25519)** exclusively for new setups, replacing Sparkle 1's DSA. The public key is stored in Info.plist as `SUPublicEDKey`; updates are signed with the bundled `sign_update` tool.
- **Sandboxing**: Sparkle 2 ships two XPC services so it can operate inside App Sandbox — `Installer.xpc` (required) and `Downloader.xpc` (optional; only if the app lacks `com.apple.security.network.client`). Enabled via `SUEnableInstallerLauncherService`/`SUEnableDownloaderService` Info.plist booleans, and requires a `com.apple.security.temporary-exception.mach-lookup.global-name` entitlement naming the bundle-ID-derived Mach service names.
- **Never in a Mac App Store build** — even with its sandboxed XPC installer, Sparkle's self-directed binary replacement conflicts with MAS's StoreKit-mediated update policy.

## Universal Binaries / Apple Silicon vs Intel

- Build with **Architectures = `$(ARCHS_STANDARD)`** (arm64 + x86_64) and **Build Active Architecture Only = No** for Release/Archive (Debug typically stays "Yes"). Xcode compiles per-architecture and merges with `lipo`.
- Verify actual shipped architectures with `lipo -info MyApp` / `file MyApp` — don't trust the build setting; some Xcode 16.x point releases had regressions ignoring `ARCHS`/`ONLY_ACTIVE_ARCH`.
- **Apple Silicon transition** (per Apple's stated roadmap through 2025–2026): macOS 26 "Tahoe" is the last macOS that installs on Intel Macs; the following major release is Apple-Silicon-only but still ships Rosetta 2; the release after that sharply curtails Rosetta. Treat "Apple Silicon only" as reasonable once your minimum deployment target and user base are confirmed Apple Silicon; ship universal otherwise. Don't assume a security-update tail for Intel beyond what Apple has stated.

## .dmg vs .pkg Packaging

- **`.dmg`** — the common single-`.app`, drag-to-`/Applications` flow. No install scripts, no elevated privileges. Build with `hdiutil` (built-in) or `create-dmg`. The `.app` inside must already be signed (Developer ID Application) and notarized; the outer `.dmg` is then separately notarized and stapled.
- **`.pkg`** — required for pre/post-install scripts, multiple components, system-level install locations (`/Library`, `LaunchDaemons`), or an Installer.app-guided flow. Build with `pkgbuild` + `productbuild`. Sign with `productsign` using a Developer ID Installer (outside MAS) or Mac Installer Distribution (MAS) certificate — never an Application certificate or `codesign` for a package.
- Signing summary: dmg's `.app` → Developer ID Application + Hardened Runtime + notarize + staple. pkg → Developer ID Installer via `productsign`, then (outside MAS) notarize the pkg and staple.

## Anti-Patterns

- Signing a `.pkg` with an Application certificate instead of an Installer certificate (`productsign`, not `codesign`)
- Submitting notarization via `altool` (dead since 2023-11-01)
- Forgetting to sign a nested framework/helper tool before the outer bundle
- Shipping without Hardened Runtime (notarization rejects it)
- Notarizing a Mac App Store build; shipping Sparkle in a MAS build
- Stapling a `.zip` directly (`stapler` can't) — staple the contained `.app`/`.dmg`/`.pkg`
- Building "Apple Silicon only" without checking the minimum deployment target and user base
- Trusting `ARCHS`/`Build Active Architecture Only` blindly — verify with `lipo -info`
- Assuming `.cs.disable-library-validation` is acceptable in a MAS submission
