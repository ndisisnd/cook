---
name: cook
description: Keyword-driven orchestrator for this repository's coding and review standards. Receives a code-task summary from the invoking agent, extracts keywords, matches them against the global concern index and the relevant domain indexes, loads only the matched rules, and returns a single compiled standards payload.
metadata:
  triggers:
    files:
      - '**/*.ts'
      - '**/*.tsx'
      - '**/*.js'
      - '**/*.jsx'
      - '**/*.dart'
      - '**/*.sql'
      - '**/*.graphql'
    keywords:
      - review
      - audit
      - refactor
      - bug
      - feature
      - frontend
      - backend
      - full-stack
      - critique
      - regression
      - diff
      - react
      - nextjs
      - next.js
      - flutter
      - graphql
      - typescript
      - dart
      - prisma
      - apollo
      - migration
      - schema
      - auth
      - api
      - endpoint
      - component
      - hook
      - resolver
---

# Cook Orchestrator

Cook is the single entry point for standards. It does not hold rules of its own — it detects what a task touches and composes a payload from the rule libraries under `standards/`. There are no mode flags (`--frontend` / `--backend` / `--full-stack`); layer concerns are matched by keyword, so a task that touches both UI and server simply matches concerns and domains from both sides.

## Protocol

> **Phase 3 status (cook-feat-robust):** Steps 1–6 are the cache-first control
> flow from Phase 1. Step 7 is the mechanical compilation script (Phase 2) — no
> LLM assembly, deterministic, model-free on cache hits — now followed by a
> mechanical self-heal of the `degraded` flag (Phase 3, feature 7). A corrupt
> cache degrades to greedy routing (Component 8) without dropping standards.

### Step 1 — Build the normalised blob (cook-owned, cache-first)

Cook does **not** wait for a caller-written summary. It grounds itself in real
signals, then checks the cache **before** any classification — so a cache hit
never wakes the model.

**1a. Resolve.** Run the resolver first:

```
python3 scripts/cook_cache.py lookup [--path <file> ...] [--project <dir>]
```

It runs the file-derivation cascade (T1 explicit paths → T2 `git` → T4 manifest →
T5 prose-only) and the extension-disambiguation table for you, builds a
fingerprint from **raw observable signals only** (no intent label), and checks
the cache. It prints a JSON blob: `status` (`hit` | `miss` | `stale` |
`fallback`), `fingerprint`, `signals` (`files`, `extensions`, `frameworks`,
`domain_hints`, `source`), `confidence`, `fallback`.

**1b. Branch on status:**

- **`hit`** — the routing is cached and fresh (vocab + index checksums still
  match). Use `routing.skills` directly. **Do not classify, do not re-match.**
  Skip to Step 3 (P0 always loads), then Step 7 (compile). This is the no-LLM
  fast path.
- **`miss` | `stale`** — no usable cache. Continue to 1c.
- **`fallback`** — the cache file is present but **corrupt** (`cache_corrupt:
  true`); the resolver could not trust it (Component 8). The mechanically
  gathered `signals` are still valid, so degrade to **greedy routing**: skip
  classification and the cache write entirely, load Step 3 (P0) plus — broadly —
  every domain in `signals.domain_hints` and the full concern set, then compile
  (Step 7). Standards still apply; only the efficiency gain is lost. Do **not**
  call `write` or `heal` while the cache is corrupt.

**1c. Classify (miss path only).** Pick exactly ONE intent label from
`vocab/intent-vocabulary.json`. Then canonicalize: map each raw signal
(`signals` + any prose terms) onto a tag in `vocab/tag-vocabulary.json`. Output
is **constrained to the vocabulary** — never invent a tag. Drop and note any
unmappable signal. The resulting `canonical_tags` are the only thing Steps 4–5
read.

**1d. Sufficiency gate (never empty-handed).**

- ≥1 `domain:*` tag resolved → emit the blob with the resolver's `confidence`.
- Weak but files were reachable → trust `signals.domain_hints` from the cascade.
- Still weak, or resolver returned `fallback: true` → set `confidence: low`,
  `fallback: true`. Steps 4–5 then load broad. Step 3 (P0) loads regardless.

### Step 2 — Review intent?

If the classified intent is `review-code`, this is a review, not a build. Derive
the review surface from `signals`:

- Frontend: `.tsx`, `.jsx`, `components/`, `pages/`, `app/`, `hooks/`, `styles/`
- Backend: `controllers/`, `routes/`, `handlers/`, `services/`, `repositories/`, `db/`
- Full-stack: both present in one target
- Security-sensitive: auth, token, session, role, permission, owner scope, upload, redirect, webhook, external URL

Tag the surface as `frontend` / `backend` / `full-stack`, appending
`security-sensitive` when those signals appear (e.g. `full-stack, security-sensitive`).
Pass it as `code_surface`, load `standards/review/SKILL.md`, write the cache
entry (Step 6), and stop.

### Step 3 — Load global P0 (always, unconditional)

