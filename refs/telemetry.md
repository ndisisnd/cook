# Cook Telemetry — optional usage log

Telemetry is **opt-in and off by default**. When enabled, every successful cook
fire appends one record — its intent, the raw prompt, and the standards
extracted (folder → the standards loaded within it). It never changes what cook
loads or returns; it only observes.

## Scope — local-first

Storage is a single JSON file, `telemetry/telemetry.json`, holding the `enabled`
flag and the `records` array together. It resolves **local-first**:

1. **Local** — `<project>/telemetry/telemetry.json`, created by `--init`. A repo
   that has been initialised keeps its own log.
2. **Global** — `<cook-root>/telemetry/telemetry.json` (the install dir,
   alongside `.agent-skills/`). The fallback for any repo not initialised.

`--init` creates the local store; once it exists, every telemetry call for that
project (`enable` / `disable` / `status` / `record`) targets it. Pass
`--project <dir>` on every call (the resolver's project dir) so scope resolves
correctly; `--global` forces the global store regardless. Both stores are
gitignored and never shipped by the installer — purely local, runtime artifacts.
The mechanical work lives in `scripts/cook_telemetry.py`; this ref is the
protocol contract around it.

## Management flags (intercept before Steps 1–6)

When a `/cook` invocation carries **only** one of the flags below — no other
flags, no prose to compile — treat it as a management command: run the matching
script call, print its stdout to the user, and **terminate**. Do not run the
resolver, classifier, or compiler.

| Flag | Action |
|---|---|
| `--init` | `python3 scripts/cook_telemetry.py init --project <dir>` |
| `--enable-telemetry` | `python3 scripts/cook_telemetry.py enable --project <dir>` |
| `--disable-telemetry` | `python3 scripts/cook_telemetry.py disable --project <dir>` |
| `--status` | `python3 scripts/cook_telemetry.py status --project <dir>` |

`--init` initialises **local** telemetry for the current repository (creates the
store and enables it), so that repo's subsequent cook calls record locally
instead of in the global store. It is idempotent — re-running preserves existing
records and just re-enables.

If a management flag appears **alongside** real load args (e.g.
`/cook --react --status`), run the management command first and print it, then
continue with the normal load for the remaining args — the management flag is
stripped and never treated as a standards flag.

## Record step (after a successful compile)

This is the final action of every fire that reached the compile step (core
Step 6), in **all** modes. It is best-effort: `record` is a silent no-op when
telemetry is disabled and never fails a fire, so it is always safe to call.

```
python3 scripts/cook_telemetry.py record \
  --intent <label> \
  --prompt <raw task summary> \
  --mode <auto|explicit-flags|explicit-prose> \
  --skills <the exact comma-separated paths passed to cook_compile.py> \
  --project <project dir>
```

- **`--intent`** — the closest label from `vocab/intent-vocabulary.json`
  (e.g. `refactor`, `fix-bug`, `write-feature`). Use `unspecified` when no
  label fits or the invocation carried no discernible intent (e.g. flags only).
- **`--prompt`** — the raw prose / task summary cook was given. Empty string
  for a pure-flags invocation with no prose.
- **`--mode`** — the invocation mode from the mode branch table.
- **`--skills`** — reuse the same value passed to `cook_compile.py --skills` so
  the logged standards match exactly what was compiled.
- **`--project`** — the project dir, so the record lands in the local store when
  the repo has been `--init`-ed, else the global one.

The script groups the skill paths into `folder → [standard, ...]`, where a
standard is `SKILL` for a shelf entry or `refs/<name>` for a ref. Produce no
user-facing output for this step; the fire's return envelope is unchanged.

## `--status` report

`status` prints, to the console: the enabled/disabled state **and scope**
(local/global), the store path, the total fire count and time window, then
ranked breakdowns — the top individual standards, by folder (how many fires
touched each), and by intent. With no records it prints a short "nothing logged
yet" hint.
