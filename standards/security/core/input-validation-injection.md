---
description: Input validation and injection defense — SQL/SOQL/LDAP/OS, parameterization, prototype pollution
alwaysApply: false
---

# Input Validation & Injection Defense

## NEVER
- Concatenate user input into SQL, SOQL, LDAP filters, OS commands, or shell strings
- Trust client-supplied identifiers, types, or sizes — re-validate server-side
- Invoke a shell to run an OS command when a structured API exists
- Use deny-list validation where allow-list applies
- Validate before canonicalization (Unicode/URL/percent-encoding) — bypasses are trivial
- Rely on string escaping as the primary SQL defense; parameterize
- Use unsafe deep-merge utilities on JS objects; merge into `__proto__`, `constructor`, or `prototype`
- Run regexes on free-form input without protecting against ReDoS

## ALWAYS
- Validate at trust boundaries with positive (allow-list) checks and canonicalization
- Treat all untrusted input as data, never as code — use APIs that separate the two
- Parameterize queries/commands; if escaping is unavoidable, use a context-specific encoder
- Anchor regexes (`^…$`) and validate the complete string
- Validate files by content (magic bytes), size, and safe extension (see `file-handling-and-uploads`)

## Validation playbook
- **Syntactic:** type, format, range, length per field
- **Semantic:** business rules (e.g., start ≤ end date, enum allow-list)
- **Normalization:** canonicalize encodings *before* validation
- **Free-form text:** define character class allow-list; normalize Unicode; cap length
- **Identifiers:** validate against an allow-list, never accept dynamic SQL/SOQL identifiers from clients

## SQL injection
- Prepared statements / parameterized queries for 100% of data access
- Bind variables inside stored procedures; no concatenation in PL/SQL or T-SQL
- Least-privilege DB users and views; never grant admin to app accounts

```java
String q = "SELECT account_balance FROM user_data WHERE user_name = ?";
PreparedStatement ps = conn.prepareStatement(q);
ps.setString(1, custname);
ResultSet rs = ps.executeQuery();
```

## SOQL / SOSL (Salesforce)
- Primary risk is data exfiltration (no DDL/DML in SOQL); secondary risk is mass-DML if results feed DML
- Prefer static SOQL/SOSL with binds: `[SELECT Id FROM Account WHERE Name = :input]`, `FIND :term`
- Dynamic SOQL: `Database.queryWithBinds()`; dynamic SOSL: `Search.query()`; allow-list any dynamic identifier; if concatenation is unavoidable, use `String.escapeSingleQuotes()`
- Enforce CRUD/FLS with `WITH USER_MODE` or `WITH SECURITY_ENFORCED` (not both)
- Enforce sharing with `with sharing` or user-mode operations; `Security.stripInaccessible()` before DML

## LDAP injection
- DN escape: `\ # + < > , ; " =` and leading/trailing spaces
- Filter escape: `* ( ) \ NUL`
- Validate input via allow-list before constructing queries; use libraries that provide DN/filter encoders
- Use bind authentication on least-privilege LDAP connections; avoid anonymous binds

## OS command injection
- Prefer in-process APIs over shelling out
- If unavoidable: structured execution that separates command and args (e.g., `ProcessBuilder`); never invoke a shell
- Allow-list the command; validate arguments against an allow-list regex
- Exclude metacharacters: `& | ; $ > < \` `` ` `` ` ! ' " ( )` and whitespace as needed
- Use `--` to terminate option parsing where supported

```java
ProcessBuilder pb = new ProcessBuilder("TrustedCmd", "Arg1", "Arg2");
pb.directory(new File("TrustedDir"));
Process p = pb.start();
```

## Prototype pollution (JavaScript)
- Prefer `new Set()` / `new Map()` over object literals when used as dictionaries
- If you need an object, use `Object.create(null)` or `{ __proto__: null }`
- Freeze/seal objects that should be immutable; consider Node `--disable-proto=delete` as defense-in-depth
- Validate keys against an allow-list; block `__proto__`, `constructor`, `prototype`
- Avoid unsafe deep-merge utilities

## Caching & transport
- `Cache-Control: no-store` on responses containing sensitive data
- Enforce HTTPS across all data flows

## Checklist
- [ ] Central validators with type, range, length, enum, canonicalization
- [ ] 100% parameterization for SQL; dynamic identifiers via allow-list only
- [ ] LDAP DN/filter escaping in use; inputs validated before query
- [ ] No shell invocation for untrusted input; structured exec + allow-list + regex validation
- [ ] JS object graph hardened: safe constructors, blocked prototype paths, safe merge
- [ ] Static checks for query/command concatenation; fuzzing for SQL/LDAP/OS vectors
