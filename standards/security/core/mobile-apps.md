---
description: Mobile app security (iOS/Android) — storage, transport, code integrity, biometrics, permissions
alwaysApply: false
---

# Mobile Application Security

## NEVER
- Make authentication or authorization decisions on the client
- Store user passwords on the device — use revocable access tokens
- Hardcode credentials in the mobile binary
- Override SSL/TLS certificate validation for self-signed certificates
- Store sensitive data in SharedPreferences (Android) or plist files (iOS)
- Use custom cryptography — use platform APIs only
- Send sensitive data via SMS
- Ship production builds with debugging enabled
- Cache or log sensitive data; display it in background snapshots
- Use short PINs (≤4 digits) for sensitive access

## ALWAYS
- Perform authn/z server-side; the client mediates UX only
- Use standard auth protocols (OAuth2, OIDC, JWT) with revocable tokens
- Encrypt credentials in transit; use HTTPS for all network communication
- Validate certificates against trusted CAs; consider pinning for high-value flows
- Store secrets in platform secure storage: iOS Keychain, Android Keystore
- Leverage hardware-backed security: Secure Enclave (iOS), StrongBox/TEE (Android)
- Store private data on internal storage only
- Implement session timeouts and remote logout
- Require re-authentication for sensitive operations
- Use biometrics with secure platform APIs and a passcode fallback
- Mask sensitive UI fields against shoulder surfing

## Network communication
- HTTPS only; strong industry-standard cipher suites; adequate key lengths
- CA-signed certificates; pin for additional security where appropriate
- Encrypt sensitive data at the application layer even when sent over TLS

## Code quality & runtime integrity
- Run static analysis in CI
- Keep dependencies current
- Disable debugging in release builds
- Validate application code integrity at runtime
- Obfuscate the binary
- Detect debugging, hooking, code injection at runtime
- Detect emulators and rooted/jailbroken devices
- Verify app signatures at runtime

## Android specifics
- ProGuard / R8 for code obfuscation
- Avoid SharedPreferences for sensitive data
- Disable backup mode to keep secrets out of cloud backups
- Use Android Keystore with hardware backing (TEE or StrongBox)
- Use Play Integrity API for device + app integrity checks

## iOS specifics
- Require device unlock for Shortcuts that touch sensitive actions
- Set Siri Intent `requiresUserAuthentication = true` for sensitive flows
- Authenticate on deep-link landing endpoints
- Mask sensitive widget content on lock screen
- Store secrets in Keychain; never in plist
- Use Secure Enclave for cryptographic key storage
- Use App Attest API for app integrity; DeviceCheck API for persistent device state

## Privacy & permissions
- Request only the permissions the app actually needs
- Minimize PII collection; implement automatic expiration
- Inform users of security-relevant events (logins from new devices)

## Testing
- Penetration testing including cryptographic assessment
- Automated tests for security features
- Real-time monitoring and incident response plan
- Forced-update mechanism for critical patches

## Checklist
- [ ] Server-side authn/z; no client trust
- [ ] Secrets in Keychain/Keystore; hardware backing used
- [ ] HTTPS everywhere; cert validation strict; pinning where justified
- [ ] Release builds: debug disabled, ProGuard/R8 or equivalent applied
- [ ] Runtime integrity: jailbreak/root/hook/emulator detection
- [ ] Permissions minimized; PII collection minimized
- [ ] Sensitive UI masked; background snapshots suppressed
- [ ] Pen testing + dependency scanning in CI
