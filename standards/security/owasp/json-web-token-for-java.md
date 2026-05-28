---
description: JWT security for Java — algorithm pinning, sidejacking prevention, revocation, storage
alwaysApply: false
---

# JWT Security (Java)

## NEVER
- Accept the `none` algorithm or allow the algorithm to be specified by the token header
- Store the HMAC key as a `String` in JVM memory — use `transient byte[]`
- Store JWT tokens in `localStorage` — use `sessionStorage` or `HttpOnly` cookies
- Hardcode HMAC secrets or RSA/ECDSA private keys in source code
- Issue tokens without an expiry (`exp` claim)

## ALWAYS
- Pin the expected algorithm explicitly in the verifier (e.g., `Algorithm.HMAC256(key)`)
- Set `typ: JWT` in the header; include `iss`, `iat`, `nbf`, and `exp` claims
- Use short-lived tokens — 15 minutes is a reasonable default
- Bind tokens to a user fingerprint cookie to prevent sidejacking
- Store the fingerprint hash (SHA-256) in the token, not the raw value
- Check the revocation denylist on every token verification
- Use a shared DB for the denylist to support multi-instance deployments
- Prefer RSA or ECDSA over HMAC for better security properties
- HMAC secrets must be cryptographically random, minimum 64 characters

## Algorithm Pinning

```java
JWTVerifier verifier = JWT.require(Algorithm.HMAC256(keyHMAC)).build();
DecodedJWT decoded = verifier.verify(token);
```

## Sidejacking Prevention (fingerprint pattern)
- On login: generate 50-byte random fingerprint; set as `__Secure-Fgp` cookie with `SameSite=Strict; HttpOnly; Secure`
- Store SHA-256 hash of fingerprint in the `userFingerprint` JWT claim (not the raw value — prevents XSS extraction)
- On verification: hash the cookie value, compare to claim; reject if mismatch

## Token Revocation
- On logout: compute SHA-256 of the ciphered token; store hex digest in `revoked_token` DB table
- Check denylist before trusting any verified token
- Use a DB (not in-process cache) so all instances share the revocation state

## Client Storage

```javascript
sessionStorage.setItem("token", data.token);           // not localStorage
xhr.setRequestHeader("Authorization", "bearer " + token);
```

## Checklist
- [ ] Algorithm pinned explicitly — `none` and algorithm confusion impossible
- [ ] Token includes `exp`, `iss`, `iat`, `nbf` claims
- [ ] HMAC key stored as `transient byte[]`, never as `String`
- [ ] Fingerprint cookie set `HttpOnly; Secure; SameSite=Strict`; hash stored in token
- [ ] Revocation denylist checked on every verification
- [ ] Tokens stored in `sessionStorage` or `HttpOnly` cookie, not `localStorage`
- [ ] HMAC secret ≥ 64 random chars, or RSA/ECDSA key used instead
