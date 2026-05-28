---
description: API and web-services security — REST/GraphQL/SOAP, schema validation, authn/z, SSRF, rate limits
alwaysApply: false
---

# API & Web Services

## NEVER
- Expose management or admin endpoints to the internet
- Accept JWTs without pinning the algorithm; never accept `alg: none`
- Reuse external tokens for internal service-to-service calls — mint a separate internal identity
- Concatenate user input into SQL, command lines, or LDAP filters (see `codeguard-0-input-validation-injection`)
- Accept raw URLs from clients for outbound calls (SSRF)
- Leave GraphQL introspection or IDE (GraphiQL) enabled in production
- Rely on CORS for authorization

## ALWAYS
- HTTPS for all endpoints; consider mTLS for high-value or internal services; validate certs (CN/SAN, revocation)
- Use standard authentication flows (OAuth2/OIDC); for services use mTLS or signed service tokens
- Authorize per-endpoint and per-resource, server-side, deny-by-default
- Validate input against a contract (OpenAPI/JSON Schema, GraphQL SDL, XSD); reject unknown fields and oversize payloads
- Enforce explicit `Content-Type`/`Accept`; reject unsupported combinations
- Apply rate limits (per IP, user, client), circuit breakers, and timeouts
- Use parameterized queries / ORM binds in all resolvers and handlers

## Token specifics
- **JWT:** pin algorithm; validate `iss`, `aud`, `exp`, `nbf`; short lifetimes; rotate; denylist on logout/revoke
- **Opaque tokens:** prefer when revocation is required and a central store exists
- **API keys:** scope narrowly; rate-limit; monitor usage; never use alone for sensitive operations

## SSRF prevention (outbound)
- Validate domains/IPs via a vetted library; restrict to `http`/`https` (block `file://`, `gopher://`, `ftp://`, etc.)
- **Fixed partners:** strict allow-list; disable redirects; network-layer egress allow-list
- **Arbitrary URLs:** block private/link-local/localhost ranges; resolve and verify all returned IPs are public; require signed tokens from target where feasible

## GraphQL-specific
- Limit query depth and overall complexity; enforce pagination; execution timeouts
- Disable introspection and the IDE in production
- Field/object-level authorization to prevent IDOR/BOLA
- Validate batching; rate-limit per object type

## SOAP / WS / XML
- Validate payloads against XSD; cap message size; enable XML signatures/encryption where required
- Harden parsers against XXE, entity expansion, and recursive payloads (see `codeguard-0-xml-and-serialization`)

## Microservices
- Authorize at the gateway (coarse) and at the service (fine)
- Propagate signed internal identity, not the external user token
- Centralized structured logging with correlation IDs; sanitize sensitive data
- Policy-as-code via sidecar or in-process PDP

## Checklist
- [ ] HTTPS/mTLS configured; certs managed; no mixed content
- [ ] Contract validation at edge and service; unknown fields rejected; size/time limits set
- [ ] Strong authn/z per endpoint; deny-by-default
- [ ] GraphQL depth/complexity limits; introspection off in prod
- [ ] SSRF protections at app and network layers; redirects disabled; allow-lists where possible
- [ ] Rate limits, circuit breakers, timeouts in place
- [ ] Management endpoints isolated and strongly authenticated
- [ ] Structured logs with correlation IDs; sensitive fields redacted
- [ ] Contract tests + schema-aware fuzzing in CI
