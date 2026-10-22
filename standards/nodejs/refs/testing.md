---
last_reviewed: 2026-10-18
---

# Node.js Testing

General TypeScript test strategy lives in `standards/typescript/refs/testing.md`; API contract assertions in `global/refs/api-design.md`.

## Runner And Shape

- Use the repo's runner; with none, `node:test` is the low-dependency default for Node-only packages.
- Keep unit tests hermetic: no real network, no real timers unless timer-specific, no leaking process-global state.
- Restore mutated globals (`process.env`, timers, `process.cwd()`, singleton loggers) after each test.

## Services And Integration

- Test HTTP handlers through the real server adapter or framework harness when behaviour depends on Node request/response semantics.
- Prefer a real test database/cache for boundary tests when persistence semantics matter; mocks are fine for unit tests and third-party SDK isolation. Database rules live in `standards/database/`.
- Use ephemeral ports or framework injection. Signal: fixed ports colliding under parallel runs.

## Async, Timers, Shutdown

- Assert rejections with the runner's rejection assertion; leave no background rejections to process handlers.
- Fake timers only when the runner supports them cleanly and all scheduled work is flushed. Signal: arbitrary `setTimeout` waits.
- Cover graceful shutdown for long-lived services: signal handling, readiness failure, connection close, hard deadline.

## Network And Filesystem

- Unit tests never call the public internet; stub the network or inject the client.
- Filesystem tests use temporary directories, cleaned afterwards; never write into the repo tree.
- CLI tests assert exit code, stdout/stderr contract, and side effects separately.
