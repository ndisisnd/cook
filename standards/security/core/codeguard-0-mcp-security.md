---
description: MCP (Model Context Protocol) security — workload identity, sandboxing, prompt-injection, transport, HITL
alwaysApply: false
---

# MCP Security

Based on CoSAI MCP Security guidelines. Never deploy MCP servers or clients without these controls.

## NEVER
- Run MCP servers or LLM-generated code with full user privileges
- Trust tool schemas, metadata, prompts, or resource content as anything other than untrusted input
- Rely on the LLM for validation or authorization decisions
- Rely solely on human approval — users fatigue and click through
- Load unsigned MCP servers; deploy without signature verification
- Expose remote MCP servers without authentication, mTLS, and rate limiting
- Build "do anything" tools with broad scope

## ALWAYS
- Validate all inputs via allow-lists at every trust boundary
- Sanitize file paths by canonicalization; use parameterized queries; apply context-aware output encoding
- Sanitize tool outputs — minimum fields only, redact PII
- Deploy prompt-injection detection
- Use strict JSON schemas to maintain instruction/data boundary
- Use single-purpose tools with explicit, narrow boundaries
- Use two-stage commit for high-impact actions: draft/preview → explicit commit with confirmation
- Provide rollback/undo paths (draft IDs, snapshots, time-bound commits)
- Log tools used, parameters, originating prompt; use OpenTelemetry for end-to-end linkability
- Maintain immutable audit records of actions and authorizations

## Workload identity
- Use SPIFFE/SPIRE for cryptographic workload identities
- Issue and rotate short-lived SVIDs

## Sandboxing & isolation
- Design servers to execute with least privilege
- Any server touching host (files, commands, network) MUST be sandboxed
- Add additional layers: gVisor, Kata Containers, SELinux sandboxes

## Cryptographic verification
- Provide cryptographic signatures and SBOMs for all server code
- Verify signatures in the client before loading servers
- Use TLS for all data in transit
- Implement remote attestation to verify servers run expected code

## Transport

### stdio (local servers)
- STRONGLY RECOMMENDED for local MCP — eliminates DNS rebinding risk
- Pipe-based stream communication
- Sandbox to prevent privilege escalation

### HTTP streaming (remote servers) — required controls
- Payload size limits (prevent large/recursive DoS)
- Rate limiting on tool calls and requests
- Client-server authn/z
- Mutual TLS authentication
- TLS encryption
- CORS + CSRF protection
- Integrity checks (prevent replay, spoofing, poisoned responses)

## Deployment patterns

| Pattern | Required controls |
| ------- | ----------------- |
| **All-local (stdio)** | Host posture is the trust boundary; use stdio; sandbox the server |
| **Single-tenant remote (http)** | Authn between client and server; secure credential storage (OS keychain, secret manager); authenticated discovery with allow-list |
| **Multi-tenant remote (http)** | Robust tenant isolation; per-tenant encryption; RBAC; prefer provider-hosted; remote attestation when possible |

## Human-in-the-loop
- Confirmation prompts for risky operations on the server side (via elicitation)
- Security-relevant messages must clearly state implications
- Do not over-prompt — users fatigue; combine with structural safeguards

## Checklist
- [ ] Workload identity via SPIFFE/SPIRE; short-lived SVIDs
- [ ] All servers sandboxed; least privilege; LLM-generated code never runs as user
- [ ] Server signatures and SBOMs verified before load
- [ ] stdio for local; HTTP streaming has payload limits, rate limits, mTLS, CORS, CSRF, integrity
- [ ] Tools single-purpose with allow-list inputs; two-stage commit on impact
- [ ] LLM never makes authz decisions; HITL combined with structural safeguards
- [ ] Tool calls, parameters, and prompts logged; OpenTelemetry linkability
