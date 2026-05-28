---
description: Prevent SQL, LDAP, OS command, and other injection attacks across all languages
alwaysApply: false
---

# Injection Prevention

## NEVER
- Concatenate user input into SQL, LDAP, or OS command strings
- Use string interpolation to build queries or shell commands
- Pass user input directly to OS command APIs without parameterisation and allowlist validation
- Use denylists as the sole defence — always pair with allowlists

## ALWAYS
- Use parameterised queries / prepared statements for all database access
- Use safe ORMs/ODMs correctly — verify they don't introduce injection under the hood
- Escape user data using the context-specific encoding function when a safe API is unavailable
- Validate inputs with allowlists (permitted characters, length, format) before use
- Separate command from arguments when invoking OS commands (never concatenate into one string)

## SQL Injection Defences (prefer in order)

| Defence | When to use |
| ------- | ----------- |
| Prepared statements / parameterised queries | Default for all DB access |
| Stored procedures (parameterised) | Legacy DB or stored-proc architecture |
| Allowlist input validation | Table/column names that cannot be parameterised |
| Context-aware escaping | Last resort when none of the above is possible |

```java
// Prepared statement — correct
String query = "SELECT account_balance FROM user_data WHERE user_name = ?";
PreparedStatement pstmt = connection.prepareStatement(query);
pstmt.setString(1, custname);
```

## LDAP Injection
- Escape DN values with RFC 2253 encoding before inserting into LDAP queries
- Escape search filter values with RFC 2254 encoding (escape `\`, `*`, `(`, `)`, null byte)

## OS Command Injection
- Pass command and arguments as separate array elements — never as a single concatenated string
- Validate command names against an explicit allowlist
- Validate arguments with allowlist regex — explicitly exclude metacharacters: `& | ; $ > < \` \ !` and whitespace

```java
// Correct — args separated
ProcessBuilder pb = new ProcessBuilder("TrustedCmd", "TrustedArg1", "TrustedArg2");
// Wrong — concatenated string
// new ProcessBuilder("C:\\DoStuff.exe -arg1 -arg2");
```

## Checklist
- [ ] All database queries use parameterised statements or safe ORM
- [ ] No user input concatenated into SQL, LDAP, or shell strings
- [ ] OS commands use array-form with allowlisted command and arguments
- [ ] LDAP DN and filter values escaped with correct RFC encoding
- [ ] Allowlist input validation applied before data reaches any interpreter
- [ ] Denylists not used as the sole injection defence
