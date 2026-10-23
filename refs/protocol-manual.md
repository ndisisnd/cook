# Cook Protocol — Manual (step by step)

Fallback for Codex and for humans. Claude Code runs [`scripts/cook_run.py`](../scripts/cook_run.py)
instead (see [`protocol-cook.md`](protocol-cook.md)): one script call does
Steps 1–6 below. Use this file when the model cannot run `cook_run.py` or when
you want to run, check or debug each stage by hand. Every subcommand used
below still works on its own. The skill list that `cook_run.py` derives follows
the same rules as Steps 3–5 and the explicit path list; it lives in
`scripts/cook_route.py`.

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

The script matches signals against `vocab/tag-vocabulary.json` aliases and
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
following; the path-list rules are in [`protocol-explicit.md`](protocol-explicit.md).
Step 6 above is shared.

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
