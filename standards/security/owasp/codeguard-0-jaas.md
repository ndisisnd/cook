---
description: JAAS authentication lifecycle — LoginModule implementation, credential handling, logout
alwaysApply: false
---

# JAAS (Java Authentication and Authorization Service)

## NEVER
- Store passwords or credentials as `String` in JVM memory — use `char[]` and clear after use
- Skip the `abort()` cleanup — always reset username and password fields on auth failure
- Leave principals or credentials attached to the subject after `logout()`
- Share sensitive state between `LoginModule`s via `sharedState` without sanitising on abort

## ALWAYS
- Save all four `initialize()` arguments: `subject`, `callbackHandler`, `sharedState`, `options`
- Clear credential arrays in `abort()` before returning
- Remove all principals and public/private credentials from the subject in `logout()`
- Check `subject.isReadOnly()` before attempting cleanup in `logout()`
- Use `CallbackHandler` to gather credentials — never read them directly in `LoginModule`

## LoginModule Lifecycle

| Method | Responsibility |
| ------ | -------------- |
| `initialize()` | Store subject, callbackHandler, sharedState, options |
| `login()` | Capture credentials via callbacks; authenticate; set `succeeded` flag |
| `commit()` | On success: add principals and credentials to subject |
| `abort()` | On failure: reset all credential and state fields |
| `logout()` | Remove all principals and credentials from subject |

## Key Implementation Rules

- `commit()`: add group principals and public credentials only after `userAuthenticated == true`
- `abort()`: reset username, password, and `succeeded` before returning
- `logout()`: use typed `getPrincipals(Class)` and `getPublicCredentials(Class)` for targeted removal
- Config file: options use `key=value` pairs; each `LoginModule` entry ends with `;`; stanza ends with `}`
- `required` flag in config means `LoginContext.login()` must succeed for authentication to proceed

## Checklist
- [ ] All five `LoginModule` methods implemented
- [ ] Credentials stored as `char[]`, cleared in `abort()`
- [ ] `commit()` adds principals/credentials only on successful auth
- [ ] `abort()` resets all state before returning
- [ ] `logout()` removes all principals and credentials from subject
- [ ] `CallbackHandler` is decoupled from `LoginModule` source file
