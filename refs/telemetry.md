# Cook Telemetry — optional usage log

Telemetry is **opt-in and off by default**. When enabled, every successful cook
fire appends one record — its intent, the raw prompt, and the standards
extracted (folder → the standards loaded within it). It never changes what cook
loads or returns; it only observes.

Storage is a single JSON file, `telemetry/telemetry.json`, under the cook root
(alongside `.agent-skills/`). The same file holds the `enabled` flag, so state
persists across fires. It is gitignored and not shipped by the installer — a
purely local, runtime artifact. The mechanical work lives in
`scripts/cook_telemetry.py`; this ref is the protocol contract around it.

## Management flags (intercept before Steps 1–6)

When a `/cook` invocation carries **only** one of the flags below — no other
flags, no prose to compile — treat it as a management command: run the matching
script call, print its stdout to the user, and **terminate**. Do not run the
resolver, classifier, or compiler.

| Flag | Action |
|---|---|
| `--enable-telemetry` | `python3 scripts/cook_telemetry.py enable` |
| `--disable-telemetry` | `python3 scripts/cook_telemetry.py disable` |
| `--status` | `python3 scripts/cook_telemetry.py status` |

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
  --skills <the exact comma-separated paths passed to cook_compile.py>
```

- **`--intent`** — the closest label from `vocab/intent-vocabulary.json`
  (e.g. `refactor`, `fix-bug`, `write-feature`). Use `unspecified` when no
  label fits or the invocation carried no discernible intent (e.g. flags only).
- **`--prompt`** — the raw prose / task summary cook was given. Empty string
  for a pure-flags invocation with no prose.
- **`--mode`** — the invocation mode from the mode branch table.
- **`--skills`** — reuse the same value passed to `cook_compile.py --skills` so
  the logged standards match exactly what was compiled.

The script groups the skill paths into `folder → [standard, ...]`, where a
standard is `SKILL` for a shelf entry or `refs/<name>` for a ref. Produce no
user-facing output for this step; the fire's return envelope is unchanged.

## `--status` report

`status` prints, to the console: the enabled/disabled state, the store path,
the total fire count and time window, then ranked breakdowns — by intent, by
folder (how many fires touched each), and the top individual standards. With no
records it prints a short "nothing logged yet" hint.
