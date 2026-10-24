# Cook Protocol — Manual (step by step)

Fallback for Codex and for humans. Claude Code runs [`scripts/cook_run.py`](../scripts/cook_run.py)
instead (see [`protocol-cook.md`](protocol-cook.md)): one script call does
Steps 1–6 below. Use this file when the model cannot run `cook_run.py` or when
you want to run, check or debug each stage by hand. Every subcommand used
below still works on its own. The skill list that `cook_run.py` derives follows
the same rules as Steps 3–5 and the explicit path list; it lives in
`scripts/cook_route.py`. To see why a file loaded without running the stages
by hand, add `--explain` to `cook_run.py`.

Operational protocol for the `cook` orchestrator. `SKILL.md` is the thin entry
point; follow this file exactly. Handle Step 0 (telemetry management flags)
first. Then, if the invocation carries **any** remaining args (flags and/or
prose), read [`protocol-explicit.md`](protocol-explicit.md) instead of Steps
1–5 — the compile step (Step 6) is shared.

### Step 0 — Telemetry management flags (intercept first)

If the invocation carries a telemetry management flag — `--init`,
`--enable-telemetry`, `--disable-telemetry`, or `--status` — read
[`telemetry.md`](telemetry.md) and follow it. When such a flag is the whole
invocation, run the matching command, print its output, and terminate (do not
proceed to Step 1). Otherwise strip the flag, run its command, then continue
below with the remaining args. Telemetry is opt-in and off by default; the
optional record step at the end of Step 6 is also defined in `telemetry.md`.

`--init` initialises a **local** telemetry store for the current repository so
its cook calls record there instead of the global install store. Always pass the
project directory (`--project <dir>`, the same one used for the resolver) to
every telemetry call so local/global scope resolves correctly.

| Mode | Condition | P0 loaded? | Cache? | Path |
|---|---|---|---|---|
| `auto` | no args | yes (unconditional) | yes | Steps 1–6 below |
| `explicit-flags` | flags only | no | yes | `protocol-explicit.md` → Step 6 |
| `explicit-prose` | any prose (± flags) | no | no | `protocol-explicit.md` → Step 6 |

### Step 1 — Resolve (mechanical, cache-first)

```
python3 scripts/cook_cache.py lookup [--path <file> ...] [--project <dir>]
```

The resolver derives the file surface (explicit paths → git → manifest),
builds a fingerprint from raw observable signals only, and checks the cache.
Stdout is JSON: `status`, `fingerprint`, `signals` (`files`, `extensions`,
`frameworks`, `domain_hints`, `source`), `confidence`, `fallback`, `routing`, `compile_needed`. A `hit` that stores a
finished payload also carries `payload` (`path`, `bytes`, `sections`,
`degraded`, `metadata`). A `stale` result carries `stale_reason`.
Non-zero exit or unparseable stdout → treat as `miss` with `confidence: low`
and empty signals; never reuse output from a failed run.

Branch on `status`:

- **`hit`** — routing is cached and fresh. No classification, no re-match.
  - `compile_needed: false` — the finished payload is verified on disk. Skip
    compile and `heal`. Return `payload` (`path`, `sections`, `degraded`) as the
    envelope. Run only the telemetry `record` from Step 6, if telemetry is on.
  - `compile_needed: true` — an older entry with no stored payload. Use
    `routing.skills` and go to Step 6 (compile, then `write --payload`).
- **`miss` | `stale`** — continue to Step 2. A stale payload (source standard
  edited, payload file gone) is rebuilt by the same path.
