---
description: Secure SAML implementation — transport, message signing, XML processing, binding, and IdP/SP validation
alwaysApply: false
---

# SAML Security

## NEVER
- Transport SAML messages below TLS 1.2
- Skip digital signature validation on assertions or responses
- Use `getElementsByTagName` to select security elements — use absolute XPath
- Download schemas automatically from third parties — use local trusted copies
- Trust `KeyInfo` elements in SAML documents for key selection
- Allow unsolicited (IdP-initiated) SSO without CSRF and replay protection
- Use deprecated XMLEnc algorithms (e.g., RSA 1.5)
- Accept open redirect `RelayState` URLs without allowlist validation
- Cache SAML messages (enables stolen-assertion and replay attacks)

## ALWAYS
- Sign all SAML messages with certified keys
- Encrypt assertions via XMLEnc
- Perform schema validation on all XML before security processing (local, hardened schemas)
- Validate `InResponseTo` in responses matches previously sent request ID
- Use `StaticKeySelector` (single key) or `X509KeySelector` with local JKS (multiple keys)
- Validate `NotBefore`/`NotOnOrAfter` timestamps and `Recipient` attributes
- Mark responses as `OneTimeUse` to prevent replay
- Use short lifetimes on SAML responses
- Validate IdP certificates: expiration, revocation (CRL/OCSP), algorithm strength
- Treat all SAML input as untrusted; validate and sanitize extracted data

## Required Message Fields

| Message | Required fields |
| ------- | --------------- |
| AuthnRequest | Unique ID, SP identifier |
| Response | Unique ID, SP ID, IdP ID, signed assertion, `InResponseTo` matching request |
| Authentication Assertion | ID, client ID, IdP ID, SP ID |

## XML Signature Security

- Schema-validate before any security use; disable wildcard/relaxed processing
- Use absolute XPath to select signed elements — never relative or `getElementsByTagName`
- For PKIX trust: validate full chain to trusted root CA
- Synchronize to a common Internet time source

## IdP-Initiated SSO (if required)

- Follow SAML Profiles 4.1.5 validation
- Validate `RelayState` URLs against an allowlist
- Implement replay detection at response or assertion level

## Checklist
- [ ] TLS 1.2+ on all SAML transports
- [ ] All assertions signed and encrypted
- [ ] Schema validation runs on every inbound XML using local schemas
- [ ] `InResponseTo` validated against sent request IDs
- [ ] `NotBefore`/`NotOnOrAfter`/`Recipient` validated
- [ ] `OneTimeUse` set; short response lifetimes enforced
- [ ] IdP certs checked for expiration and revocation
- [ ] `RelayState` validated against allowlist for IdP-initiated SSO
- [ ] Deprecated cryptographic algorithms disabled
