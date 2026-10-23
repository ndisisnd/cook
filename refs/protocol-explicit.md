# Cook Protocol: explicit args grammar

`cook_run.py --args '<text after /cook>'` applies this grammar for you. The model does not read this file on the normal path. Read it only to split `/cook` args by hand into `--flag` and `--prose` (Codex without the script, humans, debugging). The script also picks the files each flag loads; those rules are in [`protocol-manual.md`](protocol-manual.md).

Explicit args are the whole load surface: no automatic P0, no auto-matching, and `fallback` is suppressed.

## Parse args

- Tokens beginning with `--` are flags:
  - **Simple** (`--security`, `--react`, `--global`): validated against the runtime flag set derived from `vocab/tag-vocabulary.json` `routes_to`. Unknown flag: non-zero exit with the valid flag list.
  - **Sub-ref** (`--react:hooks`): `--<domain>:<ref>`, where `ref` is a file stem under `standards/<domain>/refs/`.
- A bare `--` token ends flag parsing (Unix convention): everything after it is prose, even if dash-prefixed.
- All remaining text is the **prose** argument (whitespace-trimmed). Flag order is free: `/cook fix bug --react` is the same as `/cook --react fix bug`.

## By-hand call

```
python3 scripts/cook_run.py --project <dir> [--flag <name> ...] [--prose <text>]
```

Pass each flag without its dashes.

- **Flags only** (`explicit-flags`): cacheable.
- **Any prose** (`explicit-prose`): `status: "skip"`. Prose is uncacheable because the ref selection has no deterministic key.
- Prose without flags: the script classifies the prose. `needs_llm` and `--resume` work as in [`protocol-cook.md`](protocol-cook.md).
