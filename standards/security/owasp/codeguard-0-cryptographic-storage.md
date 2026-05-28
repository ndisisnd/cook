---
description: Protect data at rest with approved algorithms, authenticated modes, and formal key management
alwaysApply: false
---

# Cryptographic Storage

## NEVER
- Implement custom cryptographic algorithms
- Use insecure random generators (`Math.random()`, `java.util.Random`, `random` module, etc.) for security purposes
- Hard-code encryption keys in source code or version control
- Use deprecated/broken algorithms: MD5, SHA-1, DES, RC4, ECB mode
- Store keys with the encrypted data without proper separation
- Generate keys from passwords, phrases, or predictable patterns

## ALWAYS
- Use authenticated encryption (GCM or CCM preferred; CTR/CBC only with Encrypt-then-MAC)
- Use AES with ≥128-bit keys (256-bit preferred) for symmetric encryption
- Use Curve25519 or RSA ≥2048 bits for asymmetric; enable OAEP/PKCS#1 random padding for RSA
- Generate unique random keys per operation using a CSPRNG
- Use vetted cryptographic libraries only
- Minimize sensitive data storage — tokenize when storage is unavoidable
- Have key rotation procedures ready and tested before compromise occurs

## Approved Random Generators

| Platform | PROHIBITED | REQUIRED |
|----------|------------|----------|
| PHP | `rand()`, `mt_rand()` | `random_bytes()`, `random_int()` |
| Java | `java.util.Random` | `java.security.SecureRandom` |
| .NET | `System.Random` | `System.Security.Cryptography.RandomNumberGenerator` |
| Python | `random` module | `secrets` module |
| JavaScript | `Math.random()` | `window.crypto.getRandomValues()` |
| Go | `math/rand` | `crypto/rand` |
| Node.js | `Math.random()` | `crypto.randomBytes()`, `crypto.randomInt()` |

Note: UUID v1 is not random. UUID v4 is only safe if the implementation uses a CSPRNG.

## Key Management

**Storage** — use in order of preference:
1. Physical/Virtual HSM
2. Cloud key vault (AWS KMS, Azure Key Vault, GCP KMS)
3. External secrets manager (HashiCorp Vault, Conjur)
4. Framework secure API (ProtectedData, Keychain)

**Key Encryption:** wrap Data Encryption Keys (DEK) with a Key Encryption Key (KEK); store KEK separately; KEK must be ≥ as strong as DEK.

**Rotate keys when:** compromise suspected · cryptoperiod expires (NIST SP 800-57) · usage limits reached (2^35 bytes for 64-bit, 2^68 for 128-bit) · algorithm security degrades.

## Architecture Layers
- Application-level encryption: required for database-compromise protection
- Database-level (TDE): additional at-rest protection
- Filesystem-level (BitLocker, LUKS): physical theft protection
- Hardware-level (encrypted RAID/SSDs): hardware protection

## Checklist
- [ ] Only approved algorithms and modes in use (AES-GCM/CCM; no ECB, DES, RC4, MD5, SHA-1)
- [ ] CSPRNG used for all key and nonce generation
- [ ] No keys hard-coded; keys stored in HSM/vault/secrets manager
- [ ] DEK wrapped by KEK; stored separately from encrypted data
- [ ] Key rotation process documented and tested
- [ ] Defense-in-depth: access controls and monitoring on encrypted data, not crypto alone
