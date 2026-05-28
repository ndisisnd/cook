---
description: Configure TLS correctly — strong protocols, ciphers, certificates, and application-level enforcement
alwaysApply: false
---

# Transport Layer Security

## NEVER
- Enable TLS 1.0, TLS 1.1, SSL v2, or SSL v3
- Use null, anonymous, or EXPORT cipher suites
- Enable TLS compression (CRIME attack vector)
- Use MD5 or SHA-1 for certificate hashing
- Use certificate key sizes below 2048 bits
- Mix HTTP and HTTPS resources on the same page (mixed content)
- Transmit cookies without the `Secure` attribute
- Pin public keys in browsers (HPKP is deprecated)
- Use wildcard certificates for systems at different trust levels

## ALWAYS
- Default to TLS 1.3; support TLS 1.2 only for legacy compatibility
- Enable `TLS_FALLBACK_SCSV` when TLS 1.2 fallback is required
- Prefer GCM ciphers; use Mozilla SSL Config Generator for balanced cipher list
- Set Diffie-Hellman groups to secure values (x25519, secp256r1, ffdhe3072 or stronger)
- Keep all SSL/TLS libraries patched and current
- Use SHA-256 for certificate signing
- Match certificate CN and SAN to the server's FQDN
- Redirect all HTTP to HTTPS with 301; serve HSTS header
- Load all page resources (JS, CSS, images) over HTTPS
- Mark all cookies `Secure`
- Send `Cache-Control: no-cache, no-store, must-revalidate` for sensitive responses
- Implement HSTS (`Strict-Transport-Security`) to prevent bypass of certificate warnings
- Consider mTLS for high-value applications requiring mutual authentication

## DH Group Config Examples

```text
# OpenSSL
Groups = x25519:prime256v1:x448:ffdhe2048:ffdhe3072

# Apache
SSLOpenSSLConfCmd Groups x25519:secp256r1:ffdhe3072

# NGINX
ssl_ecdh_curve x25519:secp256r1:ffdhe3072;
```

## Sensitive-Data Cache Headers
```text
Cache-Control: no-cache, no-store, must-revalidate
Pragma: no-cache
Expires: 0
```

## Checklist
- [ ] TLS 1.0/1.1/SSL v2/v3 disabled; TLS 1.3 default
- [ ] Null, anon, EXPORT ciphers disabled; GCM preferred
- [ ] TLS compression disabled
- [ ] Certificate: ≥2048-bit key, SHA-256, CN/SAN matches FQDN
- [ ] All HTTP redirects to HTTPS (301) with HSTS header
- [ ] No mixed content — all resources loaded over HTTPS
- [ ] All cookies carry `Secure` attribute
- [ ] Sensitive responses carry no-store cache headers
- [ ] TLS config validated with SSL Labs / testssl.sh
