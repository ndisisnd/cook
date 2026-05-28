---
description: X.509 certificate validation — expiry, key strength, signature algorithm, self-signed checks
alwaysApply: true
---

# Digital Certificates

When you see certificate data — `-----BEGIN CERTIFICATE-----` blocks, `.pem`/`.crt`/`.cer`/`.der` reads, or calls like `PEM_read_X509`, `cryptography.x509.load_pem_x509_certificate`, `CertificateFactory`, `tls.LoadX509KeyPair` — verify the properties below before accepting it.

## NEVER
- Accept an expired or not-yet-valid certificate
- Use RSA <2048-bit or EC curves <256-bit (`secp192r1`, P-192, P-224)
- Accept certificates signed with MD5 or SHA-1 (`md5WithRSAEncryption`, `sha1WithRSAEncryption`)
- Trust self-signed certificates for public-facing production systems
- Hardcode certificate data in source — load from files or a certificate store so rotation is possible
- Disable certificate verification (`verify=False`, `InsecureSkipVerify`, `rejectUnauthorized: false`) outside of explicit local test setups

## ALWAYS
- RSA ≥2048-bit (prefer 3072+) or ECDSA on P-256+ curve
- SHA-2 family signatures (`sha256WithRSAEncryption` or stronger)
- Validate full chain to a trusted root; check revocation (OCSP stapling or CRL)
- Validate hostname/SAN against the connection target
- Load certs from external files, a cert store, or a secret manager — rotatable without redeploy

## Validation checks

| # | Condition | Severity | Action |
| - | --------- | -------- | ------ |
| 1 | `notAfter` in the past | CRITICAL | Reject; renew immediately |
| 2 | `notBefore` in the future | Warning | Reject until valid window starts |
| 3 | RSA <2048 or EC <256-bit | High | Re-issue with RSA-2048+ or ECDSA P-256+ |
| 4 | Signed with MD5 or SHA-1 | High | Re-issue with SHA-256+ |
| 5 | `Issuer == Subject` (self-signed) | Info | Allow only for dev/test/internal with explicit trust |

## Inspection

```bash
openssl x509 -text -noout -in <cert>
```

Reports `notBefore`/`notAfter`, public-key algorithm and size, signature algorithm, and issuer/subject — everything needed for the checks above.

## Checklist
- [ ] No expired or not-yet-valid certs in use
- [ ] All keys meet minimum strength (RSA 2048+, EC P-256+)
- [ ] No MD5/SHA-1 signatures anywhere in the chain
- [ ] Self-signed certs confined to dev/test/internal
- [ ] No hardcoded cert blobs; loaded from files/store/secret-manager
- [ ] Chain + hostname + revocation validated on every TLS handshake
- [ ] No `verify=False` / `InsecureSkipVerify` / `rejectUnauthorized:false` outside local tests
