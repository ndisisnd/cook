---
description: Password storage — approved slow-hash algorithms, parameters, salting, and upgrade paths
alwaysApply: false
---

# Password Storage

Passwords must be hashed (one-way), not encrypted (reversible).

## NEVER
- Store passwords in plaintext, reversible encryption, or with fast hashes (MD5, SHA-1, SHA-256 unsalted)
- Implement salting manually when using a modern hashing library (handled automatically)
- Use `bcrypt(sha512($password))` pre-hashing — vulnerable to password shucking
- Store the pepper in the same database as the hashes
- Use work factors below the minimums in the table below

## ALWAYS
- Use a slow, memory-hard hashing algorithm — Argon2id preferred
- Accept the full Unicode character range including null bytes; never truncate entropy
- Generate salts with a CSPRNG (modern libs do this automatically)
- Store pepper in a secrets vault or HSM, separate from the password database
- Tune work factor so hash computation takes < 1 second on production hardware
- Store algorithm identifier and parameters with each hash (PHC string format)
- Provide an upgrade path when migrating from legacy weak algorithms

## Approved Algorithms

| Algorithm | Minimum parameters | When to use |
|-----------|-------------------|-------------|
| Argon2id | m=19456 (19 MiB), t=2, p=1 | Preferred |
| scrypt | N=2^17, r=8, p=1 | If Argon2id unavailable |
| bcrypt | work factor ≥ 10; max 72-byte input | Legacy systems only |
| PBKDF2-HMAC-SHA256 | 600,000 iterations | FIPS-140 required |
| PBKDF2-HMAC-SHA512 | 210,000 iterations | FIPS-140 required |
| PBKDF2-HMAC-SHA1 | 1,300,000 iterations | FIPS-140 required |

## Legacy Hash Upgrade
- **Method 1:** Force password reset — expire weak hashes, require reset on next login
- **Method 2:** Layer hash — `argon2id(md5_hash)` at login, replace with direct hash on next auth

## Peppering
- Apply as pre-hash addition or post-hash HMAC (key = pepper)
- Use `bcrypt(base64(hmac-sha384($password, $pepper)), $salt, $cost)` if pre-hashing with bcrypt
- Changing pepper requires all users to reset passwords

## Checklist
- [ ] Argon2id (or approved fallback) used with parameters meeting minimums
- [ ] No plaintext, MD5, SHA-1, or fast-hash storage
- [ ] Salts CSPRNG-generated and unique per password (library-managed)
- [ ] Work factor validated on production hardware (< 1s)
- [ ] Pepper stored outside the password database
- [ ] Full Unicode input accepted without truncation
- [ ] Migration path in place for any legacy weak hashes
