# Cook Protocol

Operational protocol for the `cook` orchestrator. `SKILL.md` is the thin entry
point; follow this file exactly. If the invocation carries **any** args (flags
and/or prose), read [`protocol-explicit.md`](protocol-explicit.md) instead of
Steps 1–5 — the compile step (Step 6) is shared.

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
`frameworks`, `domain_hints`, `source`), `confidence`, `fallback`, `routing`.
Non-zero exit or unparseable stdout → treat as `miss` with `confidence: low`
and empty signals; never reuse output from a failed run.

Branch on `status`:

- **`hit`** — routing is cached and fresh. Use `routing.skills` directly; skip
  to Step 6. No classification, no re-match.
- **`miss` | `stale`** — continue to Step 2.
- **`fallback`** — the cache file exists but is corrupt (`cache_corrupt: true`).
  Degrade to greedy routing: Step 3's P0 + every domain in
  `signals.domain_hints` (each `SKILL.md`) + all 8 concern refs (Step 4's set),
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

**Sufficiency (never empty-handed):** ≥1 `domain:*` route → proceed with the
resolver's `confidence`. None resolved, or the resolver said `fallback: true`
→ set `confidence: low`, `fallback: true`, and load broad in Steps 4–5
(all 8 concern refs + the `signals.domain_hints` domains). P0 loads regardless.

### Step 3 — Load global P0 (always)

Load `standards/global/SKILL.md`. It applies to every auto-mode task
regardless of stack, confidence, or cache state — never skipped. (Explicit
mode intentionally omits it; see `protocol-explicit.md`.)

### Step 4 — Match concerns

For each route `concern:<name>`, load `standards/global/refs/<name>.md`. The
full concern set — also the fallback load — is exactly: `architecture.md`,
`api-design.md`, `error-handling.md`, `security.md`, `auth.md`,
`performance.md`, `debug.md`, `cicd.md`.

Supabase key-boundary work stacks with security: secret-key / `service_role` /
client-public-env / key-leak language also loads `security.md`; API-key
service-to-service language may also load `auth.md`. The Supabase refs own the
platform-specific key boundary; auth/security own the generic trust boundary.

### Step 5 — Match domains, then persist

For each route `domain:<name>`, load `standards/<name>/SKILL.md`, then use that
domain's `_INDEX.md` to pick which `refs/*.md` match the task. Multiple
domains may match (e.g. Next.js UI + Postgres schema → both shelves).

Persist the decision (miss path only — skip on hit and on the corrupt-cache
fallback):

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
  --out .agent-skills/payload-<fingerprint>.md
```

(Use `payload-prose.md` on the explicit-prose path, which has no fingerprint.)
The compiler deduplicates, buckets (Universal → Domain → Concern), strips
frontmatter, writes the assembled markdown to `--out`, and prints a summary
envelope: `path`, `bytes`, `sections`, `degraded`, `metadata`. If the invoker
supplied a payload cap, pass `--budget <bytes>` — over-budget sections drop
lowest-priority first (domain refs → domain SKILLs → concerns; never
Universal) and are listed in `metadata.dropped_for_budget`.

Then reconcile the `degraded` flag (skip on the corrupt-cache fallback path):

```
python3 scripts/cook_cache.py heal --fingerprint <fp> --degraded <compiler.degraded>
```

`heal` stamps read failures onto the entry and clears them once files read
again; it rewrites only when the set changed, so the hit path stays cheap.

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
