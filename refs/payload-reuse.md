# Payload reuse

One cook call per pipeline. Subagents read slices of that payload. They do not get copies.

## Caller contract

- Call cook once. Keep the envelope: `payload.path`, `manifest_path`, `sections`.
- Give each subagent the payload path and the section names it needs. Do not paste the payload.
- A subagent that needs standards runs `slice` for its sections only.
- Inject the full payload only when the caller sets `inject: full`.
- Pass `--consumer <label>` (for example `eng-build`) on the cook call so `--status` shows reuse against reinjection.

## Slice

```
python3 scripts/cook_compile.py slice --payload <payload.path> --section "<header|rel>" [--section ...]
python3 scripts/cook_compile.py slice --payload <payload.path> --list
```

- A section is a `sections[].header` (`## React — Hooks`, or without `## `) or a `sections[].rel` (`standards/react/refs/hooks.md`).
- Output is the section text, byte for byte as in the payload. Several sections come out in payload order, with the payload separator.
- Exit 1: unknown or ambiguous section. The available sections print on stderr.
- Exit 2: payload or manifest missing, or the manifest is stale. Run cook again.
- No LLM and no recompile. The same input gives the same output.

## Choosing sections

- Take `## Universal` for every subagent that writes or reviews code.
- Add the shelf `SKILL` section for each language or framework the subagent touches.
- Add a ref section only when the subagent's task matches it.
