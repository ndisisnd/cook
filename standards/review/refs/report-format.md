---
name: Report Format
description: required structure and wording for the eval report file, including vibecoder-friendly fields
type: reference
---

# Report Format

## File Structure

- Open with `# Review Findings`.
- Follow immediately with `## TL;DR` — a 2–3 sentence plain-English summary of the change and what was found.
- Group findings by severity in this order: `Blocker`, `Major`, `Minor`, `Note`.
- Put findings first. Put any short summary after the findings.
- Write one finding per bullet.
- End with `## Recommendation`.

## Finding Format

Use this exact shape for each finding:

```markdown
- [Severity] `path/to/file:line` - short issue title
  - **Plain English**: one sentence a non-engineer could understand
  - Why: concrete failure mode or risk
  - Impact: who or what breaks
  - Fix: short repair direction
  - Skip outcome: what specifically goes wrong if left unfixed (be concrete — "users lose data", "attackers can read other users' records")
  - Ignorable: Yes | No | With tracking — one-line reason
  - Coverage gap: missing test or missing validation path
```

### Field guidance

| Field | Rule |
|-------|------|
| Plain English | No jargon. Imagine explaining it to a product manager or junior dev. |
| Skip outcome | Name a concrete bad event, not an abstract risk. "The checkout button charges twice" beats "may cause duplicate charges". |
| Ignorable | **No** for Blockers (always). **With tracking** for Majors that have a known workaround or low prod likelihood. **Yes** for Notes by default. |

## Summary Format

- End with `## Recommendation`.
- State `block`, `fix before merge`, or `safe with follow-up`.
- Give one sentence for the reason.

## Worked Example

```markdown
# Review Findings

## TL;DR
This PR adds a new checkout endpoint. It processes payments correctly on the happy path but skips ownership checks on the order lookup, meaning one user can pay for — and therefore cancel — another user's order. There is one blocker that must be fixed before merge.

**Target type**: code
**Surface**: backend

## Blocker

- [Blocker] `src/api/orders.ts:91` - resource lookup skips owner scoping
  - **Plain English**: Any logged-in user can look up and modify someone else's order just by guessing the order ID.
  - Why: the handler reads by raw id without checking tenant ownership
  - Impact: one user can access, modify, or cancel another user's order
  - Fix: scope the query by `tenantId` plus the user-supplied id
  - Skip outcome: an attacker enumerates order IDs and cancels or steals other users' purchases
  - Ignorable: No — this is an auth bypass on a financial resource
  - Coverage gap: no authorization regression test covers cross-tenant access

## Major

- [Major] `src/api/orders.ts:51` - form submits twice on repeated clicks
  - **Plain English**: Clicking "Pay" twice quickly will charge the card twice.
  - Why: the submit handler has no idempotency guard or debounce
  - Impact: customers get double-charged; support burden increases
  - Fix: disable the button on first submit and re-enable only on error; use a server-side idempotency key
  - Skip outcome: occasional duplicate charges, chargebacks, and support tickets
  - Ignorable: With tracking — low frequency in practice but high severity when it occurs; track in backlog with a deadline
  - Coverage gap: no test submits the form twice in quick succession

## Recommendation

block - the change exposes unauthorized access to financial records.
```
