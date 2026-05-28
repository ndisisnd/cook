---
description: C memory and string safety — ban unsafe functions and enforce bounds-checked replacements
alwaysApply: false
---

# Memory and String Safety Guidelines (C)

## NEVER
- Use unsafe memory functions: `memcpy`, `memset`, `memmove`, `memcmp`, `bzero`, `memzero`
- Use unsafe string functions: `strcpy`, `strcat`, `strcmp`, `strlen`, `sprintf`, `strstr`, `strtok`
- Pass `sizeof(pointer)` as a buffer size — always pass the actual buffer size
- Ignore `errno_t` return values from `*_s()` functions
- Use hardcoded buffer sizes that may change at a callsite

## ALWAYS
- Replace all unsafe functions with their `*_s()` bounds-checked variants
- Pass the destination buffer size (not source size) to `*_s()` functions
- Check every `errno_t` return value and handle errors explicitly
- Pass buffer sizes as explicit parameters when operating on pointer arguments
- Enable compiler warnings for unsafe function usage and treat them as errors
- Use static analysis and pre-commit hooks to catch banned function calls

## Function Replacements

| Banned | Safe Replacement |
|--------|-----------------|
| `memcpy(d,s,n)` | `memcpy_s(d, d_size, s, n)` |
| `memset(d,v,n)` | `memset_s(d, d_size, v, n)` |
| `memmove(d,s,n)` | `memmove_s(d, d_size, s, n)` |
| `memcmp(s1,s2,n)` | `memcmp_s(s1, s1max, s2, s2max, n, &indicator)` |
| `bzero(d,n)` | `memset_s(d, d_size, 0, n)` |
| `strcpy(d,s)` | `strcpy_s(d, d_size, s)` |
| `strcat(d,s)` | `strcat_s(d, d_size, s)` |
| `strcmp(s1,s2)` | `strcmp_s(s1, s1max, s2, &indicator)` |
| `strlen(s)` | `strnlen_s(s, max_size)` |
| `sprintf(s,fmt,...)` | `snprintf(s, n, fmt, ...)` |
| `strstr(d,s)` | `strstr_s(d, dmax, s, slen, &substr)` |
| `strtok(s,d)` | `strtok_s(s, &smax, d, &next)` |

## Common Pitfalls

```c
// WRONG: source size, not destination size
strcpy_s(dest, strlen(src), src);

// CORRECT: destination buffer size
strcpy_s(dest, sizeof(dest), src);

// WRONG: sizeof(pointer) — equals 8, not buffer size
void func(char *buf) { strcpy_s(buf, sizeof(buf), src); }

// CORRECT: pass size explicitly
void func(char *buf, size_t buf_size) { strcpy_s(buf, buf_size, src); }
```

## Checklist
- [ ] No unsafe memory functions (`memcpy`, `memset`, `memmove`, `memcmp`, `bzero`)
- [ ] No unsafe string functions (`strcpy`, `strcat`, `strcmp`, `strlen`, `sprintf`, `strstr`, `strtok`)
- [ ] All `*_s()` calls use destination buffer size, not source size
- [ ] All `errno_t` return values checked and errors handled
- [ ] No `sizeof(pointer)` passed as buffer size
- [ ] Static analysis / compiler warnings for unsafe functions enabled
- [ ] Pre-commit hook scanning for banned functions configured
