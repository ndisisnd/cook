---
description: OAuth 2.0 security — PKCE, grant types, token binding, and redirect URI validation
alwaysApply: false
---

# OAuth 2.0 Security

## NEVER
- Use Resource Owner Password Credentials Grant — exposes credentials to the client
- Use Implicit Grant (`response_type=token`) — use Authorization Code instead
- Allow open redirectors: never forward browsers to arbitrary URIs from query params
- Allow wildcard or partial redirect URI matching — use exact string matching only
- Use `plain` PKCE code challenge method — use S256 only
- Transmit authorization responses over unencrypted connections
- Allow `http` redirect URIs except for native clients on loopback interface
- Allow clients to influence their own `client_id` or `sub` values

## ALWAYS
- Validate redirect URIs by exact string match during registration and at runtime
- Implement PKCE for all public clients; enforce `code_verifier` at the token endpoint
- Prevent PKCE downgrade: reject `code_verifier` when no `code_challenge` was in the auth request
- Use one-time CSRF tokens in `state`, or rely on PKCE/nonce for CSRF protection
- Use `iss` parameter or distinct redirect URIs to prevent mix-up attacks in multi-AS environments
- Sender-constrain tokens with mTLS or DPoP to prevent replay
- Apply refresh token rotation or ensure refresh tokens are sender-constrained
- Restrict tokens to minimum scope; enforce audience restriction on Resource Servers
- Use asymmetric client authentication (mTLS, `private_key_jwt`) over shared secrets
- Enforce TLS end-to-end for all OAuth communications

## Grant & Token Summary

| Concern | Requirement |
|---------|-------------|
| Grant type | Authorization Code (`code` or `code id_token`) only |
| PKCE challenge | S256; never `plain` |
| CSRF | `state` with one-time token, PKCE, or OIDC `nonce` |
| Token binding | mTLS or DPoP |
| Client auth | Asymmetric (mTLS, `private_key_jwt`) preferred |
| Audience | RS must verify token was issued for it |
| Scope | Minimum required; use `authorization_details` for fine-grained control |

## Checklist
- [ ] PKCE (S256) implemented for all public clients; downgrade attack prevented
- [ ] Redirect URIs validated by exact string match
- [ ] Implicit Grant and ROPC Grant absent
- [ ] CSRF protection via `state`, PKCE, or `nonce`
- [ ] Tokens sender-constrained (mTLS or DPoP)
- [ ] Audience restriction enforced on Resource Servers
- [ ] Asymmetric client authentication used
