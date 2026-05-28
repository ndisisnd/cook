---
description: C/C++ toolchain hardening — compiler/linker flags, build configs, and binary verification
alwaysApply: false
---

# C/C++ Toolchain Hardening

## NEVER
- Ship release builds without stack protection, PIE, RELRO, and NX flags
- Define `DEBUG` macro in release builds or `NDEBUG` in debug builds
- Mix sanitizer flags across different builds (memory sanitizer must be isolated)
- Skip binary verification after build — trust flags were applied without checking

## ALWAYS
- Enable `-Wall -Wextra -Wconversion` and treat warnings as bugs
- Add all hardening flags to release build config (compiler and linker)
- Define `NDEBUG` in release; define `DEBUG` and enable sanitizers in debug
- Use `assert()` for pre/post-conditions and invariants — disabled automatically when `NDEBUG` is set
- Verify hardening flags on the final binary (`checksec` on Linux, BinScope on Windows)
- Enforce hardening flags in CMake/CI and fail the build if verification fails
- Audit third-party libraries regularly with OWASP Dependency-Check or equivalent

## Hardening flags

| Category | GCC/Clang flag | Purpose |
|---|---|---|
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
| Mode | Flags | Macros | Sanitizers |
|---|---|---|---|
| Debug | `-O0 -g3` | `-DDEBUG` (no `NDEBUG`) | `-fsanitize=address,undefined,leak`; separate build for `-fsanitize=memory` |
| Release | `-O2` + all hardening flags | `-DNDEBUG` (no `DEBUG`) | None |

## Checklist
- [ ] All hardening compiler and linker flags active in release config
- [ ] `NDEBUG` defined in release; `DEBUG` defined in debug only
- [ ] Address, UB, and leak sanitizers enabled in debug builds
- [ ] Memory sanitizer in isolated build (not combined with other sanitizers)
- [ ] `checksec` (Linux) or BinScope (Windows) run in CI; build fails on missing flags
- [ ] Third-party library vulnerabilities audited in CI pipeline
