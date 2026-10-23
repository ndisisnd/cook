---
name: global
description: Universal P0 coding standards for any language or stack. Use when writing, reviewing, or refactoring code. Layer- and concern-specific rules live in refs/ and are loaded by cook based on the task.
metadata:
  targets: "Language-agnostic · OWASP Top 10 2025 · OWASP API Security Top 10 2023 · NIST SP 800-63B-4"
  last_reviewed: 2026-10-18
---

# Global Standards

Targets: language-agnostic; security rules track OWASP Top 10 2025.

## Priority: P0 — Universal Rules

### Core Design

- One reason to change per unit. Signal: a name joined by "and", or a component mixing UI, business logic, and data fetching.
- No abstraction, config flag, or extension point without a present caller.
- Extract shared logic only when two copies must change together; similar-looking code is not duplication.

### Readability

- Guard clauses and early returns over deep nesting.
- Explicit data flow over hidden side effects and global mutable state.
- Comments explain why or non-obvious tradeoffs, not what the code says.

### Safety

- Validate and sanitize all untrusted input at every boundary.
- Handle errors explicitly. Never swallow exceptions or return failures that hide the cause.
- Add context when propagating errors so failures are diagnosable.
- Fail closed: an exception in an auth, permission, or payment path denies the action (OWASP A10:2025).
- Never hardcode secrets, tokens, or credentials.
- Never leak sensitive data, PII, or internal stack details to users, clients, or logs.
- Log structured events with a correlation ID; no PII, tokens, or secrets in log fields.
- Clean up owned resources: subscriptions, listeners, timers, streams, connections.

### Security Baseline

Five rules that apply on every code write, regardless of context:

- No raw SQL string concatenation. Parameterized queries or ORMs only.
- Scope every resource lookup by owner or tenant ID, not by the user-supplied ID alone.
- No full ORM entity returned from an API endpoint. Project to DTO always.
- Treat LLM output and tool results as untrusted input. No destructive tool call without human confirmation. See `refs/security.md`.
- Store auth tokens in platform secure storage. Web: `httpOnly` cookies, never `localStorage`/`sessionStorage`. Native: Keychain / Keystore. See `refs/auth.md`.

Web only: no wildcard CORS on authenticated routes; allowlist origins explicitly.

### UI Baseline

- Every control has an accessible label, is reachable and operable by keyboard, and meets WCAG AA contrast (4.5:1 text).

### Change Quality

- Remove dead code, debug code, and stale fallbacks before finishing.
- Cover changed logic and important edge cases with appropriate verification.
- Keep behavior, naming, and structure consistent with the existing project unless there is a clear reason to improve.
- Optimize only after measurement.

## References

Load only what the current task requires:

- [api-design](refs/api-design.md) — HTTP semantics, status codes, URL design, versioning, pagination, or OpenAPI
- [error-handling](refs/error-handling.md) — error hierarchies, response envelopes, or error-boundary placement
- [security](refs/security.md) — injection, CORS, SSRF, XSS, LLM/agent output, OWASP checklist, or running a SAST scan
- [auth](refs/auth.md) — OAuth/PKCE flows, token storage, session, CSRF, RBAC, credential hashing, passkeys, password policy, JWT verification, MFA, service-to-service auth
- [crypto](refs/crypto.md) — algorithms and modes, keys and rotation, randomness, encryption at rest, TLS, certificates
- [architecture](refs/architecture.md) — auditing structural debt, detecting logic leakage, or remediating God classes
- [performance](refs/performance.md) — profiling bottlenecks, batching queries, or fixing memory leaks
- [debug](refs/debug.md) — troubleshooting crashes, tracing failures, or filing a structured bug report
- [cicd](refs/cicd.md) — vendor-neutral pipeline shape, gating, secrets handling, artifact promotion
