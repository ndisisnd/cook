# Cook Protocol

Operational protocol for the `cook` orchestrator. `SKILL.md` is the thin entry
point; follow this file exactly. Handle Step 0 (telemetry management flags)
first. Then run `scripts/cook_run.py` once. It does the lookup, classify,
skill derivation, compile, cache write and telemetry record in one process.
The old step-by-step flow is in [`protocol-manual.md`](protocol-manual.md)
(Codex fallback, humans).

### Step 0 — Telemetry management flags (intercept first)

If the invocation carries a telemetry management flag — `--init`,
`--enable-telemetry`, `--disable-telemetry`, or `--status` — read
[`telemetry.md`](telemetry.md) and follow it. When such a flag is the whole
invocation, run the matching command, print its output, and terminate (do not
run `cook_run.py`). Otherwise strip the flag, run its command, then continue
below with the remaining args. Telemetry is opt-in and off by default; `cook_run.py` records the fire itself.

`--init` initialises a **local** telemetry store for the current repository so
its cook calls record there instead of the global install store. Always pass the
project directory (`--project <dir>`, the same one used for the resolver) to
every telemetry call so local/global scope resolves correctly.

| Mode | Condition | P0 loaded? | Cache? | Path |
|---|---|---|---|---|
| `auto` | no args | yes (unconditional) | yes | `cook_run.py` (no args) |
| `explicit-flags` | flags only | no | yes | `protocol-explicit.md` → `cook_run.py --flag` |
| `explicit-prose` | any prose (± flags) | no | no | `protocol-explicit.md` → `cook_run.py --flag` |

### Run

```
python3 scripts/cook_run.py --project <dir> [--path <file> ...] [--task <task summary>] \
  [--flag <name> ...] [--prose <text>] [--budget <bytes>] [--intent <label>]
```

- No args: auto mode. Pass `--task` with the task summary so `_INDEX.md`
  keywords can match.
- Flags only: `--flag react --flag security` (names without the dashes). Read
  [`protocol-explicit.md`](protocol-explicit.md) only to parse `/cook` args.
- Any prose: `--prose <text>` (uncacheable).

Stdout is one JSON envelope: `mode`, `status` (`hit|miss|stale|skip|needs_llm`),
`fingerprint`, `payload` (`path`, `bytes`, `sections`), `manifest_path`,
`degraded`, `dropped_for_budget`, `needs_llm`, `platform_ambiguous`.

### Branch on `needs_llm`

- `false` — done. Return the envelope.
- `true` — no domain resolved, or Apple platform unclear. Read `llm_input`
  (`vocab` path, raw signals, `matched_tags`). Pick canonical tags from the
  vocab; never invent a tag. For `platform_ambiguous`, pick `ios` or `macos`
  from the task; if the task does not say, pass no platform tag. Then run:

```
python3 scripts/cook_run.py --resume <fingerprint> --tags <tag,tag,...>
```

This is the only two-call path. The tags are added to the mechanical matches.

### Return

**Return the envelope — `payload`, `degraded`, `dropped_for_budget` — to the
invoking agent. Never inline or restate the payload content**; the invoker
reads the payload file itself. A non-empty `degraded` is a partial load: the
surviving sections are on disk, P0 always loaded, and flagged files retry on
the next invocation.

A corrupt cache (`cache_corrupt: true` in the envelope) is handled by the
script: it loads broad and skips the cache write. Standards still apply; only
efficiency is lost.

## Notes

- Cook owns detection and composition only; rules live under `standards/`.
- The fingerprint is built from raw observable signals only; the intent label
  and task text are never in the key.
- When in doubt about the change surface, trust git-derived `signals.files`
  before widening the match.
