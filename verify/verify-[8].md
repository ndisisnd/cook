---
status: planned
---

# Verification Run [8] — React Folder Archive Cleanup

> Companion to verify-[7] (Flutter). The React **content** consolidation is already
> done (verify-[5], status: completed): `standards/react/SKILL.md` + 6 `refs/` exist
> and carry the merged rules. But the migration was left **half-finished** — the 8
> old `react-*` sub-skill folders (25 files) still sit in `standards/react/`, and
> `_INDEX.md` still carries a "Deprecated (pending removal)" section. This plan
> finishes the job: bring React to the clean dart/graphql bar by **archiving** the 8
> folders, using the exact same out-of-tree archive approach as verify-[7].
>
> **Nothing is deleted.** The 8 folders are **moved verbatim to `archive/react/`** at
> the repo root, preserving their `react-<name>/...` paths for later review.
>
> **Gate:** archiving is only safe once we confirm no rule still lives *only* in a
> deprecated folder. §3 is a mandatory source-coverage audit that must pass before §4
> runs. verify-[5] specified this audit but its success-criteria boxes were left
> unchecked — treat coverage as unverified until §3 confirms it.

## 1. What Will Change

### Problem before

`standards/react/` is in the same incomplete state flutter is in now:

```
standards/react/
├── SKILL.md                 # active — merged target (done in verify-[5])
├── _INDEX.md                # active — but still has a "Deprecated (pending removal)" section
├── refs/                    # active — 6 merged refs
│   ├── component-patterns.md  performance.md  security.md
│   └── state-management.md     testing.md      tooling.md
├── react-component-patterns/  # DEPRECATED — still here (SKILL.md, refs/, evals/)
├── react-hooks/               # DEPRECATED
├── react-performance/         # DEPRECATED
├── react-security/            # DEPRECATED
├── react-state-management/    # DEPRECATED
├── react-testing/             # DEPRECATED
├── react-tooling/             # DEPRECATED
└── react-typescript/          # DEPRECATED
```

The 8 deprecated folders hold **25 files** (8 `SKILL.md`, 9 refs incl. `REFERENCE.md`
/ `patterns.md` / `example.md`, 8 `evals/evals.json`). They are dead weight: a glob
over `standards/react/**/SKILL.md` re-discovers them, and they contradict the
single-skill model every clean domain follows.

### After

```
standards/react/             # clean — matches dart/graphql exactly
├── SKILL.md
├── _INDEX.md                # "Deprecated" section → short "Archived" note → archive/react/
└── refs/  (6 files)

archive/react/               # repo root, out of standards/ — for review before deletion
├── react-component-patterns/  (verbatim)
├── ... all 8 folders ...
└── react-typescript/
```

---

## 2. Archive Location

Same rule and rationale as verify-[7] §"Archive location": the archive lives at
**`archive/react/`** (repo root, sibling to `standards/` and `verify/`), **not** under
`standards/react/`. `_INDEX.md` is auto-generated from `SKILL.md` frontmatters, so any
generator or router that globs `standards/react/**/SKILL.md` would re-discover archived
skills if they stayed in the standards tree. Moving them out guarantees cook's domain
detection and the index generator never pick them up. Inside the archive, keep each
folder's original layout (`SKILL.md`, `refs/`, `evals/`) untouched.

If verify-[7] has already created `archive/flutter/`, place `archive/react/` alongside
it under the same top-level `archive/`.

---

## 3. Pre-flight Gate — Source Coverage Audit (must pass before §4)

Archiving moves content out of the routed tree, so first confirm every rule in each
deprecated folder already exists in the active `SKILL.md` or a `refs/` file. Re-run the
audit from verify-[5] §5 "Task 7 — Source coverage audit" against the current tree.

Folder → destination (from `react/_INDEX.md` and verify-[5]):

| Deprecated folder | Content destination |
|---|---|
| `react-hooks/` (SKILL.md + refs/REFERENCE.md) | `SKILL.md` — P0 Hook Correctness |
| `react-component-patterns/SKILL.md` | `SKILL.md` — P0 Component Basics |
| `react-component-patterns/refs/{patterns,REFERENCE}.md` | `refs/component-patterns.md` |
| `react-security/SKILL.md` | `SKILL.md` — P0 Boundary Safety (+ `refs/security.md`) |
| `react-security/refs/REFERENCE.md` | `refs/security.md` |
| `react-typescript/` (SKILL.md + refs/example.md) | `SKILL.md` — P1 TypeScript |
| `react-performance/` (SKILL.md + refs/REFERENCE.md) | `refs/performance.md` |
| `react-state-management/` (SKILL.md + refs/REFERENCE.md) | `refs/state-management.md` |
| `react-testing/` (SKILL.md + refs/REFERENCE.md) | `refs/testing.md` |
| `react-tooling/` (SKILL.md + refs/example.md) | `refs/tooling.md` |

