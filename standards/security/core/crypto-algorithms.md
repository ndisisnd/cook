---
description: Cryptographic algorithms and post-quantum readiness — banned, deprecated, and required choices
alwaysApply: true
---

# Cryptographic Algorithms

## NEVER
- **Hash:** MD2, MD4, MD5, SHA-0, SHA-1 (collision-broken; SHA-1 legacy only, never for auth/signing)
- **Symmetric:** RC2, RC4, Blowfish, DES, 3DES, AES-ECB; AES-CBC without an explicit MAC
- **Signature:** RSA with PKCS#1 v1.5 padding; JWT `alg: "none"`
- **Key exchange:** static RSA, anonymous Diffie-Hellman, DHE with weak/common primes
- **Classical:** Vigenère, ROT, XOR-with-key (not crypto)
- Custom-rolled crypto, hardcoded keys, experimental/draft OIDs (e.g. legacy `X25519Kyber`)
- C/OpenSSL low-level APIs: `AES_encrypt`, `RSA_new`/`RSA_free`/`RSA_get0_n`, `SHA1_Init`, `HMAC(…, SHA1, …)`

## ALWAYS
- **Symmetric:** AES-256-GCM or ChaCha20-Poly1305 (AEAD); AES-256-GCM for PQC resistance (Grover halves effective key strength)
- **Hash:** SHA-256+ or SHA-3 family
- **KEM:** ECDHE X25519 or secp256r1; use **hybrid PQC** where supported (RFC 9242/9370):
  - Preferred: `X25519MLKEM768`
  - Alt: `SecP256r1MLKEM768`
  - High-assurance: `SecP384r1MLKEM1024`
  - Pure PQC baseline: ML-KEM-768 (avoid ML-KEM-512 unless risk-accepted)
- **Signatures:** ECDSA P-256. ML-DSA only with HSM/TPM-backed keys — never software-only.
- **Protocols:** (D)TLS 1.3 only; IKEv2 only (ESP with AES-256-GCM + ECDHE PFS); SSH PQC/hybrid KEX (e.g. `sntrup761x25519`)
- **C/OpenSSL:** EVP_* high-level APIs (`EVP_EncryptInit_ex`, `EVP_PKEY_*`, `EVP_DigestInit_ex`, `EVP_Q_MAC`)
- Store keys in KMS/HSM; generate with a CSPRNG — never software-generated and in-source
- Keep algorithm/protocol choices in config, not hardcoded

## Key management
- Generate keys with a CSPRNG; store in KMS/HSM
- Separate encryption keys from signing keys
- Rotate per policy; re-keys (e.g. IKEv2 CREATE_CHILD_SA) must preserve hybrid algorithms
- Expose algorithm choices via config/policy so swapping is a deploy, not a code change
- Emit telemetry on negotiated groups, handshake sizes, and failure causes to track PQC adoption

## Example — AES-256-GCM (C/OpenSSL EVP)

```c
EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, key, iv);
EVP_EncryptUpdate(ctx, ct, &len, pt, pt_len);
EVP_EncryptFinal_ex(ctx, ct + len, &final_len);
EVP_CIPHER_CTX_free(ctx);
```

## Checklist
- [ ] No banned algorithms in code or transitive dependencies
- [ ] AEAD mode for all symmetric encryption
- [ ] TLS 1.3 enforced end-to-end; legacy/draft hybrid groups removed
- [ ] Keys in KMS/HSM, never in source; CSPRNG for generation
- [ ] Algorithm choices configurable, not hardcoded
- [ ] C code uses EVP_*, not deprecated `AES_*`/`RSA_*`/`SHA1_*`
