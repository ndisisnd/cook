---
description: OS command injection defense — avoid shell invocation and validate/parameterize when unavoidable
alwaysApply: false
---

# OS Command Injection Defense

## NEVER
- Construct shell commands by string-concatenating user input
- Pass user-controlled data to `exec`, `system`, `shell_exec`, `passthru`, `popen`
- Rely on simple escaping as the sole defense (argument injection still possible)
- Pass user input as arguments to a command without allowlist validation

## ALWAYS
- Use built-in library functions instead of shell commands when equivalent exists (e.g. `mkdir()` not `system("mkdir …")`)
- When OS commands are unavoidable, use parameterized execution — pass command and args as separate array items (never a single shell string)
- Validate all arguments against a strict allowlist before use
- Use language-specific escaping as an additional layer only (not the primary defense)
- Apply the `--` POSIX delimiter to prevent argument injection: `curl -- $url`
- Run the process with minimum required OS privileges

## Defense Options (in priority order)

| Option | Approach |
|--------|----------|
| 1 — Avoid | Replace shell call with library equivalent |
| 2 — Parameterize | Separate command + args array; no shell interpolation |
| 3 — Validate + escape | Allowlist args + language escaping (e.g. `escapeshellarg()`) |

## Java — parameterized example

```java
// WRONG: single string passed to shell
new ProcessBuilder("C:\\DoStuff.exe -arg1 -arg2");

// RIGHT: command and args separated
new ProcessBuilder("TrustedCmd", "TrustedArg1", "TrustedArg2").start();
```

## Dangerous metacharacters to strip/reject
`& | ; $ > < ` \ ! ' " ( )`

## Allowlist regex example
`^[a-z0-9]{3,10}$` — restrict to alphanumeric, bounded length

## Checklist
- [ ] All OS command calls replaced with library equivalents where possible
- [ ] Remaining calls use parameterized array form (no shell string interpolation)
- [ ] All user-supplied arguments validated against allowlist regex
- [ ] Language escaping (`escapeshellarg` / equivalent) applied as secondary layer
- [ ] `--` delimiter used where applicable
- [ ] Process runs with least-privilege OS account