Load `standards/global/SKILL.md`. Its P0 universal rules apply to every code task
regardless of stack, confidence, or cache state. This floor is never skipped —
not on `fallback: true`, not on a weak classification.

### Step 4 — Match global concerns (via canonical_tags)

For each `canonical_tag` whose `routes_to` is a `concern:*` target, load the
matching concern ref under `standards/global/refs/` (`architecture.md`,
`api-design.md`, `error-handling.md`, `security.md`, `performance.md`,
`debug.md`). The tag-vocabulary `routes_to` is the matching surface; the
`standards/global/_INDEX.md` Concern Match table remains the within-file route
target. On `fallback: true`, load the broad concern set.

### Step 5 — Match domains (via canonical_tags)

For each `canonical_tag` whose `routes_to` is a `domain:*` target, load that
domain's `SKILL.md` plus any matched `refs/*.md`. **Multiple domains may
match** — a Next.js UI + Postgres schema resolves both `domain:nextjs` and
`domain:database`. Use the domain's `_INDEX.md` only to pick *which* refs within
that domain to load. For `typescript`, load `standards/typescript/SKILL.md`
directly. On `fallback: true`, load the broad domain set indicated by
`signals.domain_hints`.

### Step 6 — Write the cache entry (miss path only)

After matching, persist the decision so the next identical surface is a hit:

```
python3 scripts/cook_cache.py write --fingerprint <fp> --intent <label> \
  --skills <comma-separated skill paths> --tags <comma-separated canonical_tags> \
  --confidence <high|medium|low> [--fallback] \
  --index <comma-separated _INDEX.md paths used>
```

The write stamps the entry with a `tag-vocabulary.json` checksum and per-index
checksums (Feature 4) and writes atomically (tmp + rename). Skip this step on a
cache hit (the entry already exists) and on the `fallback` path (corrupt cache).

Write the **full** `--skills` list from Steps 3–5 — every matched path, even one
whose file might fail to read. A read failure is not a routing failure: the
routing was correct, so the entry must record it in full. The `degraded` flag is
*not* set here (the read outcome is unknown until the compiler runs) — Step 7
reconciles it after compilation.

### Step 7 — Compile and return

Invoke the compilation script with the path list assembled by Steps 3–5 (or
from `routing.skills` on a cache hit). The script is a single Bash call — no
LLM involvement:

```
python3 scripts/cook_compile.py \
  --skills <comma-separated paths relative to cook root>
```

The script deduplicates paths, buckets them (Universal → Domain → Concern),
reads each file, strips YAML frontmatter, and concatenates with terse section
headers (`## Universal`, `## React`, `## Security`, etc.). Output is JSON:

```json
{
  "content": "<assembled markdown>",
  "degraded": [],
  "metadata": {"resolutions_applied": [], "dropped_for_budget": []}
}
```

**Reconcile the `degraded` flag (feature 7 self-heal).** Right after compiling,
stamp the compiler's `degraded` list onto the cache entry — unless this is the
`fallback` (corrupt-cache) path, where there is no entry to heal:

```
python3 scripts/cook_cache.py heal --fingerprint <fp> --degraded <compiler.degraded>
```

This single mechanical call covers both directions and adds **no** LLM step:

- **Miss path:** if a matched file failed to read, `heal` stamps it onto the
  freshly written entry (the entry keeps the full routing; the flag names what
  failed *this* run).
- **Cache hit:** the compiler re-reads every `routing.skills` path, so its
  `degraded` list is current. A previously flagged file that now reads clears
  the flag; a newly missing file sets it. `heal` rewrites the entry only when
  the set changed (else `status: unchanged`), so the hit path stays cheap.

Then return the JSON envelope to the invoking agent. A non-empty `degraded` is a
**partial load**: the surviving sections are still returned, P0 always loaded, and
the next invocation re-attempts the flagged files automatically. The CI / pre-commit
validator (`scripts/check_index_routes.py`) is the upstream prevention pass — it
fails the build if any `_INDEX.md` route target points at a missing file.

**Path list construction:**
- **Cache hit:** use `routing.skills` from the resolver output directly.
- **Miss path:** collect the paths loaded in Steps 3–5:
  - Step 3: `standards/global/SKILL.md`
  - Step 4: each matched `standards/global/refs/<name>.md`
  - Step 5: each matched domain `SKILL.md` + matched `refs/*.md`
- **Fallback path (corrupt cache):** Step 3 P0 + every `signals.domain_hints`
  domain `SKILL.md` + the full concern set — loaded broad, compiled, returned;
  no `write`/`heal`.

## Notes

- Cook owns detection and composition only. The rules live in `global/` (universal + concern refs) and the domain folders.
- Global is one rule library among peers, not a privileged baseline that decides layers.
- The cache fingerprint is built from raw observable signals only; the intent label is stored *in* the entry, never in the key — this is what lets the cache be checked before classification.
- When in doubt about the change surface, trust `git`-derived `signals.files` before widening the match.
