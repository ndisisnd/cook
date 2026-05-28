---
description: Replace unsafe C/C++ string and memory functions with bounds-checked alternatives to prevent buffer overflows
alwaysApply: false
---

# Safe C/C++ Functions

Flag every unsafe function on sight; replace with the safe alternative below.

## NEVER
- `gets()` — no bounds checking at all (critical; always replace)
- `strcpy()` — copies until null, no bounds check (high risk)
- `strcat()` — appends with no bounds check (high risk)
- `sprintf()` / `vsprintf()` — no output buffer bounds check (high risk)
- `scanf("%s", buf)` without width specifier — unbounded read (medium risk)
- `strtok()` in multi-threaded code — uses static buffer, not reentrant (medium risk)

## ALWAYS
- Default to `snprintf()` for string formatting and concatenation
- Default to `fgets()` for reading string input
- Use `strtok_r()` (POSIX) or `strtok_s()` (C11) in place of `strtok()`
- Validate size arguments before `memcpy`/`memmove`; prefer `memcpy_s()` when available
- Use `memmove()` when source and destination buffers may overlap
- Enable compiler flags: `-fstack-protector-all`, `-D_FORTIFY_SOURCE=2`, `-Wformat -Wformat-security`
- Use `-fsanitize=address` during development to catch memory errors

## Replacement Table

| Unsafe | Safe alternative |
| ------ | ---------------- |
| `gets(buf)` | `fgets(buf, sizeof(buf), stdin)` |
| `strcpy(dst, src)` | `snprintf(dst, sizeof(dst), "%s", src)` |
| `strcat(dst, src)` | `snprintf(dst, sizeof(dst), "%s%s", dst, src)` |
| `sprintf(buf, fmt, ...)` | `snprintf(buf, sizeof(buf), fmt, ...)` |
| `scanf("%s", buf)` | `fgets(buf, sizeof(buf), stdin)` then `sscanf` |
| `strtok(s, delim)` | `strtok_r(s, delim, &saveptr)` |
| `memcpy` (unchecked) | `memcpy_s(dst, dstsize, src, count)` |

## strncpy Null-Termination Fix

```c
char dest[10];
strncpy(dest, source, sizeof(dest) - 1);
dest[sizeof(dest) - 1] = '\0';   // strncpy does not guarantee termination
```

## Checklist
- [ ] No `gets()`, `strcpy()`, `strcat()`, `sprintf()` in new or reviewed code
- [ ] All string formatting uses `snprintf()` with explicit buffer size
- [ ] All user input reads use `fgets()` with size limit
- [ ] `strtok()` replaced with `strtok_r()` / `strtok_s()` in threaded code
- [ ] `memcpy`/`memmove` size arguments validated
- [ ] Compiler flags `-fstack-protector-all` and `-D_FORTIFY_SOURCE=2` enabled
- [ ] AddressSanitizer (`-fsanitize=address`) used in development builds
