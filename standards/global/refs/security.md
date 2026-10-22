---
last_reviewed: 2026-10-18
---

# Security

## UI Security

- Never use `dangerouslySetInnerHTML` or equivalent without explicit sanitization.
- Never construct URLs from unsanitized user input.

## Ownership Scoping

- Scope every resource query by owner or tenant ID alongside any user-supplied ID.

> Authentication, token storage, session, CSRF, RBAC route-guards, credential
> hashing, brute-force/rate-limiting on auth endpoints, JWT signature verification,
> and password-reset flows live in [auth.md](auth.md). The OWASP tables below stay as
> the master detection reference.

## Input Validation

- Validate once at the server boundary. Mirror in the UI for UX only — the server is the source of truth.

## Exceptional Conditions (A10:2025)

- Fail closed. An exception in an auth, payment, or permission check denies the request.
- Roll back partial state on failure (transaction, compensating action). Never leave half-applied writes.
- Return a generic error to the client. Log the detail server-side with a correlation ID.

## LLM and Agent Output

- Treat model output, tool results, and retrieved content as untrusted input. Validate before use in SQL, shell, HTML, or URLs.
- A tool call with destructive or external effect (delete, pay, send, deploy) needs human confirmation.
- Give each agent tool the narrowest scope and a short-lived credential. Never put secrets in prompts.

## Secure Coding Patterns

### Parameterized Queries

```typescript
// Parameterized — prevents SQL injection
const user = await db.query(
  'SELECT * FROM users WHERE email = $1 AND status = $2',
  [email, 'active']
);
// Never: `WHERE email = '${email}'`
```

### Secret Management

```python
import os
API_KEY = os.environ["API_KEY"]  # from environment
# API_KEY = "sk-abc123"          # hardcoded — never commit
```

## OWASP Web Application Top 10 (2025)

| ID | Risk | Key detection signal |
| --- | --- | --- |
| A01 | Broken Access Control (incl. SSRF) | `findById(params.id)` without owner filter. Route without auth guard. HTTP client with user-controlled URL and no allowlist. |
| A02 | Security Misconfiguration | CORS `*`. Debug mode in prod. Missing CSP, HSTS headers. Default credentials. |
| A03 | Software Supply Chain Failures | CVE in dependency audit. Unpinned or unreviewed new dependency. Install scripts enabled. CI action pinned by tag, not SHA. |
| A04 | Cryptographic Failures | MD5 or SHA1 for passwords. HTTP URL hardcoded. No TLS. |
| A05 | Injection | String concat in DB queries. Unsanitized input to templates, shell, or eval. |
| A06 | Insecure Design | No rate limiting on auth. Missing input validation at entry points. |
| A07 | Authentication Failures | JWT without expiry. No session invalidation on logout. |
| A08 | Software or Data Integrity Failures | Unverified JWT or cookie. Deserialization of untrusted input. Unsigned update or artifact. |
| A09 | Security Logging & Alerting Failures | No audit log on deletion, password change, or privilege escalation. No alert on repeated auth failure. |
| A10 | Mishandling of Exceptional Conditions | `catch` that allows the request on error (fail-open). Swallowed exception. Partial write left on failure. |

## OWASP API Security Top 10 (2023)

| ID | Risk | Key detection signal |
| --- | --- | --- |
| API1 | Broken Object Level Auth (BOLA) | Resource lookup by user-supplied ID without `AND owner_id = currentUser`. |
| API2 | Broken Authentication | JWT missing `exp`. Token not revoked on logout. Bearer token in URL. |
| API3 | Broken Property Level Auth | Full ORM entity returned. No DTO projection. Mass assignment. |
| API4 | Unrestricted Resource Consumption | No server-enforced `limit` or `pageSize`. No throttle on heavy operations. |
| API5 | Broken Function Level Auth | Admin route reachable without role guard. |
| API6 | Unrestricted Business Flow | No verification on OTP, checkout, or password-reset flows. |
| API7 | Server Side Request Forgery | Webhook, URL preview, or import fetches a user-supplied URL with no allowlist or private-IP block. |
| API8 | Security Misconfiguration | Stack trace in response. CORS `*` on authenticated routes. |
| API9 | Improper Inventory Management | Deprecated or undocumented endpoints still reachable. |
| API10 | Unsafe API Consumption | Third-party response used without schema validation. |

## Security Scan Commands (SAST)

### Hardcoded Secrets

```bash
grep -riE "(password|apiKey|api_key|secret|private_key|token)\s*=\s*['\"][^'\"]{6,}" \
  . --exclude-dir={node_modules,dist,build,.git} -l
```

### PII in Logs

```bash
# TypeScript/JavaScript
grep -rE "console\.(log|error|warn)" . --include="*.ts" --include="*.js" | grep -iE "password|token|secret"
# Go
grep -rE "log\.(Print|Printf|Println|Fatal)" . --include="*.go" | grep -iE "password|token|secret"
# Dart
grep -rE "print\(|debugPrint\(" . --include="*.dart" | grep -iE "password|token|secret"
```

### SQL Injection Surfaces

```bash
grep -rE "\+.*SELECT|\+.*INSERT|\+.*UPDATE|\+.*DELETE|query\(.*\+|fmt\.Sprintf.*SELECT" \
  . --include="*.ts" --include="*.js" --include="*.go" --include="*.py" --include="*.dart"
```

### Auth Coverage (NestJS example)

```bash
total=$(grep -rE "@(Get|Post|Put|Delete|Patch)\(" . | wc -l)
guarded=$(grep -rE "@(UseGuards|Auth)\(" . | wc -l)
# guarded/total should be close to 1.0
```

### RCE / SSRF / Path Traversal

| Risk | Pattern to scan for |
| --- | --- |
| RCE | `eval(`, `new Function(`, `shell_exec(`, `exec(` with dynamic input |
| SSRF | `axios.get(`, `fetch(`, `http.Get(` where URL is user-controlled |
| Path traversal | File I/O where path comes from user input without `path.join` or equivalent normalization |

## Dependency CVE Scans

```bash
npm audit --audit-level=high    # Node
dart pub outdated --json        # Dart/Flutter
go list -m -u all               # Go
pip-audit                       # Python
cargo audit                     # Rust
```
