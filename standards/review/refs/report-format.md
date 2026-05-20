---
name: Report Format
description: required structure and wording for the `PRD-[n]-fix` report file
type: reference
---

# Report Format

## File Structure

- Start with `# Review Findings`.
- Group findings by severity in this order: `Blocker`, `Major`, `Minor`, `Note`.
- Put findings first. Put any short summary after the findings.
- Write one finding per bullet.

## Finding Format

Use this exact shape for each finding:

```markdown
- [Severity] `path/to/file:line` - short issue title
  - Why: concrete failure mode or risk
  - Impact: who or what breaks
  - Fix: short repair direction
  - Coverage gap: missing test or missing validation path
```

## Summary Format

- End with `## Recommendation`.
- State `block`, `fix before merge`, or `safe with follow-up`.
- Give one sentence for the reason.

## Worked Example

```markdown
# Review Findings

## Blocker

- [Blocker] `src/api/users.ts:91` - resource lookup skips owner scoping
  - Why: the handler reads by raw id without checking tenant ownership
  - Impact: one user can access another user's record
  - Fix: scope the query by `tenantId` plus the user-supplied id
  - Coverage gap: no authorization regression test covers cross-tenant access

## Recommendation

block - the change exposes unauthorized data access.
```
