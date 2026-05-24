# Security

## UI Security

- Never use `dangerouslySetInnerHTML` or equivalent without explicit sanitization.
- Never construct URLs from unsanitized user input.

## Ownership Scoping

- Scope every resource query by owner or tenant ID alongside any user-supplied ID.

> Authentication, token storage, session, CSRF, RBAC route-guards, and credential
> hashing live in [auth.md](auth.md). Routing and the always-on `localStorage`
> token rule moved there.

## Input Validation

- Validate once at the server boundary. Mirror in the UI for UX only — the server is the source of truth.

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

## OWASP Web Application Top 10 (2021)

| ID | Risk | Key detection signal |
| --- | --- | --- |
| A01 | Broken Access Control | `findById(params.id)` without owner filter. Route without auth guard. |
| A02 | Cryptographic Failures | MD5 or SHA1 for passwords. HTTP URL hardcoded. No TLS. |
| A03 | Injection | String concat in DB queries. Unsanitized input to templates or eval. |
| A04 | Insecure Design | No rate limiting on auth. Missing input validation at entry points. |
| A05 | Security Misconfiguration | CORS `*`. Debug mode in prod. Missing CSP, HSTS headers. |
| A06 | Vulnerable Components | CVE in dependency audit. Unreviewed new direct dependency. |
| A07 | Auth Failures | JWT without expiry. No session invalidation on logout. |
| A08 | Data Integrity Failures | Unverified JWT or cookie. Deserialization of untrusted input. |
| A09 | Logging & Monitoring | No audit log on deletion, password change, or privilege escalation. |
| A10 | SSRF | HTTP client with user-controlled URL and no allowlist. |

## OWASP API Security Top 10 (2023)

| ID | Risk | Key detection signal |
| --- | --- | --- |
| API1 | Broken Object Level Auth (BOLA) | Resource lookup by user-supplied ID without `AND owner_id = currentUser`. |
| API2 | Broken Authentication | JWT missing `exp`. Token not revoked on logout. Bearer token in URL. |
| API3 | Broken Property Level Auth | Full ORM entity returned. No DTO projection. Mass assignment. |
| API4 | Unrestricted Resource Consumption | No server-enforced `limit` or `pageSize`. No throttle on heavy operations. |
| API5 | Broken Function Level Auth | Admin route reachable without role guard. |
| API6 | Unrestricted Business Flow | No verification on OTP, checkout, or password-reset flows. |
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
  . --include="*.ts" --include="*.js" --include="*.go" --include="*.java" --include="*.dart"
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
