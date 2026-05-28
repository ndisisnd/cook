---
description: C/C++ memory and string safety — banned functions, bounds-checked replacements, compiler/linker hardening, build configurations
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
- Hardcoded buffer sizes that may change at a callsite
- `DEBUG` macro in release builds, or `NDEBUG` in debug builds
- Mixed sanitizer flags across different builds (memory sanitizer must be isolated)
- Shipping release builds without stack protection, PIE, RELRO, and NX flags
- Skipping binary verification after build — trust that flags were applied without checking

## ALWAYS use
- Bounded / formatting alternatives from the replacement table below
- Check every `errno_t` return value
- Pass buffer size explicitly when a function receives a `char *`
- Compute destination size with `sizeof(array)` only for true arrays, never for parameters or heap pointers
- `assert()` for pre/post-conditions and invariants — disabled automatically when `NDEBUG` is set
- Enable `-Wall -Wextra -Wconversion` and treat warnings as bugs
- Verify hardening flags on the final binary (`checksec` on Linux, BinScope on Windows)
- Enforce hardening flags in CMake/CI and fail the build if verification fails
- Audit third-party libraries regularly with OWASP Dependency-Check or equivalent

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

| Category | GCC/Clang flag | Purpose |
| -------- | -------------- | ------- |
| Warnings | `-Wall -Wextra -Wconversion -Wformat -Wformat-security` | Catch unsafe patterns at compile time |
| Stack protection | `-fstack-protector-all` | Canary detects stack overflows |
| PIE (compiler) | `-fPIE` (Linux/Win), `-fpie` (macOS) | Enables ASLR |
| PIE (linker) | `-pie` | ASLR at runtime |
| Fortify | `-D_FORTIFY_SOURCE=2` (requires `-O1`+) | Bounds checks on libc functions |
| CFI (Clang) | `-fsanitize=cfi` (requires `-flto`) | Guards against ROP/JOP |
| RELRO | `-Wl,-z,relro,-z,now` | Makes GOT read-only post-link |
| NX stack | `-Wl,-z,noexecstack` | Prevents stack execution |
| NX heap (Linux) | `-Wl,-z,noexecheap` | Prevents heap execution |
| Windows | `/NXCOMPAT /DYNAMICBASE` | DEP + ASLR support |

## Build configurations

| Mode | Compiler flags | Macros | Sanitizers |
| ---- | -------------- | ------ | ---------- |
| Debug | `-O0 -g3` | `-DDEBUG` (no `NDEBUG`) | `-fsanitize=address,undefined,leak`; separate build for `-fsanitize=memory` |
| Release | `-O2` + all hardening flags | `-DNDEBUG` (no `DEBUG`) | None |

## Checklist
- [ ] No banned memory/string functions in the codebase
- [ ] All bounded operations use `*_s()` variants with proper size parameters
- [ ] Every `errno_t` return value checked
- [ ] `sizeof()` used only on true arrays; size parameters passed for pointers
- [ ] Strings explicitly null-terminated after bounded copies
- [ ] All hardening compiler and linker flags active in release config
- [ ] `NDEBUG` defined in release; `DEBUG` defined in debug only
- [ ] Address, UB, and leak sanitizers enabled in debug builds
- [ ] Memory sanitizer in isolated build (not combined with other sanitizers)
- [ ] `checksec` (Linux) or BinScope (Windows) run in CI; build fails on missing flags
- [ ] Third-party library vulnerabilities audited in CI pipeline
- [ ] Static analysis + pre-commit hooks scan for banned functions
