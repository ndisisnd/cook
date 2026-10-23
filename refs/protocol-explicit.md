# Cook Protocol — Explicit mode

Read only when `/cook` was invoked with flags and/or prose. The flags go to
`cook_run.py --flag` (core protocol "Run"). Explicit args are the
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
python3 scripts/cook_run.py --project <dir> [--flag <name> ...] [--prose <text>]
```

Pass each flag without its dashes. `cook_run.py` validates them, applies the
path-list rules below, compiles and returns the envelope (see
[`protocol-cook.md`](protocol-cook.md)).

- **Flags only** (`explicit-flags`): cacheable. A `hit` returns the stored
  payload with no compile.
- **Any prose** (`explicit-prose`): `status: "skip"` — prose is uncacheable
  (the ref selection has no deterministic key). Nothing is written to the cache.
- Prose without flags: the script classifies the prose; `needs_llm` and
  `--resume` work as in the core protocol.

The multi-call flow (`lookup`, `write`, `compile`) is in
[`protocol-manual.md`](protocol-manual.md).

## Path list

- `--global` → `standards/global/SKILL.md` + every `standards/global/refs/*.md`
  — the complete global shelf, and the only explicit-mode opt-in to P0.
- **Concern flag** (`--security`, `--auth`, `--crypto`, `--performance`, `--architecture`,
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
- **Prose without flags** → the script classifies the prose. Each
  `concern:<name>` route loads `standards/global/refs/<name>.md`; each
  `domain:<name>` route loads that domain's `SKILL.md` plus the refs its
  `_INDEX.md` matches against the prose. Only when `needs_llm: true` (nothing
  resolved): canonicalise the tags and `--resume`. Never invent paths.

The script applies these rules; you do not build the path list yourself.
