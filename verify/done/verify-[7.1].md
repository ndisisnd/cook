---
status: done
parent: verify-[7].md
---

# Verification Run [7.1] — Flutter Consolidation Issue Tracker

> Follow-up to **[verify-[7].md](verify-[7].md)** (Flutter skill consolidation).
> That run produced a full audit; this file tracks every open issue found.
> Fix P0s before committing. P1s before marking the migration done.

---

## Issues

| ID | Priority | File(s) | Issue | Outcome if Unfixed |
|---|---|---|---|---|
| 7.1-1 | **P0** | `standards/flutter/SKILL.md`, `standards/flutter/refs/` (×13), `standards/flutter/_INDEX.md`, `CHANGELOG.md` | New SKILL.md and all 13 refs are untracked (`??`) in git; `_INDEX.md` and `CHANGELOG.md` are modified but unstaged. Archive moves are staged correctly (`R`). Incomplete changeset — new files would be absent from any commit. | A `git commit` right now records only deletions; the entire new standards tree is missing from history. |
| 7.1-2 | **P0** | `standards/flutter/SKILL.md` line 37, `standards/flutter/refs/error-handling.md` line 3 | Priority contradiction: SKILL.md labels error handling **P0 (CRITICAL)**; `refs/error-handling.md` opens with **Priority: P1 (HIGH)**. Plan explicitly elevated it to P0 but the ref body was never updated to match. | Consuming agent reads two conflicting severities and may silently apply the weaker (P1) enforcement on a rule intended to be stop-the-world. |
| 7.1-3 | **P1** | `standards/flutter/SKILL.md` Anti-Patterns section | Anti-pattern dropped from `flutter-idiomatic-flutter` source: *"No direct controller access in widget — use BLoC or Signals to decouple UI from state."* All other idiomatic anti-patterns transferred correctly. | Code that accesses controllers directly in `build()` passes review without objection. |
| 7.1-4 | **P1** | `standards/flutter/refs/navigation.md` go_router section line 5 | go_router priority silently downgraded: source `flutter-go-router-navigation/SKILL.md` was **P0 (CRITICAL)**; merged result is **P1 (OPERATIONAL)**. Plan said "resolve the conflict" without specifying which wins; agent picked the lower value without documenting rationale. | Router/redirect guard work treated as operational rather than critical; a missing auth redirect may not be flagged as a stop-the-world violation. |
| 7.1-5 | **P2** | `standards/flutter/refs/architecture.md` | `BankDto` class + `BankRepository` block appears **twice** in the same file — once from `REFERENCE.md` (Full Layer Implementation) and again from the orphaned `repository-mapping.md` (Repository Mapping Reference). Both sources covered the same example. | Reader sees duplicate code blocks; erodes trust in merge quality. No functional harm. |
| 7.1-6 | **P2** | `standards/flutter/SKILL.md` P1 Idiomatic section | Dropped replacement guidance from `flutter-idiomatic-flutter`: *"use `Stack + FractionallySizedBox` for overlays"* as the alternative to `IntrinsicWidth/Height`. New SKILL.md only says "Avoid unless strictly required" with no substitute. | Developer who follows the "avoid" rule has no guidance on what to use instead for overlay layouts. |

---

## Fix Order

1. **7.1-1** — Stage all new files (`git add standards/flutter/SKILL.md standards/flutter/refs/ standards/flutter/_INDEX.md CHANGELOG.md`) then commit.
2. **7.1-2** — Change `refs/error-handling.md` line 3 from `**Priority: P1 (HIGH)**` to `**Priority: P0 (CRITICAL)**`.
3. **7.1-3** — Add to `SKILL.md` Anti-Patterns: `**No direct controller access in widget**: Use BLoC or Signals to decouple UI from state.`
4. **7.1-4** — Decide and document: keep go_router at P1 (intentional downgrade) or restore P0. Either way, add an inline note in `refs/navigation.md` explaining the chosen priority.
5. **7.1-5** — Remove the duplicate "Repository Mapping Reference" block at the bottom of `refs/architecture.md` (lines ~229–263); the Full Layer Implementation section already contains it.
6. **7.1-6** — Extend the `IntrinsicWidth/Height` bullet in SKILL.md P1 Idiomatic: append `; for overlays prefer \`Stack + FractionallySizedBox\``.
