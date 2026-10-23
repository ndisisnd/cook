---
last_reviewed: 2026-10-23
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
- Allowlist, never denylist. Canonicalize (Unicode normalize, URL-decode) before validating, not after.
- Anchor regex on structured fields (`^...$`). An unanchored match passes `evil<valid>`. Bound length. Avoid nested quantifiers (ReDoS).
- Never take a file path or name from the client. The server defines all paths.
- Table, column, and sort identifiers cannot be parameterized. Map them to a server-side allowlist.
- Validate email by a single-use, time-limited token, not regex. Limits: local part 64 chars, total 254.
- Cap body size at the edge. Reject unknown fields against the schema (OpenAPI, JSON Schema).

## Exceptional Conditions (A10:2025)

- Fail closed. An exception in an auth, payment, or permission check denies the request.
- Roll back partial state on failure (transaction, compensating action). Never leave half-applied writes.
- Return a generic error to the client. Log the detail server-side with a correlation ID.

## LLM and Agent Output

- Treat model output, tool results, and retrieved content as untrusted input. Validate before use in SQL, shell, HTML, or URLs.
- A tool call with destructive or external effect (delete, pay, send, deploy) needs human confirmation.
- Give each agent tool the narrowest scope and a short-lived credential. Never put secrets in prompts.
- Never concatenate untrusted text (user input, web pages, emails, RAG chunks) into the system prompt. Mark it as data.
- Enforce authorization in code on every tool call, with the end user's identity. The model never decides who may do what. The system prompt is not a secret store: assume it leaks.
- Render model markdown with a link and image allowlist. Image URLs are an exfiltration channel.
- Run generated code only in a sandbox: no network, no host secrets, resource limits.
- Cap tokens, tool calls, recursion depth, wall time, and spend per request. Keep a kill switch.
- Tag memory and RAG entries with source and trust level. Filter retrieval by caller permissions. Isolate tenants in vector stores.
- Pin model, prompt template, MCP server, and plugin versions. Third-party tool descriptions can carry injection.
- Human approval alone fails through fatigue. Show the exact arguments. Use draft then commit for high-impact writes.
- Prefer stdio for local MCP servers. A local HTTP MCP server binds `127.0.0.1` and validates `Origin` (DNS rebinding). Remote MCP servers use OAuth 2.1 with PKCE, check token audience, never pass the client token on to upstream APIs, and rate-limit. Sandbox any server that touches the host.

## Injection and Deserialization

- Shell out last. Use a library call first. Otherwise pass argv as an array with no shell: Node `execFile`, Python `subprocess.run([...])` without `shell=True`, Java `ProcessBuilder(cmd, arg)`. Escaping alone is not a defense: argument injection still works.
- Put `--` before user-supplied args (`curl -- "$url"`) so a value like `-o` is not read as an option. Allowlist the command and regex-allowlist each argument.
- LDAP: escape DN values and filter values separately. Filter escapes: `\ * ( )` and NUL. Use a library encoder. Bind with a least-privilege account, never anonymously.
- XSS: encode at the point of output for its context (HTML body, quoted attribute, JS, CSS, URL) with the template engine's autoescape. Never build HTML by string concat. Always quote attribute values. Percent-encode URL parameter values only, never a whole URL. Never put user data in `on*` handler attributes: HTML encoding does not protect the JavaScript inside. Input filters do not replace output encoding.
- Prototype pollution: no unsafe deep-merge. Block keys `__proto__`, `constructor`, `prototype`. Use `Map`, `Set`, or `Object.create(null)` for dictionaries keyed by user input.
- Never deserialize untrusted data with `pickle.loads`, `yaml.load` (use `yaml.safe_load`), PHP `unserialize`, .NET `BinaryFormatter`, or Java `ObjectInputStream` without a class allowlist. Keep Jackson default typing and fastjson autotype off. Set JSON.NET `TypeNameHandling.None`. Prefer plain JSON plus schema validation. Verify the signature before deserializing signed data.
- XML: disable DTDs on every parser (Java `disallow-doctype-decl`, .NET `DtdProcessing.Prohibit`, Python `defusedxml`, no `XML_PARSE_NOENT` or `XML_PARSE_DTDLOAD` in libxml2). Never use `java.beans.XMLDecoder` on untrusted input. Cap entity expansion, depth, and payload size.

