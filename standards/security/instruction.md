# Verification Brief — security/core compression pilot

**Status:** temporary file. Delete after verification is complete.

## Goal

Compress `core/*.md` files for token efficiency. Three pilot files have been rewritten under a new template. Verify they are correct, complete, and consistent.

## Files in pilot

| File | Before | After |
| ---- | -----: | ----: |
| `core/codeguard-1-hardcoded-credentials.md` | 44 L | 41 L |
| `core/codeguard-1-crypto-algorithms.md` | 136 L | 52 L |
| `core/codeguard-1-digital-certificates.md` | 136 L | 49 L |

Originals are in git history (last commit on `main` before this work). To diff against the source-of-truth, run `git log --oneline -- standards/security/core/codeguard-1-*.md` and `git show <prev>:standards/security/core/codeguard-1-<name>.md`.

## Template the pilot files must follow

```
---
description: <one-line scope, ≤120 chars>
alwaysApply: true|false
---

# <Topic>

<optional 1-sentence framing of WHEN this rule fires — only if non-obvious>

## NEVER
- <hard prohibitions, one line each, terse>

## ALWAYS
- <hard mandates, one line each, terse>

## <Detail sections — 1-3 only, named by topic>
- <bullets, tables, or short code>

## Checklist
- [ ] <4-7 scannable verification items mirroring NEVER/ALWAYS>
```

### Template rules

1. **File length ≤100 lines**, including frontmatter and the trailing newline.
2. **Critical-at-top-and-bottom**: `NEVER` and `ALWAYS` sections appear in the first half; `Checklist` is the last section and mirrors the same critical rules.
3. **Frontmatter**: keep only `description` and `alwaysApply`. Drop empty `languages: []`, drop `tags:` (verified not consumed by `scripts/cook_compile.py`).
4. **No narrative preamble** beyond a single framing sentence. Mission statements ("Build a resilient…") must be cut.
5. **Tables for repetitive shapes** ("old → new", "provider → format", "condition → severity").
6. **Code examples**: keep only if they show non-obvious API shape. Strip error-handling boilerplate. Aim for ≤6 lines per example.
7. **No "Test Plan" section** — fold into `Checklist`.
8. **No meta-instructions** like "you must always explain how this rule was applied" — those belong in `security/SKILL.md` once.

## Verification checklist

For each of the three pilot files, confirm:

### Structure
- [ ] Frontmatter has only `description` and `alwaysApply` (no `languages`, no `tags`)
- [ ] File is ≤100 lines (`wc -l`)
- [ ] Has `## NEVER` and `## ALWAYS` sections in the first half
- [ ] Has a `## Checklist` as the final section
- [ ] No `## Test Plan` section
- [ ] No narrative intro paragraph beyond one framing sentence

### Content fidelity (compare against the pre-compression versions in git)
- [ ] **No rule from the original was dropped** — every banned item, mandate, recognition pattern, or check from the original appears in the rewrite (possibly reworded or tabulated)
- [ ] **No rule was weakened** — "NEVER" / "MUST" intent preserved; nothing softened to "consider" or "prefer" unless the original was also soft
- [ ] **No new prescriptive rules invented** that weren't in the original or weren't a natural restatement
- [ ] Provider/format tables (credentials) and validation tables (certificates) are complete vs originals
- [ ] Crypto banned/recommended lists cover all original items (MD2-SHA1, RC2-3DES, ECB/CBC, PKCS#1 v1.5, anon-DH, hybrid KEM list, etc.)

### Consistency across the three files
- [ ] Same section ordering and heading style
- [ ] Same bullet style (`-`, not `*`)
- [ ] Same code-fence language tags where present
- [ ] Tone is uniformly imperative and terse (no "you should consider…" hedging)

### Smell tests
- [ ] No duplicate content between the three files (TLS, key storage, cert validation only appear where they belong)
- [ ] Checklist items map 1:1 onto NEVER/ALWAYS bullets above them (no checklist item references something not stated above)

## Out of scope for this pass

- Other `core/*.md` files (the `codeguard-0-*` set) — those are next, not pilot.
- `owasp/*.md` files — untouched.
- Cross-file dedup (`safe-c-functions` exists in both `core/` and `owasp/`; `additional-cryptography` overlaps `crypto-algorithms`) — flagged but deferred.

## If you find issues

Report findings as a list per file:
- **File:** path
- **Severity:** critical (dropped rule, weakened intent) / minor (style, ordering, typo)
- **Issue:** what's wrong
- **Suggested fix:** specific edit

Do not edit the files yourself — return findings to the orchestrator.

## When verification passes

Delete this `instruction.md` and confirm the pilot is approved for rollout to the remaining `core/codeguard-0-*.md` files under the same template.
