---
description: Java security essentials — SQLi, JPA, XSS, logging, cryptography, key management
alwaysApply: false
---

# Java Security

## NEVER
- Concatenate user input into SQL or JPQL query strings
- Log user-controlled input via string concatenation — use parameterised logging
- Hardcode cryptographic keys, secrets, or passwords in source code
- Write custom cryptographic implementations
- Use weak or deprecated algorithms (MD5, SHA-1, DES, ECB mode)

## ALWAYS
- Use `PreparedStatement` or named JPA parameters for all database queries
- Validate input with an allowlist regex before use
- Encode output with `Encode.forHtml()` or equivalent before rendering
- Use AES-GCM with a 128-bit tag and a cryptographically random 12-byte nonce
- Generate nonces with `SecureRandom.getInstanceStrong()`
- Use a trusted library (Google Tink or equivalent) for all cryptographic operations
- Implement key rotation and proper key lifecycle management
- Keep all dependencies updated with security patches

## SQL / JPA

```java
// PreparedStatement
String query = "select * from color where friendly_name = ?";
PreparedStatement ps = con.prepareStatement(query);
ps.setString(1, userInput);

// JPA named parameter
Query q = em.createQuery("select c from Color c where c.friendlyName = :name");
q.setParameter("name", userInput);
```

## XSS Prevention

```java
// Allowlist validation
if (!Pattern.matches("[a-zA-Z0-9\\s\\-]{1,50}", userInput)) return false;
// Output encoding
String safe = Encode.forHtml(policy.sanitize(outputToUser));
```

## Cryptography

```java
// AES-GCM encryption
Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
byte[] nonce = new byte[12];
SecureRandom.getInstanceStrong().nextBytes(nonce);
cipher.init(Cipher.ENCRYPT_MODE, secretKey, new GCMParameterSpec(128, nonce));
```

## Logging

```java
logger.warn("Login failed for user {}.", username); // safe — parameterised
// NOT: logger.warn("Login failed for user " + username); // log injection risk
```

## Checklist
- [ ] All DB queries use `PreparedStatement` or named JPA parameters
- [ ] User input validated with allowlist regex before processing
- [ ] HTML output encoded with `Encode.forHtml()` or equivalent
- [ ] Logging uses parameterised calls, never string concatenation
- [ ] Cryptography uses AES-GCM with random nonce via `SecureRandom`
- [ ] No hardcoded keys or secrets in source
- [ ] Trusted crypto library (Tink or equivalent) used — no custom implementations
