---
last_reviewed: 2026-10-23
---

# Cryptography

Cross-cutting concern: algorithms and modes, keys, randomness, encryption at rest and
in transit, TLS, and certificates. Password hashing lives in [auth.md](auth.md); CORS,
secrets scanning, and the OWASP tables live in [security.md](security.md). Maps to
OWASP A04:2025.

Each rule carries a detection signal for review mode. All P0 unless tagged.

## Algorithms & Modes

- **Symmetric encryption is AEAD: AES-256-GCM or ChaCha20-Poly1305.** Never ECB, RC4,
  DES/3DES, Blowfish, or CBC/CTR without an encrypt-then-MAC.
  Signal: `aes-*-ecb`, `createCipher(`, `aes-256-cbc` with no HMAC.
- **Never repeat a nonce/IV under one key.** Random 96-bit GCM nonces are safe only up
  to about 2^32 messages per key; past that, use a counter or rotate the key.
  Signal: a constant `iv`/`nonce`, or `iv = Buffer.alloc(16)`.
- **Hash with SHA-256+ or SHA-3; MAC with HMAC-SHA-256.** Never MD5/SHA-1 for
  integrity or signing. Derive keys from other keys with HKDF; derive from passwords
  only with a password KDF (see [auth.md](auth.md)).
  Signal: `md5(`, `createHash('sha1')`, a password used directly as a key.
- **Signatures: Ed25519 or ECDSA P-256. RSA is >=2048 bits (prefer 3072) with OAEP for
  encryption and PSS for signing; never PKCS#1 v1.5 for encryption (v1.5 signatures,
  such as RS256, only for interop).** Key exchange is
  ephemeral ECDHE (X25519 or secp256r1); never static RSA or anonymous DH.
  Signal: `RSA_PKCS1_PADDING`, `modulusLength: 1024`.
- **Never write custom crypto; use a vetted library.** In C use OpenSSL `EVP_*`, never
  `AES_*`, `RSA_*`, `SHA1_*`.
- **P1 (design):** prefer hybrid post-quantum key exchange (`X25519MLKEM768`, RFC 10024) where
  supported. Keep algorithm choices in config, not code.

## Randomness

- **Keys, nonces, salts, tokens, and reset codes come from a CSPRNG.**
  JS `crypto.randomBytes` / `randomInt` / `crypto.getRandomValues`; Python `secrets`;
  Java `SecureRandom`; Go `crypto/rand`; .NET `RandomNumberGenerator`.
  Signal: `Math.random()`, `random.random()`, `math/rand`, `java.util.Random` making a secret.

## Keys & Key Management

- **Never hardcode keys or keep them in source, plain env vars, or committed config.**
  Store them in a KMS/HSM or secrets manager; use platform secure storage on devices.
  Signal: a hex/base64 literal passed to `createCipheriv` or `createHmac`.
- **Envelope encryption: encrypt data with a data key (DEK), wrap the DEK with a key
  encryption key (KEK) held in KMS/HSM, and store the wrapped DEK apart from the data.**
- **One key, one purpose.** Never reuse a key for both encryption and signing, or
  across environments.
- **Have a tested rotation path before you need it.** Rotate on compromise or at the
  cryptoperiod; store a key ID with each ciphertext so old and new keys coexist.
  Signal: ciphertext with no key version.
- **Audit every key access;** never export keys from the KMS/HSM unauthenticated.

## Encryption at Rest

- **Encrypt sensitive fields at the application layer.** Disk or database TDE protects
  only against stolen media, not a compromised database account.
- **Encrypt backups and test restores.** Tokenize sensitive data where possible.

## TLS & Transport

- **TLS 1.3 by default; TLS 1.2 only for legacy clients. Never SSL, TLS 1.0, or 1.1.**
  AEAD suites only; no NULL, EXPORT, or anonymous suites; TLS compression off.
  Signal: `minVersion: 'TLSv1'`, `SSLv23_method`, `ssl_protocols TLSv1`.
- **Enforce HTTPS end to end: redirect HTTP with 301, send HSTS, and keep every
  resource on HTTPS.** HSTS header and rollout: [security.md](security.md).
  Signal: a hardcoded `http://` URL, a cookie without `Secure`.
- **Database and service connections require TLS 1.2+ with client-side certificate
  verification.** Signal: `sslmode=disable`, `ssl: false`.
- **Pinning: SPKI pinning only in clients you control (mobile), always with a backup
  pin and an update path. Never browser HPKP (deprecated).**
- **Never share one wildcard certificate across systems of different trust levels.**
  For mTLS between services, see [auth.md](auth.md).

## Certificates

- **Never disable certificate verification outside local tests.**
  Signal: `verify=False`, `InsecureSkipVerify`, `rejectUnauthorized: false`,
  `NODE_TLS_REJECT_UNAUTHORIZED=0`.
- **Validate expiry, the full chain to a trusted root, revocation (OCSP stapling or
  CRL), and that hostname/SAN matches the target.** Reject expired or not-yet-valid
  certs and MD5/SHA-1 signatures.
- **Keys are RSA >=2048 (prefer 3072) or ECDSA P-256+. Never P-192/P-224.** Self-signed
  certs are for dev, test, or internal use with explicit trust only.
- **Load certificates from files, a cert store, or a secret manager so they rotate
  without a redeploy.**
  Signal: a `-----BEGIN` PEM blob in source.

## Anti-Patterns

ECB / unauthenticated CBC · constant IV · MD5/SHA-1 integrity · RSA under 2048 or
PKCS#1 v1.5 · `Math.random()` secrets · hardcoded keys · DEK beside its ciphertext ·
one key, many purposes · no key ID or rotation · TLS 1.0/1.1 · no HSTS · disabled
cert verification · SHA-1 or expired certs · certs in source · custom crypto.
