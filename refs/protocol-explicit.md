# Cook Protocol — Explicit mode

Read only when `/cook` was invoked with flags and/or prose. Replaces core
Steps 1–5; the compile step (core Step 6) is shared. Explicit args are the
whole load surface: **no automatic P0, no auto-matching, and `fallback` is
suppressed** — signals are still recorded on the entry for diagnostics, but
the user's args decide what loads.

## Parse args

- Tokens beginning with `--` are flags:
  - **Simple** (`--security`, `--react`, `--global`) — validated against the
    runtime flag set derived from `vocab/tag-vocabulary.json` `routes_to`.
    Unknown flag → non-zero exit with the valid flag list.
  - **Sub-ref** (`--react:hooks`) — `--<domain>:<ref>`, where `ref` is a file
    stem under `standards/<domain>/refs/`.
- A bare `--` token terminates flag parsing (Unix convention): everything
  after it is prose, even if dash-prefixed.
- All remaining text is the **prose** argument (whitespace-trimmed). Flag
  order is free: `/cook fix bug --react` ≡ `/cook --react fix bug`.

## Resolver call

```
python3 scripts/cook_cache.py lookup --project <dir> \
  [--flag <name> ...] [--prose <text>]
```

- **Flags only** (`explicit-flags`): normal hit/miss lookup with the flags
  folded into the fingerprint. On `hit`, use `routing.skills` and go to
  compile. On `miss`, build the path list below, then persist with the core
  Step 5 `write` command (add `--flag <name>` per flag; `--mode` defaults to
  `explicit-flags`), then compile.
- **Any prose** (`explicit-prose`): the resolver returns `status: "skip"` —
  prose is uncacheable (the LLM's ref selection has no deterministic key).
  Build the path list, skip the cache write entirely, and compile.

## Path list

- `--global` → `standards/global/SKILL.md` + every `standards/global/refs/*.md`
  — the complete global shelf, and the only explicit-mode opt-in to P0.
- **Concern flag** (`--security`, `--auth`, `--performance`, `--architecture`,
  `--api-design`, `--error-handling`, `--debug`, `--cicd`) →
  `standards/global/refs/<concern>.md` only (no P0 SKILL.md).
- **Bare domain flag** (`--<domain>`) → `standards/<domain>/SKILL.md` **always**
  loads; which refs load beside it depends on what else names that same domain:
  - **Alone** — no prose and no `--<domain>:<ref>` for it → every
    `standards/<domain>/refs/*.md` (the **full shelf**).
  - **+ one or more `--<domain>:<ref>` for the SAME domain** → the SKILL.md floor
    **plus only the named refs**; the full shelf is **suppressed** (the other
    `refs/*.md` do NOT load). The sub-ref flags select a subset on top of the
    floor. Worked example:
    `--macos --macos:architecture-and-state --macos:distribution` →
    `standards/macos/SKILL.md`
    + `standards/macos/refs/architecture-and-state.md`
    + `standards/macos/refs/distribution.md`, and **nothing else** — none of the
    other `standards/macos/refs/*.md` load.
  - **+ prose** (and no sub-ref for it) → the SKILL.md floor plus the refs the
    domain's `_INDEX.md` keyword table matches against the prose. Zero matched
    refs still loads the SKILL.md — the flag guarantees the shelf entry. (If
    both prose and `--<domain>:<ref>` name the same domain, load the SKILL.md
    plus the **union** of the named refs and the prose-matched refs — both are
    explicit selections, and the full shelf stays suppressed.)
- **Sub-ref flag alone** (`--react:hooks` with NO bare `--react` present) →
  `standards/<domain>/refs/<ref>.md` only; the domain SKILL.md does **NOT** load.
  Pair it with the bare domain flag to add the SKILL.md floor:
  `--react --react:hooks` → `standards/react/SKILL.md`
  + `standards/react/refs/hooks.md` only — floor + that one ref, **not** the
  full shelf.
- **Prose without flags** → run
  `python3 scripts/cook_cache.py classify --prose <text>` first. Each
  `concern:<name>` route loads `standards/global/refs/<name>.md`; each
  `domain:<name>` route loads that domain's `SKILL.md` plus the refs its
  `_INDEX.md` matches against the prose. Only when `needs_llm: true` (nothing
  resolved): scan the domain `_INDEX.md` files yourself and load what matches.
  Never invent paths.

Then go to core Step 6 (compile and return).