## Web and API Hardening

### Headers and cookies

- Send CSP as an HTTP header, not `<meta>`. Start in `Content-Security-Policy-Report-Only`, then enforce. Prefer a per-request nonce (CSPRNG, at least 128 bits, base64) with `'strict-dynamic'` over domain allowlists. Always set `object-src 'none'`, `base-uri 'none'`, and `frame-ancestors`. No `'unsafe-inline'` or `'unsafe-eval'` in `script-src`.
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`. Roll out with `max-age=86400` first. Add `includeSubDomains` only when every subdomain serves HTTPS. Add `preload` only after a stable year: removal takes months. Never send HSTS over plain HTTP.
- Also set `X-Content-Type-Options: nosniff`, `Cross-Origin-Opener-Policy: same-origin`, and `Cross-Origin-Resource-Policy: same-site` (`same-origin` when no sibling subdomain loads the resource). Send `Cache-Control: no-store` on sensitive responses. Strip `X-Powered-By`, versioned `Server`, and `X-AspNet-Version`. Do not rely on `X-XSS-Protection`.
- Never change state on `GET`. Check the CSRF token on every `POST`, `PUT`, `PATCH`, `DELETE`, including the login form. XSS defeats every CSRF control. Session cookie flags, `__Host-`, and CSRF design: [auth.md](auth.md).

### Redirects and SSRF

- Never redirect to a raw `returnUrl` or `url` parameter. Allow local paths only: starts with `/`, not `//` or `/\`, no scheme. Otherwise map a server-side token to the URL.
- Check external targets with a URL parser against an exact-host allowlist. No wildcard domains. No substring or `startsWith` checks. Show an interstitial for external hops. PHP: `exit` after `header("Location: ...")`.
- SSRF: accept an IP or domain, not a full URL. Disable redirects in the outbound client. Allow `http` and `https` only (block `file://`, `gopher://`, `dict://`, `phar://`). Fixed partners: exact allowlist. Arbitrary targets: resolve, verify every returned IP is public (not private, loopback, or link-local `169.254.0.0/16`), then connect to the verified IP. Add an egress firewall. On AWS, require IMDSv2 and disable IMDSv1.

### File uploads

- Allowlist extensions after decoding the filename. Check magic bytes and MIME. Never trust the client `Content-Type`. Reject double extensions (`.jpg.php`) and null bytes (`.php%00.jpg`).
- Store under a server-generated UUID name, outside the webroot, served by a handler that maps ID to file. Re-encode images. Cap size, and cap size after decompression for archives (zip bombs). Block `.htaccess`, `.htpasswd`, `crossdomain.xml`, `clientaccesspolicy.xml`.
- Upload endpoints need authentication and CSRF protection.

### API surface

- Never put tokens, keys, or passwords in URL query strings.
- Never copy the request `Accept` header into the response `Content-Type`.
- Return `405` for a disallowed method, `406` for unsupported `Accept`, `413` for oversize bodies, `415` for unsupported `Content-Type`, `429` on rate limit, and a generic `500`.
- CORS is not authorization. Enforce access control at every endpoint.
- Mint a separate internal identity for service-to-service calls. Never forward the external user token.
- Keep admin and management endpoints off the public internet. Require MFA if they must be reachable.

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

- Gitignore `.env*`. Commit `.env.example` with placeholders. Run secret scanning (gitleaks, trufflehog) in CI.
- Rotate a leaked secret. Deleting it from the repo or history does not revoke it.

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
