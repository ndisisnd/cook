---
name: Review Lenses
description: inspection lenses for correctness, security, architecture, and tests
type: reference
---

# Review Lenses

## Correctness Lens

- Check whether the code matches the stated requirement.
- Check null, empty, timeout, retry, and duplicate-submission paths.
- Check state transitions for missing failure handling.
- Check data mapping for dropped or renamed fields.

Example:
- A form submit handler updates UI state on success but never resets state on failure. That is a correctness finding.

## Security Lens

- Check trust boundaries for missing validation or sanitization.
- Check auth, role, owner, or tenant scoping on sensitive paths.
- Check logs plus responses for leaked secrets or internal data.
- Check unsafe HTML, URL, upload, redirect, or query construction.

Example:
- A backend handler reads `req.params.id` and returns the record without owner scoping. That is a security finding.

## Architecture Lens

- Check for business logic leaking into controllers, components, or views.
- Check for duplicated logic across layers.
- Check for large units that mix unrelated responsibilities.
- Check whether the new code matches the existing project structure.

Example:
- A React component performs API orchestration, validation, and formatting in one render path. That is an architecture finding.

## Test Lens

- Check whether the risky path has direct test coverage.
- Check whether new branches add failure paths without tests.
- Check whether the tests verify behavior rather than implementation trivia.
- Check whether the docs or examples now drift from the code.

Example:
- The diff adds retry logic but no test covers the retry limit or final failure path. That is a test gap.
