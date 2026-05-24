---
name: global
description: Universal P0 coding standards for any language or stack. Use when writing, reviewing, or refactoring code. Layer- and concern-specific rules live in refs/ and are loaded by cook based on the task.
metadata:
  triggers:
    files:
      - '**/*.ts'
      - '**/*.tsx'
      - '**/*.js'
      - '**/*.jsx'
      - '**/*.go'
      - '**/*.dart'
      - '**/*.java'
      - '**/*.kt'
      - '**/*.swift'
      - '**/*.py'
    keywords:
      - solid
      - kiss
      - dry
      - yagni
      - refactor
      - clean code
      - readability
      - naming
      - error handling
      - security
      - performance
---

# Global Standards

## Priority: P0 — Universal Rules

### Core Design

- Apply `SOLID`, especially Single Responsibility: each function, component, class, or service has one clear reason to change.
- Apply `KISS`: choose the simplest design that solves the current problem correctly.
- Apply `DRY`: remove repeated logic when the duplication is real and stable, not accidental similarity.
- Apply `YAGNI`: do not add abstraction, configurability, or extension points without a present need.

### Readability

- Use intention-revealing names. A reader should understand purpose without decoding abbreviations.
- Guard clauses and early returns over deep nesting.
- Explicit data flow over hidden side effects.
- Keep units focused enough to reason about quickly. Split when one unit mixes unrelated responsibilities.
- Comments explain why, constraints, or non-obvious tradeoffs — not what the code already says.

### Safety

- Validate and sanitize all untrusted input at every boundary.
- Handle errors explicitly. Never swallow exceptions or return failures that hide the cause.
- Add context when propagating errors so failures are diagnosable.
- Never hardcode secrets, tokens, or credentials.
- Never leak sensitive data, PII, or internal stack details to users, clients, or logs.
- Clean up owned resources: subscriptions, listeners, timers, streams, connections.

### Security Baseline

Three rules that apply on every code write, regardless of context:

- No raw SQL string concatenation. Parameterized queries or ORMs only.
- No wildcard CORS on authenticated routes. Explicit allowlisted origins only.
- No full ORM entity returned from an API endpoint. Project to DTO always.
- No auth tokens in `localStorage`/`sessionStorage`. Use `httpOnly` cookies; deeper auth rules live in `refs/auth.md`.

### Change Quality

- Remove dead code, debug code, and stale fallbacks before finishing.
- Cover changed logic and important edge cases with appropriate verification.
- Keep behavior, naming, and structure consistent with the existing project unless there is a clear reason to improve.

---

## Anti-Patterns

- Clever code that obscures intent
- Deep nesting instead of guard clauses
- Duplicated business logic across files or layers
- Hardcoded secrets or sensitive data in logs
- Resource lookups without owner or tenant scoping
- Global mutable state
- Premature optimization without measurement
- Debug code or dead code left in production paths
- Component mixing UI, business logic, and data fetching

---

## References

Load only what the current task requires:

- [api-design](refs/api-design.md) — HTTP semantics, status codes, URL design, versioning, pagination, or OpenAPI
- [error-handling](refs/error-handling.md) — error hierarchies, response envelopes, or error-boundary placement
- [security](refs/security.md) — injection, CORS, SSRF, XSS, OWASP checklist, or running a SAST scan
- [auth](refs/auth.md) — OAuth/PKCE flows, token storage, session, CSRF, RBAC, credential hashing, brute-force/rate-limiting, JWT verification, password reset, MFA, service-to-service auth
- [architecture](refs/architecture.md) — auditing structural debt, detecting logic leakage, or remediating God classes
- [performance](refs/performance.md) — profiling bottlenecks, batching queries, or fixing memory leaks
- [debug](refs/debug.md) — troubleshooting crashes, tracing failures, or filing a structured bug report
- [cicd](refs/cicd.md) — vendor-neutral pipeline shape, gating, secrets handling, artifact promotion
