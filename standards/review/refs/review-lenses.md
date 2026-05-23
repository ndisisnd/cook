---
name: Review Lenses
description: inspection lenses for correctness, security, and reliability
type: reference
---

# Review Lenses

## Correctness Lens

- Check whether the code matches the stated requirement.
- Check null, empty, timeout, retry, race, and duplicate-submission paths.
- Check state transitions for missing failure handling or invalid intermediate states.
- Check data mapping for dropped or renamed fields.
- Treat a missing test on risky behavior as an unverified correctness claim.

Example:
- A form submit handler updates UI state on success but never resets state on failure, and no test covers the failure path. That is a correctness finding.

## Security Lens

- Check trust boundaries for missing validation or sanitization.
- Check auth, role, owner, or tenant scoping on sensitive paths.
- Check logs plus responses for leaked secrets or internal data.
- Check unsafe HTML, URL, upload, redirect, or query construction.

Example:
- A backend handler reads `req.params.id` and returns the record without owner scoping. That is a security finding.

## Reliability Lens

- Check error handling and failure paths for silent production breakage.
- Check partial writes, lock cleanup, retry limits, and timeout behavior.
- Check observability for failures that operators need to detect.
- Check structural failure paths, including layer bleed that hides errors or bypasses recovery.

Example:
- Retry logic catches transient errors but never stops retrying or logs the final failure. That is a reliability finding.