For **every** file above, read it in full and confirm each meaningful rule, example,
and anti-pattern is either present in its destination or was deliberately dropped for a
stated reason. **If any gap is found**, carry the missing content into the active
`SKILL.md`/ref **first**, then proceed. Do not archive a folder whose content is not
fully accounted for. `evals/evals.json` carries no rules — nothing to audit; it is
archived as-is.

---

## 4. Execution Steps

1. **Run the §3 gate.** Resolve any gaps by editing the active `SKILL.md`/`refs/`.
   Do not continue until coverage is confirmed.

2. **Move — do not delete — the 8 `react-*/` folders to `archive/react/`.**
   - Create `archive/react/` at the repo root.
   - `git mv` each `standards/react/react-<name>/` to
     `archive/react/react-<name>/`, verbatim (SKILL.md, refs/, evals/). `git mv`
     preserves history and makes the move reviewable in the diff.
   - After the move, `standards/react/` contains only `SKILL.md`, `_INDEX.md`, and
     `refs/` — no `react-*/` subfolders remain.

3. **Update `standards/react/_INDEX.md`.** Replace the "Deprecated (pending removal)"
   section with a short **Archived** note: state that the 8 superseded sub-skills were
   moved to `archive/react/` pending review, and keep the folder→destination mapping
   table (above) so a reviewer can trace each one. The File Match table and Loading
   Instructions are already correct — leave them.

4. **Confirm `cook/SKILL.md` routing.** The React domain row already points at
   `standards/react/_INDEX.md`; confirm nothing anywhere instructs the router to load
   `react/<skill>/SKILL.md` sub-folders. (No change expected — verify only.)

5. **Update `CHANGELOG.md`** (per repo workflow) describing the React folder archive.

---

## 5. Success Criteria

### Archive
- [ ] `archive/react/` exists at the repo root (outside `standards/`)
- [ ] All 8 `react-<name>/` folders present under `archive/react/`, verbatim (SKILL.md, refs/, evals/ intact) — 25 files
- [ ] No `react-*/` subfolders remain under `standards/react/`
- [ ] The move used `git mv` (history preserved; nothing deleted)

### Active react/ is clean
- [ ] `standards/react/` contains exactly `SKILL.md`, `_INDEX.md`, and `refs/`
- [ ] `refs/` still holds the 6 files: `component-patterns`, `performance`, `security`, `state-management`, `testing`, `tooling`
- [ ] `SKILL.md` and the 6 refs are unchanged except for any gap-fixes from the §3 gate
- [ ] No `REFERENCE.md`, `patterns.md`, or `example.md` remain under `standards/react/`

### _INDEX.md
- [ ] No "Deprecated (pending removal)" section remains
- [ ] An "Archived" note points to `archive/react/` and reproduces the folder→destination mapping
- [ ] File Match table and Loading Instructions unchanged

### cook routing
- [ ] `cook/SKILL.md` contains no instruction to load `react/<skill>/SKILL.md` sub-folders
- [ ] React domain row resolves to `standards/react/_INDEX.md` → `SKILL.md` + refs

### No loss / no unintended changes
- [ ] §3 source-coverage audit passed (every deprecated-folder rule accounted for) before any move
- [ ] No source file was deleted — every superseded file is present in `archive/react/`
- [ ] No changes to `standards/dart/`, `graphql/`, `database/`, `typescript/`, `flutter/`, `nextjs/`, `global/`, or `review/`
- [ ] `CHANGELOG.md` updated

---

## 6. Verification Notes for the Executing Agent

1. Run the §3 audit first and record the result (pass, or list of gaps fixed). This is
   the only step that can lose content if skipped.
2. After the move, confirm `standards/react/` is down to `SKILL.md` + `_INDEX.md` +
   `refs/` and that `archive/react/` holds all 8 folders with all 25 files.
3. Read `_INDEX.md` and confirm the "Deprecated" section is gone, replaced by an
   "Archived" note pointing to `archive/react/`.
4. Confirm `cook/SKILL.md` still routes React via `_INDEX.md` → `SKILL.md` + refs, with
   no stale "load the sub-skill folder" instruction.

This run is intentionally narrow: **no content redesign.** verify-[5] already merged
the rules; this finishes that migration by removing the deprecated folders from the
routed tree, exactly as verify-[7] does for Flutter. Once both land, React and Flutter
match the dart/graphql exemplar and `archive/` holds both sets of originals for review.
