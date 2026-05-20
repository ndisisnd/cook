---
name: global
description: Universal coding standards for frontend, backend, and full-stack work. Use when writing, reviewing, or refactoring code across any language or stack. Invoke with --frontend, --backend, or --full-stack to activate mode-specific rules.
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

### Change Quality

- Remove dead code, debug code, and stale fallbacks before finishing.
- Cover changed logic and important edge cases with appropriate verification.
- Keep behavior, naming, and structure consistent with the existing project unless there is a clear reason to improve.

---

## Priority: P1 — Mode-Specific Rules

### --frontend

Apply when the change touches components, pages, hooks, or styling.

**Component structure**
- One component per file. No cross-concern mixing in a single component.
- Keep state as local as possible. Lift only when two or more components need the same state.
- Extract business logic from components into hooks or services. Components describe UI, not decisions.

**UI security**
- Never use `dangerouslySetInnerHTML` or equivalent without explicit sanitization.
- Never construct URLs from unsanitized user input.
- Never store auth tokens in `localStorage` — prefer `httpOnly` cookies or short-lived session memory.

**Performance**
- Avoid unnecessary re-renders: memoize stable callbacks and computed values only when there is a measured reason.
- Avoid data waterfalls: fetch in parallel at the highest appropriate boundary.
- Virtualize long lists. Never render unbounded item counts into the DOM or widget tree.

### --backend

Apply when the change touches services, controllers, handlers, routes, or DB access.

**API semantics**
- `GET` is read-only and idempotent. Never mutate state in a `GET`.
- Use correct status codes. `201` for created resources. `204` for empty responses. Never `200` for an error.
- Paginate all list endpoints. Default limit 20, max 100. Reject requests that exceed the max.

**Error architecture**
- Domain layer throws pure business errors with no HTTP status codes.
- API layer maps domain errors to HTTP responses globally — not per-handler.
- Infrastructure layer wraps third-party exceptions and never leaks raw DB errors upward.

**Auth and ownership**
- Scope every resource query by owner or tenant ID alongside any user-supplied ID.
- Require auth on all routes by default. Explicit opt-out only.
- Every role-gated action has a guard. No open admin routes.

**Performance**
- No N+1 queries. Batch or join data access.
- Index every foreign key and filter column used in hot queries.

### --full-stack

Apply both `--frontend` and `--backend` rules. Additionally:

- No business logic leaked from backend services into frontend components.
- Validate once at the server boundary. Mirror in the UI for UX only.
- API contract changes — field removal, rename, or status code change — require a version bump.

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
- [security](refs/security.md) — auth, encryption, access control, OWASP checklist, or running a SAST scan
- [architecture](refs/architecture.md) — auditing structural debt, detecting logic leakage, or remediating God classes
- [performance](refs/performance.md) — profiling bottlenecks, batching queries, or fixing memory leaks
- [debug](refs/debug.md) — troubleshooting crashes, tracing failures, or filing a structured bug report
