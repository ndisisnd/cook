# Debugging

## Scientific Method

1. **Observe** — gather data before forming a theory. Collect logs, stack traces, screenshots, and steps to reproduce.
2. **Hypothesize** — form a specific theory: "I think X is causing Y because Z."
3. **Experiment** — create a reproduction case. Change one variable at a time to validate the hypothesis.
4. **Fix** — implement the solution only after the root cause is proven.
5. **Verify** — confirm the fix works and has not introduced regressions.

## Best Practices

- **Diff diagnosis** — what changed since it last worked?
- **Minimal reproduction** — create the smallest possible snippet that reproduces the issue.
- **Binary search** — comment out half the code to isolate the failing section.
- **Rubber ducking** — explain the code line-by-line out loud; the act of explaining often reveals the error.

## Anti-Patterns

- Shotgun debugging: changing multiple things at once without proving root cause
- Debug prints left in production code
- Symptom masking: swallowing errors or catching exceptions without handling them

## Bug Report Template

```markdown
## Context

- Component: [e.g., Auth Service, Login Screen]
- Version/Commit: [e.g., v1.2.0, sha12345]
- Severity: [Critical / Major / Minor]

## Description

Clear and concise description of the bug.

## Steps to Reproduce

1. Go to '...'
2. Click '...'
3. See error.

## Expected Behavior

What you expected to happen.

## Actual Behavior

What actually happened.

## Logs / Screenshots

Paste stack traces or attach screenshots here.

## Environment

- OS: [e.g., macOS, iOS 17]
- Browser / Device: [e.g., Chrome 124, iPhone 14]
```
