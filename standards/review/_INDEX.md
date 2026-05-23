<!-- Top-level routing for the review skill. -->
# review Skills Index

## File Match

| Skill | File pattern | Keywords |
| ----- | ------------ | -------- |
| **review** | n/a | review this, review this PR, review this diff, audit this code, look for bugs, check for regressions, findings |

## Routing Notes

> Load `<SKILLS>/review/SKILL.md` when the primary task is code review rather than code editing.
> Cook detects the code surface and passes it as `code_surface`; the review skill uses it to load the matching standards.
> Use the review skill for findings and recommendations. Use coding skills for implementation.
