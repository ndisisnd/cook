---
# Allowed values: planned, complete
status: planned
---

# Verification Run [N] - [Task]

> [Briefly state what this plan authorizes, why it is needed, and the precedent followed.]
>
> **This file is a plan. It changes nothing on its own.** Execute only the scoped edits below,
> then update this file with audit and verification results.

---

## 1. Before / After

**Before:** [Current files, folders, behavior, or risk.]

**After:** [Target files, folders, behavior, or result.]

| File | Action |
|---|---|
| `[path]` | [create / edit / move / archive / delete / verify only] |
| `[path]` | [create / edit / move / archive / delete / verify only] |

---

## 2. Source Trace

Map every source that can lose rules, behavior, examples, or references.

| Source | Destination | Handling |
|---|---|---|
| `[source path]` | `[destination path or section]` | [carry / merge / update / archive / drop with reason] |
| `[source path]` | `[destination path or section]` | [carry / merge / update / archive / drop with reason] |

High-risk rows: `[orphans, shared refs, generated files, destructive moves, stale links]`.

---

## 3. Execution

1. Read all traced sources and relevant routing/generated files before editing.
2. Make the smallest scoped edits needed to reach the target state.
3. Re-walk the source trace and record the audit result below before moves, deletion, or archive cleanup.
4. Update indexes, changelog, docs, and routing only if required by the file table.
5. Run focused verification and re-read changed docs for stale paths or dangling references.

### Audit Result

- Status: `[pending / passed / failed]`
- Gaps fixed: `[none / list]`
- Deliberate drops: `[none / source + reason]`

---

## 4. Guardrails

- Allowed paths: `[list paths]`.
- Do not edit unrelated files or redesign outside this task.
- Do not silently drop content; every removal, merge, or archive must appear in §2 and the audit result.
- Use repo generators/scripts for generated files.
- Stop and ask if concurrent user changes directly conflict.

---

## 5. Success Criteria

- [ ] Target files/actions in §1 are complete
- [ ] Every §2 source row is accounted for or deliberately dropped with reason
- [ ] High-risk rows were read in full and handled explicitly
- [ ] Required indexes/docs/changelog/routing are updated
- [ ] Verification command(s): `[command and result]`
- [ ] No unintended files changed; no user changes reverted

---

## 6. Notes for Executor

- Work in order: trace, edit, audit, cleanup, verify.
- Prefer narrow edits over broad rewrites.
- Record deviations, failed checks, and follow-ups here.
