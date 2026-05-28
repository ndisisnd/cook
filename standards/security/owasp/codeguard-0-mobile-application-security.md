---
description: Mobile application security — auth, data storage, network, code integrity, and platform controls for iOS/Android
alwaysApply: false
---

# Mobile Application Security

## NEVER
- Store user passwords on device — use revocable access tokens instead
- Hardcode credentials in the mobile app binary
- Override SSL certificate validation (e.g., for self-signed certs)
- Store sensitive data in SharedPreferences (Android), plist files (iOS), or app caches
- Disable backup mode while sensitive data is present (Android)
- Send sensitive data via SMS
- Log, cache, or capture sensitive data in background snapshots
- Ship production builds with debugging enabled

## ALWAYS
- Perform all authentication and authorization checks server-side only
- Use platform-specific secure storage: iOS Keychain / Secure Enclave, Android Keystore (TEE/StrongBox)
- Encrypt sensitive data using platform APIs; avoid custom encryption schemes
- Use HTTPS for all network communication with trusted-CA-signed certificates
- Use strong, industry-standard cipher suites
- Implement session timeouts and remote logout
- Require re-authentication for sensitive operations
- Validate and sanitize all user input and output
- Keep all third-party libraries updated; use only trusted/validated components
- Request only necessary permissions for app and backend services
- Obfuscate the app binary (Android ProGuard or equivalent)
- Include code to validate application integrity at runtime

## Authentication
- Require password complexity; avoid 4-digit PINs
- Use platform-supported biometric authentication with secure fallback
- Inform users of logins from new devices
- Mask sensitive information in UI fields

## Code Integrity & Anti-Tampering
- Check for debugging, hooking, or code injection at runtime
- Detect emulator or rooted/jailbroken device state
- Verify app signatures at runtime
- Use Google Play Integrity API (Android) or App Attest + DeviceCheck API (iOS)

## iOS-Specific
- Set Siri intent `requiresUserAuthentication = true` for sensitive functionality
- Configure Shortcuts permissions to require device unlock
- Implement authentication checks on all deep link endpoints
- Use conditional logic to mask sensitive widget content on lock screen

## Checklist
- [ ] No passwords or credentials stored on device or hardcoded in binary
- [ ] Sensitive data in platform-secure storage (Keychain/Keystore), not prefs or plist
- [ ] SSL pinning or trusted CA enforced; no validation overrides
- [ ] HTTPS only; strong cipher suites; data encrypted even over SSL
- [ ] Session timeouts, remote logout, and re-auth for sensitive operations implemented
- [ ] Production build: debugging off, binary obfuscated, integrity validation active
- [ ] Runtime anti-tampering: rooted/jailbreak detection, signature verification
