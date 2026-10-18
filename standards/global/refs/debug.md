---
last_reviewed: 2026-10-18
---

# Debugging

## Rules

- Reproduce first. Write the smallest failing case (ideally a test) before changing code.
- Prove the root cause before the fix. Change one variable at a time.
- Check what changed since it last worked (`git bisect`, dependency diff, config diff).
- Fix the cause, not the symptom. Never silence the error or widen a `catch` to make it pass.
- Keep the reproduction as a regression test after the fix.
- Remove debug prints and temporary flags before finishing.

## Bug Report Fields

Component · version/commit · severity · steps to reproduce · expected vs actual ·
logs/stack trace (secrets and PII redacted) · environment (OS, browser/device).