- **`fallback`** — the cache file exists but is corrupt (`cache_corrupt: true`).
  Degrade to greedy routing: Step 3's P0 + every domain in
  `signals.domain_hints` (each `SKILL.md`) + all 9 concern refs (Step 4's set),
  then compile (Step 6). Standards still apply; only efficiency is lost. Never
  call `write` or `heal` while the cache is corrupt.

### Step 2 — Classify (mechanical first, LLM only as fallback)

```
python3 scripts/cook_cache.py classify [--path <file> ...] [--project <dir>]
```

The script matches signals against `vocab/tag-vocabulary.json` aliases (prose,
extensions, frameworks and whole path segments; never a part of a file name) and
prints `canonical_tags`, `routes`, and `needs_llm`. Only when
`needs_llm: true` (no `domain:*` route resolved): read the vocab yourself and
canonicalize the raw signals onto its tags — never invent a tag; drop and note
any unmappable signal.

`platform_ambiguous: true` means shared Apple vocabulary (SwiftUI, SwiftData,
Keychain, ...) matched with no platform signal. Pick `domain:ios` (UIKit,
iPhone/iPad, `ios/` paths) or `domain:macos` (AppKit, Mac, menu bar) from the
task; if the task does not say, load neither platform shelf.

**Sufficiency (never empty-handed):** ≥1 `domain:*` route → proceed with the
resolver's `confidence`. None resolved, or the resolver said `fallback: true`
→ set `confidence: low`, `fallback: true`, and load broad in Steps 4–5
(all 9 concern refs + the `signals.domain_hints` domains). P0 loads regardless.

### Step 3 — Load global P0 (always)

Load `standards/global/SKILL.md`. It applies to every auto-mode task
regardless of stack, confidence, or cache state — never skipped. (Explicit
mode intentionally omits it; see `protocol-explicit.md`.)

### Step 4 — Match concerns

For each route `concern:<name>`, load `standards/global/refs/<name>.md`. The
full concern set — also the fallback load — is exactly: `architecture.md`,
`api-design.md`, `error-handling.md`, `security.md`, `auth.md`,
`crypto.md`, `performance.md`, `debug.md`, `cicd.md`.

Supabase key-boundary work stacks with security: secret-key / `service_role` /
client-public-env / key-leak language also loads `security.md`; API-key
service-to-service language may also load `auth.md`. The Supabase refs own the
platform-specific key boundary; auth/security own the generic trust boundary.

### Step 5 — Match domains, then persist

For each route `domain:<name>`, load `standards/<name>/SKILL.md`, then use that
domain's `_INDEX.md` to pick which `refs/*.md` match the task. Multiple
domains may match (e.g. Next.js UI + Postgres schema → both shelves).

If the `_INDEX.md` has a `Core refs (auto mode):` line, also load every ref it
names (`hooks` is `refs/hooks.md`; `global/error-handling` is the global concern
ref), whenever the domain routes. They need no keyword.

Persist the decision (miss path only — skip on hit and on the corrupt-cache
fallback). Run it **after** Step 6's compile, so the payload file exists, and
add `--payload` (see Step 6):

```
python3 scripts/cook_cache.py write --fingerprint <fp> \
  --skills <comma-separated skill paths> --tags <comma-separated canonical_tags> \
  --confidence <high|medium|low> [--fallback] \
  --index <comma-separated _INDEX.md paths used>
```

Record the **full** path list, even a file that might fail to read — a read
failure is not a routing failure; Step 6's `heal` reconciles it.

### Step 6 — Compile and return (shared by all modes)

```
python3 scripts/cook_compile.py --skills <comma-separated paths> \
  --out .agent-skills/payload-<fingerprint>.md --manifest
```

`--manifest` also writes `payload-<fingerprint>.json` beside the payload (one
`{header, rel, bucket, byte_start, byte_end}` row per section).
`cook_compile.py slice --payload <file> --section <header|rel>` prints only the
named sections from that manifest (see `payload-reuse.md`).

(Use `payload-prose.md` on the explicit-prose path, which has no fingerprint.)
The compiler deduplicates, buckets (Universal → Domain → Concern), strips
frontmatter, writes the assembled markdown to `--out`, and prints a summary
envelope: `path`, `bytes`, `sections`, `degraded`, `metadata`. If the invoker
supplied a payload cap, pass `--budget <bytes>` — over-budget sections drop
lowest-priority first (domain refs → domain SKILLs → concerns; never
Universal) and are listed in `metadata.dropped_for_budget`.

On a cache miss or stale result, order is: compile, then `write` with the
payload. Add `--payload .agent-skills/payload-<fingerprint>.md` (and
`--payload-budget <bytes>` when `--budget` was used) to the Step 5 `write`
command. Later hits then return `compile_needed: false`. Pass the same
`--budget` to `lookup` when the invoker supplies a cap.

Then reconcile the `degraded` flag (skip on the corrupt-cache fallback path):

```
python3 scripts/cook_cache.py heal --fingerprint <fp> --degraded <compiler.degraded>
```

`heal` stamps read failures onto the entry and clears them once files read
again; it rewrites only when the set changed, so the hit path stays cheap.

Then, **best-effort**, record the fire for telemetry (a silent no-op when
telemetry is disabled — always safe to call):

```
python3 scripts/cook_telemetry.py record --intent <label> \
  --prompt <raw task summary> --mode <mode> --skills <same paths as compile> \
  --project <project dir>
```

See [`telemetry.md`](telemetry.md) for the arg contract. This never alters the
return envelope and never fails a fire; skip it only if the compile itself did
not run.

**Return the summary envelope — `path`, `sections`, `degraded` — to the
invoking agent. Never inline or restate the payload content**; the invoker
reads the payload file itself. A non-empty `degraded` is a partial load: the
surviving sections are on disk, P0 always loaded, and flagged files retry on
the next invocation. Upstream prevention: `scripts/check_index_routes.py`
fails CI when an `_INDEX.md` route targets a missing file.

## Notes

- Cook owns detection and composition only; rules live under `standards/`
  (global universal + concern refs, plus the domain folders). Global is a peer
  library, not a privileged baseline.
- The fingerprint is built from raw observable signals only; the intent label
  is diagnostic, stored in the entry, never in the key — which is what lets
  the cache be checked before classification.
- When in doubt about the change surface, trust git-derived `signals.files`
  before widening the match.

## Explicit mode — manual resolver call

For flags and/or prose the multi-step flow replaces core Steps 1–5 with the
following; the flag grammar is in [`protocol-explicit.md`](protocol-explicit.md)
and the path-list rules are in the next section. Step 6 above is shared.

```
python3 scripts/cook_cache.py lookup --project <dir> \
  [--flag <name> ...] [--prose <text>]
```

- **Flags only** (`explicit-flags`): normal hit/miss lookup with the flags
  folded into the fingerprint. On `hit` with `compile_needed: false`,
  skip compile and `heal` and return `payload` as the envelope. On `hit` with
  `compile_needed: true`, use `routing.skills` and compile. On `miss` or
  `stale`, build the path list below, compile (core Step 6, with `--manifest`),
  then persist with the core Step 5 `write` command (add `--flag <name>` per
  flag and `--payload <compiled file>`; `--mode` defaults to `explicit-flags`).
- **Any prose** (`explicit-prose`): the resolver returns `status: "skip"` —
  prose is uncacheable (the LLM's ref selection has no deterministic key).
  Build the path list, skip the cache write entirely, and compile.

## Explicit mode — path list

Moved here from `protocol-explicit.md` (v1.2.0). `cook_run.py` applies these
rules itself (`scripts/cook_route.py`); build the list by hand only in the
manual flow. The text below is verbatim.

- `--global` → `standards/global/SKILL.md` + every `standards/global/refs/*.md`
  — the complete global shelf, and the only explicit-mode opt-in to P0.
- **Concern flag** (`--security`, `--auth`, `--crypto`, `--performance`, `--architecture`,
  `--api-design`, `--error-handling`, `--debug`, `--cicd`) →
  `standards/global/refs/<concern>.md` only (no P0 SKILL.md).
- **Bare domain flag** (`--<domain>`) → `standards/<domain>/SKILL.md` **always**
  loads; which refs load beside it depends on what else names that same domain:
  - **Alone** — no prose and no `--<domain>:<ref>` for it → the SKILL.md plus
    every ref with **no** file pattern in the `_INDEX.md` (always loads) and
    every ref whose file pattern matches a touched file (the paths from
    `--path`, else git) or whose `content:` signal occurs in a touched source file
    (an inline test still loads the testing ref). A ref with patterns and no match is skipped. With **zero** file signals → every
    `standards/<domain>/refs/*.md` (the full shelf) and the envelope sets
    `fallback_reason: "no_file_signals"`.
  - **`--<domain>:all`** → the SKILL.md plus every ref (the **full shelf**),
    whatever the files. `all` is reserved and is not a ref stem.
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
    domain's `_INDEX.md` keyword table matches against the prose, **unioned**
    with the pattern-free refs and the refs whose file patterns match the touched files. Zero matched
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
