---
name: Finding Severity
description: severity rules for blockers, major issues, and lower-priority findings
type: reference
---

# Finding Severity

## Severity Bands

| Severity | Use for | Expected action |
| --- | --- | --- |
| Blocker | Security flaw, data loss, broken core flow, corrupt output | Stop merge or release until fixed |
| Major | High-likelihood bug, regression, missing access check, missing error path | Fix before merge unless the owner accepts the risk |
| Minor | Low-impact bug, narrow edge case, maintainability issue with clear risk | Fix soon or track explicitly |
| Note | Clarification, follow-up question, or improvement with low risk | Optional follow-up |

## Ranking Rules

- Rank by user impact first.
- Rank by exploitability first for security findings.
- Rank by production likelihood before code style concerns.
- Raise severity when the code has no tests for the risky path.
- Lower severity only when the failure needs an unlikely precondition.

## Evidence Rules

- Cite the file and line for every finding.
- Name the failure mode in one sentence.
- State the impact in one sentence.
- State the missing check, missing test, or broken assumption.

## Worked Example

- `Blocker` - `src/api/orders.ts:84` builds a SQL string with user input. Impact: attackers can read or alter order data.
- `Major` - `src/components/CheckoutForm.tsx:51` submits twice on repeated clicks. Impact: users can create duplicate orders.
- `Minor` - `src/utils/date.ts:33` fails on empty input. Impact: one admin screen can crash on malformed data.
