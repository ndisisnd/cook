---
description: LDAP injection prevention — escaping, input validation, and least-privilege binding for directory queries
alwaysApply: false
---

# LDAP Injection Prevention

## NEVER
- Concatenate untrusted user input directly into LDAP search filters or DNs
- Use administrative or write-capable accounts for application LDAP bindings
- Allow anonymous connections or unauthenticated binds
- Write custom escaping routines; use established security libraries instead

## ALWAYS
- Escape all untrusted data before incorporating it into LDAP queries
- Use context-appropriate escaping: DN escaping differs from search filter escaping
- Validate input against an allowlist of known-safe characters before query construction
- Normalize user input before validation
- Use read-only, least-privilege binding accounts for application connections
- Configure LDAP with bind authentication to enforce verification and authorization

## Escaping Reference

| Context | Characters requiring escaping |
|---|---|
| Distinguished Name (DN) | `\ # + < > , ; " =` and leading/trailing spaces |
| Search Filter | `* ( ) \ NUL` |

Characters allowed unescaped in DNs: `* ( ) . & - _ [ ] \` ~ | @ $ % ^ ? : { } ! '`

## Library Implementations

| Platform | API |
|---|---|
| Java (ESAPI) | `encodeForLDAP(String)`, `encodeForDN(String)` |
| .NET | `Encoder.LdapFilterEncode()` (RFC 4515), `Encoder.LdapDistinguishedNameEncode()` (RFC 2253) |
| .NET Framework 4.5 | LINQ to LDAP (automatic encoding) |

Java allowlist pattern (validate before building filter):
```java
if (!userSN.matches("[\\w\\s]*") || !userPassword.matches("[\\w]*"))
    throw new IllegalArgumentException("Invalid input");
```

## Checklist
- [ ] All user input escaped with context-correct method (DN vs filter) before LDAP query
- [ ] Established library used for escaping (ESAPI, .NET Encoder) — no custom routines
- [ ] Input validated against allowlist of safe characters prior to query construction
- [ ] LDAP binding account is read-only and least-privilege
- [ ] Anonymous and unauthenticated binds disabled
- [ ] Sensitive data stored in sanitized form
