---
description: Applied cryptography and TLS — algorithm choices, key management, data-at-rest, TLS config, HSTS, pinning
alwaysApply: false
---

# Applied Cryptography & TLS

> Companion to `crypto-algorithms` (algorithm policy) and `digital-certificates` (cert validation). This file covers applied configuration: TLS, HSTS, key lifecycle, data-at-rest, pinning.

## NEVER
- Use ECB mode; use CBC/CTR without an encrypt-then-MAC construction
- Use RSA <2048 or curves below 256-bit (Curve25519/secp256r1 minimum)
- Use MD5/SHA-1 for integrity
- Use a non-cryptographic RNG for keys, nonces, salts, or tokens
- Generate keys from passwords or other predictable inputs
- Hardcode keys, or store them in plain env vars or config files
- Allow TLS 1.0/1.1 or SSL; disable TLS_FALLBACK_SCSV
- Browser HPKP (deprecated); rely on user-bypassable cert validation in any client

## ALWAYS
- Symmetric: AES-GCM or ChaCha20-Poly1305 (AEAD)
- Asymmetric: RSA ≥2048 with OAEP for encryption, or modern ECC (Curve25519/Ed25519)
- Hashes: SHA-256+ for integrity
- RNG: platform CSPRNG (`SecureRandom`, `crypto.randomBytes`, `secrets` module)
- Generate keys inside validated modules (HSM/KMS)
- Separate keys by purpose (encryption, signing, wrapping)
- Wrap data-encryption keys (DEKs) with a key-encryption key (KEK); store separately
- Rotate keys on compromise, cryptoperiod, or policy
- Audit all key access and operations

## Data at rest
- Encrypt sensitive data; minimize stored secrets; tokenize where possible
- Authenticated encryption; manage nonces/IVs to never repeat under the same key; unique per-item salts
- Encrypt backups; restrict access; test restores; manage retention

## TLS configuration
- Protocols: TLS 1.3 preferred; TLS 1.2 only for legacy compat; TLS 1.0/1.1 and SSL disabled; enable TLS_FALLBACK_SCSV
- Ciphers: AEAD suites only; disable NULL/EXPORT/anon; disable compression
- Key-exchange groups: prefer x25519/secp256r1; configure secure FFDHE groups if needed
- Certificates: 2048-bit+ keys, SHA-256+ signatures, correct CN/SAN; manage lifecycle and revocation (OCSP stapling)
- Application: HTTPS site-wide; redirect HTTP → HTTPS; prevent mixed content; cookies `Secure`

## HSTS rollout
- Send `Strict-Transport-Security` only over HTTPS, phased:
  - Test: `max-age=86400; includeSubDomains`
  - Prod: `max-age=31536000; includeSubDomains` (≥1 year)
  - Optional preload only once mature — understand permanence

## Pinning
- Avoid browser HPKP — deprecated
- Consider SPKI pinning only for controlled clients (mobile) where you own both ends
- Always configure backup pins; plan a secure update channel; never allow user bypass
- Test rotation and failure handling before deploying

## Checklist
- [ ] AEAD everywhere; vetted libraries only; no custom crypto
- [ ] Keys generated and stored in KMS/HSM; purpose-scoped; rotation documented
- [ ] TLS 1.3 (or 1.2 legacy) with strong ciphers; compression off; OCSP stapling on
- [ ] HSTS deployed per phased plan; mixed content eliminated
- [ ] Pinning used only where justified, with backup pins and update path
- [ ] Automated scans (SSL Labs / testssl.sh) clean for protocols, ciphers, HSTS
