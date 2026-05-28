---
description: Secure web services via TLS, authentication, authorization, input validation, and XML/DoS protection
alwaysApply: false
---

# Web Service Security

## NEVER
- Accept Basic Authentication where Client Certificate / Mutual-TLS is appropriate
- Skip authorization checks on any method, request, or privileged resource
- Omit schema validation (XSD) on SOAP/XML payloads
- Parse XML without protection against entity expansion, XML bombs, or recursive payloads
- Serve SOAP attachments without virus scanning before storage
- Accept unbounded message sizes (no SOAP size limits)

## ALWAYS
- Use well-configured TLS for all web service communications
- Validate server certificates: trusted issuer, not expired/revoked, domain match, proven key ownership
- Enforce consistent encoding styles between client and server
- Authorize clients on every request; re-check privileges for requested resources each call
- Separate administrative endpoints from regular service endpoints
- Add challenge-response for sensitive operations (password changes, payment instructions, contact updates)
- Apply output encoding to prevent XSS when web service data is consumed by web clients
- Comply with WS-I Basic Profile as security baseline

## Input Validation

| Target | Requirement |
|--------|-------------|
| SOAP payloads | Validate against XSD |
| All parameters | Define max length and character set |
| Fixed-format fields | Strong allow-list pattern (zip, phone) |
| XML entities | Reject malformed entities and XML bombs |
| External entities | Block or reject |

## Resource Protection

- Limit SOAP message sizes to prevent DoS
- Cap CPU cycles, memory, and simultaneous connections
- Configure parser limits: max recursion depth, payload size, entity expansion, element name length
- Build test cases to verify parser resistance to recursive/oversized/entity-expansion payloads

## Message Integrity

- Sign XML data requiring integrity beyond TLS with sender's private key
- Encrypt sensitive data with strong ciphers for transport and at-rest when required

## Checklist
- [ ] All endpoints use TLS with validated server certificates
- [ ] Every request authorized; privileges re-checked per call
- [ ] SOAP payloads validated against XSD with length/charset limits
- [ ] XML parser hardened against bombs, recursion, entity expansion, overlong names
- [ ] SOAP message size limits enforced
- [ ] SOAP attachments virus-scanned before storage
- [ ] Output encoding applied before data reaches web clients
