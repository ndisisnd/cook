---
description: Harden XML parsing against XXE, SSRF, DoS, schema poisoning, and data integrity attacks
alwaysApply: false
---

# XML Security

## NEVER
- Enable DTD processing or external entity resolution on untrusted XML
- Load schemas over unencrypted HTTP or from untrusted remote locations
- Allow XML parser to make unconstrained outbound network calls
- Accept XML documents without depth/size limits
- Store schemas with lax filesystem permissions

## ALWAYS
- Use a standards-compliant parser with `disallow-doctype-decl`, `external-general-entities`, and `external-parameter-entities` disabled
- Reject malformed XML and halt on fatal parse errors
- Validate all XML against local, trusted XSDs with narrow type restrictions
- Enforce explicit `maxOccurs` limits on all elements
- Enforce nesting depth and document size limits to prevent DoS
- Perform business logic validation after schema validation (e.g., numeric ranges on payment amounts)
- Reject unexpected elements or attributes outside the schema
- Keep XML processing libraries up to date with secure defaults
- Log and monitor parse errors and rejections; alert on repeated failures
- Audit local schema files regularly for unauthorized changes

## Schema Design

- Use explicit types, length limits, regex patterns, and enumerations in XSDs
- Prefer XSD over DTD; avoid DTDs entirely where possible
- Use `xs:assertion` for cross-field constraints where supported
- Store all schemas locally; apply strict filesystem permissions

## SSRF / Network Isolation

- Disable external entity resolution or restrict to local whitelisted resources
- Validate and sanitize all external URI references in XML entities
- Monitor for unexpected DNS lookups or network activity during parsing
- Sandbox XML processing to block outbound calls

## DoS Prevention

- Enforce maximum element nesting depth
- Enforce maximum document size (bytes)
- Reject or timeout on unexpectedly complex documents
- Test parser CPU usage differences between valid and malformed inputs

## Checklist
- [ ] Parser DTD and external-entity features disabled
- [ ] All XML validated against local, versioned XSD schemas
- [ ] `maxOccurs` explicit on every element; depth and size limits enforced
- [ ] Business logic validation applied post-schema
- [ ] Outbound network calls from parser blocked or sandboxed
- [ ] Parse errors logged; alerts on repeated failures
- [ ] Schema files stored locally with restricted permissions and audited
