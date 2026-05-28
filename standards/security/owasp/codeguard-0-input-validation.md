---
description: Input validation strategy — allowlists, type checks, file uploads, email, regex safety
alwaysApply: false
---

# Input Validation

Input validation is not the primary defence against XSS or SQLi — it reduces impact but must be paired with output encoding and parameterised queries.

## NEVER
- Trust client-side validation alone — always re-validate server-side
- Use denylists as the primary validation strategy — use allowlists
- Use partial-match regex (without `^...$` anchors) for structured fields
- Write regex with catastrophic backtracking potential (ReDoS)
- Accept file paths or names from client input — server defines all paths
- Store uploaded files under their original extension or client-supplied name

## ALWAYS
- Validate all input as early as possible in the data flow
- Apply allowlist validation: define permitted character sets, length, and format
- Validate both syntax (format) and semantics (business-rule correctness)
- Perform server-side validation before any data reaches the database or downstream components
- Canonicalize/normalize Unicode text before validating
- Enforce maximum file size and validate extension against expected types
- Check ZIP files before extraction: target path, compression ratio, estimated size

## Validation Strategies

| Type | Approach |
| ---- | -------- |
| Structured fields (SSN, date, ZIP) | Strict allowlist regex anchored `^...$` |
| Fixed options (dropdowns) | Exact match against server-side allowlist |
| Free-form Unicode | Normalize, then allowlist Unicode categories |
| Numbers | Type-convert with exception handling + range check |
| Strings | Length bounds + character set allowlist |

## File Upload Rules
- Validate filename extension against expected types
- Analyse content (magic bytes / image rewriting) — do not trust MIME type alone
- Use server-generated random filenames for storage
- Scan uploaded files for malicious content before making accessible
- Block dangerous file types: `.htaccess`, `.htpasswd`, `crossdomain.xml`, `clientaccesspolicy.xml`, and web-executable scripts (`.asp`, `.aspx`, `.php`, `.jsp`, `.js`, `.cgi`)

## Email Validation
- Syntactic: two parts split by `@`; no backticks, quotes, or null bytes; domain letters/numbers/hyphens/periods; local ≤ 63 chars; total ≤ 254 chars
- Semantic: send verification email with a token — cryptographically random, ≥ 32 chars, single-use, time-limited

## Checklist
- [ ] All validation implemented server-side, not only client-side
- [ ] Allowlist regex anchored `^...$` with explicit length limits
- [ ] File uploads validated on extension, content type, and size
- [ ] Dangerous upload types blocked and server controls the storage path
- [ ] Unicode input normalized before validation
- [ ] Email tokens cryptographically random, single-use, and time-limited
- [ ] Regex patterns reviewed for ReDoS risk
