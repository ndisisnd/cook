# Cook Protocol

Read this file when `/cook` carries args or a telemetry flag. `SKILL.md` covers the plain run.

## Step 0: telemetry flags

If the invocation carries `--init`, `--enable-telemetry`, `--disable-telemetry` or `--status`, read [`telemetry.md`](telemetry.md) and run its command with `--project <dir>`. If the flag is the whole invocation, print the output and stop. Otherwise strip the flag and continue with the remaining args. `cook_run.py` records the fire itself.

## Run

```
python3 scripts/cook_run.py --project <dir> [--path <file> ...] [--task "<summary>"] \
  [--args '<text after /cook>'] [--budget <bytes>] [--intent <label>] [--explain]
```

- No args: auto mode. Pass `--task`. Global P0 loads and the result is cached.
- Any args: pass the text after `/cook`, unchanged, as `--args`. The script splits flags from prose, validates the flags and picks the files. Do not build a path list. If the text holds a single quote, use `--args -` and pipe the text on stdin.
- Flags only: cached, no P0. Any prose: never cached (`status: skip`), no P0. Explicit args load exactly what they name.
- An unknown flag exits 1 and prints the valid flags on stderr. Report that message; do not guess a flag.
- `--explain` adds an `explain` object that says why each file loaded. Use it only when asked why.

Stdout is one JSON envelope: `mode`, `status` (`hit|miss|stale|skip|needs_llm`), `fingerprint`, `payload` (`path`, `bytes`, `sections`), `manifest_path`, `sections`, `degraded`, `dropped_for_budget`, `needs_llm`, `platform_ambiguous`.

## needs_llm

`needs_llm: true` means no domain resolved, or the Apple platform is unclear. Read `llm_input` (`vocab` path, raw signals, `matched_tags`). Pick canonical tags from the vocab. Never invent a tag. For `platform_ambiguous`, pick `ios` or `macos` from the task. If the task does not say, pass no platform tag. Then run:

```
python3 scripts/cook_run.py --resume <fingerprint> --tags <tag,tag,...>
```

## Return

Return the envelope (`payload`, `degraded`, `dropped_for_budget`) to the invoking agent. Never inline or restate the payload. Subagents slice it: [`payload-reuse.md`](payload-reuse.md). A non-empty `degraded` is a partial load: the surviving sections are on disk and P0 always loads.

`cache_corrupt: true` in the envelope means the script loaded broad and skipped the cache write. Standards still apply; only efficiency is lost.
