---
description: C/C++ memory and string safety — banned functions, bounded alternatives, compiler hardening
alwaysApply: false
---

# Safe C / C++ Functions

## NEVER use
- `gets()` — no bounds check; classic buffer overflow
- `strcpy()`, `strcat()`, `sprintf()`, `vsprintf()` — no destination bounds
- `scanf("%s", ...)` without a width specifier — unbounded write
- `strtok()` — not reentrant; static internal buffer
- `memcpy()`, `memset()`, `memmove()`, `memcmp()`, `bzero()`, `memzero()` — no boundary checking
- `strstr()`, `strcmp()`, `strlen()` — when bounded variants are available in a C11 Annex K environment
- `sizeof(pointer)` to compute buffer size — yields the pointer size (8), not the buffer

## ALWAYS use
- Bounded / formatting alternatives below
- Check every `errno_t` return value
- Pass buffer size explicitly when a function receives a `char *`
- Compute destination size with `sizeof(array)` only for true arrays, never for parameters or heap pointers

## Replacement table

| Banned | Risk | Replacement |
| ------ | ---- | ----------- |
| `gets()` | unbounded read | `fgets(buf, n, stream)` |
| `strcpy()` | unbounded copy | `snprintf()` or `strcpy_s()` (C11 Annex K) |
| `strcat()` | unbounded append | `snprintf()` or `strcat_s()` |
| `sprintf()` / `vsprintf()` | unbounded format | `snprintf()` / `vsnprintf()` |
| `scanf("%s", ...)` | unbounded read | `fgets()` + `sscanf()`, or width-bounded `scanf("%127s", buf)` |
| `strtok()` | non-reentrant | `strtok_r()` (POSIX) or `strtok_s()` |
| `memcpy()` | no bounds | `memcpy_s(dest, dest_size, src, count)` |
| `memset()` | no bounds | `memset_s()` |
| `memmove()` | no bounds | `memmove_s()` (use when buffers may overlap) |
| `memcmp()` | no bounds | `memcmp_s()` |
| `bzero()` / `memzero()` | no bounds | `memset_s()` |
| `strstr()` | no bounds | `strstr_s()` |
| `strcmp()` | no bounds | `strcmp_s()` |
| `strlen()` | no bounds | `strnlen_s(str, max)` |

## Safe patterns

```c
// String copy
char dest[256];
if (strcpy_s(dest, sizeof(dest), src) != 0) {
    EWLC_LOG_ERROR("strcpy_s failed");
    return ERROR;
}

// String concatenation
char buffer[256] = "prefix_";
if (strcat_s(buffer, sizeof(buffer), suffix) != 0) return ERROR;

// Memory copy
if (memcpy_s(dest, dest_max, src, size) != 0) return ERROR;

// Tokenization
char *next = NULL;
rsize_t smax = strnlen_s(str, MAX_STRING_SIZE);
for (char *t = strtok_s(str, &smax, delim, &next); t; t = strtok_s(NULL, &smax, delim, &next)) { /* process */ }

// strncpy fallback (when Annex K unavailable) — always explicitly null-terminate
strncpy(dest, src, sizeof(dest) - 1);
dest[sizeof(dest) - 1] = '\0';
```

## Pitfalls to flag

| Pitfall | Wrong | Right |
| ------- | ----- | ----- |
| Source-size as destination bound | `strcpy_s(dest, strlen(src), src)` | `strcpy_s(dest, sizeof(dest), src)` |
| Ignoring return values | `strcpy_s(dest, sizeof(dest), src);` | `if (strcpy_s(...) != 0) handle_error();` |
| `sizeof` on a pointer parameter | `void f(char *b) { strcpy_s(b, sizeof(b), src); }` | `void f(char *b, size_t bsz) { strcpy_s(b, bsz, src); }` |

## Compiler & linker hardening
- `-Wall -Wextra -Wconversion -Wformat -Wformat-security`
- `-fstack-protector-all` or `-fstack-protector-strong`
- `-D_FORTIFY_SOURCE=2`
- `-fPIE -pie` (ASLR)
- `-fsanitize=address` in development (catch use-after-free, OOB)
- Linker: full RELRO (`-Wl,-z,relro,-z,now`), noexecstack, NX/DEP
- Verify with `checksec` in CI; fail builds missing protections

## Checklist
- [ ] No banned memory/string functions in the codebase
- [ ] All bounded operations use `*_s()` variants with proper size parameters
- [ ] Every `errno_t` return value checked
- [ ] `sizeof()` used only on true arrays; size parameters passed for pointers
- [ ] Strings explicitly null-terminated after bounded copies
- [ ] Hardening flags enabled; verified via `checksec` in CI; ASan/UBSan on debug builds
- [ ] Static analysis + pre-commit hooks scan for banned functions
