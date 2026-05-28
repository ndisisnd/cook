---
description: Cryptographic key generation, storage, usage separation, rotation, and trust store security
alwaysApply: false
---

# Key Management Security

## NEVER
- Store keys in plaintext format anywhere (memory, disk, config files)
- Read or use cryptographic keys directly from standard application-level code
- Reuse a single key for different cryptographic purposes (e.g., encryption + signing)
- Escrow keys used for digital signatures
- Allow export of keys from the trust store without authentication and authorization

## ALWAYS
- Generate keys within a FIPS 140-2 validated cryptographic module or HSM; generate all random values inside that same module
- Store keys in a cryptographic vault (HSM or isolated cryptographic service)
- Encrypt keys with a Key Encryption Key (KEK) before offline export; KEK strength ≥ protected key strength
- Use ephemeral keys to achieve Perfect Forward Secrecy
- Implement key rotation and full lifecycle management
- Monitor and audit all key access operations
- Use only well-maintained, third-party-validated cryptographic libraries

## Key Lifecycle
- Prefer hardware cryptographic modules over software modules
- Split long-lived in-memory keys into components updated frequently to prevent "burn-in"
- Plan for recovery from corruption of key generation/registration/distribution media
- Back up keys encrypted with a FIPS 140-2 validated module; consider escrow for encryption keys

## Trust Store
- Design controls to block injection of third-party root certificates
- Implement integrity controls on trust store objects
- Set strict policies and procedures for exporting key material
- Implement a secure, audited process for updating the trust store

## Checklist
- [ ] Keys generated inside FIPS 140-2 validated module/HSM with in-module RNG
- [ ] No plaintext key storage; vault or encrypted offline storage used
- [ ] Each key used for exactly one cryptographic purpose
- [ ] Key rotation and lifecycle management implemented
- [ ] Trust store protected against unauthorized injection and export
- [ ] All key access operations logged and audited
