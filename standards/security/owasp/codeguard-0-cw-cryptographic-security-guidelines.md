---
description: C/OpenSSL cryptographic API rules — banned algorithms, deprecated functions, and EVP replacements
alwaysApply: false
---

# Cryptographic Security Guidelines (C / OpenSSL)

## NEVER
- Use deprecated low-level APIs: `AES_encrypt/decrypt`, `RSA_new/free`, `SHA1_Init/Update/Final`, `CMAC_Init`, `HMAC()` with SHA1, `DSA_sign()`, `DH_check()`, `AES_wrap/unwrap_key()`
- Use banned hash algorithms: MD2, MD4, MD5, SHA-0
- Use banned symmetric ciphers: RC2, RC4, Blowfish, DES, 3DES
- Use static RSA key exchange or Anonymous Diffie-Hellman (no forward secrecy)
- Leave key material in memory after use — zero it explicitly

## ALWAYS
- Use EVP high-level APIs for all crypto operations
- Use SHA-256, SHA-384, or SHA-512 for hashing
- Use AES-128, AES-256, or ChaCha20 for symmetric encryption
- Use ECDHE or DHE (with proper validation) for key exchange
- Handle all `errno_t` / return values from crypto operations — never ignore errors

## API Replacements

| Deprecated | Replacement |
|------------|-------------|
| `AES_encrypt()`, `AES_decrypt()` | `EVP_EncryptInit_ex()`, `EVP_EncryptUpdate()`, `EVP_EncryptFinal_ex()` |
| `RSA_new()`, `RSA_free()`, `RSA_*` | `EVP_PKEY_new()`, `EVP_PKEY_up_ref()`, `EVP_PKEY_free()` |
| `SHA1_Init/Update/Final()` | `EVP_DigestInit_ex()`, `EVP_DigestUpdate()`, `EVP_DigestFinal_ex()` |
| `CMAC_Init()`, `HMAC()` w/ SHA1 | `EVP_Q_MAC()` with SHA-256 |
| `AES_wrap_key()` | EVP key-wrapping APIs |
| `DSA_sign()`, `DH_check()` | Corresponding EVP APIs |

## Secure AES-GCM Pattern

```c
EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, key, iv);
EVP_EncryptUpdate(ctx, ciphertext, &len, plaintext, plaintext_len);
EVP_EncryptFinal_ex(ctx, ciphertext + len, &len);
EVP_CIPHER_CTX_free(ctx);
```

## Checklist
- [ ] No deprecated SSL/crypto APIs (`AES_*`, `RSA_*`, `SHA1_*`, `CMAC_*`, `HMAC` w/ SHA1)
- [ ] No banned algorithms (MD5, DES, RC4, 3DES, Blowfish, SHA-0)
- [ ] HMAC uses SHA-256 or stronger
- [ ] All crypto via EVP high-level APIs
- [ ] All crypto return values checked and errors handled
- [ ] Key material zeroed after use
