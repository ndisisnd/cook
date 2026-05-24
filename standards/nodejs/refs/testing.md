# Node.js Testing

Use this ref for Node service, CLI, worker, integration, or network-boundary tests. General test strategy for TypeScript projects lives in `standards/typescript/refs/testing.md`; API contract assertions live in `global/refs/api-design.md`.

## Test Runner And Shape

- Use the repo's established runner. If there is no existing runner, `node:test` is a low-dependency default for Node-only packages.
- Keep unit tests hermetic: no real network, no real timers unless the behaviour under test is timer-specific, no dependency on process-global state that leaks between tests.
- Restore mutated globals such as `process.env`, timers, `process.cwd()`, and singleton loggers after each test. Signal: a test mutates process state without cleanup.

## Services And Integration Boundaries

- Test HTTP handlers through the actual server adapter or framework test harness when behaviour depends on Node request/response semantics.
- Prefer a real test database/cache for boundary integration tests when persistence semantics matter. Mocks are acceptable for unit tests and third-party SDK isolation. Database-specific rules live in `standards/database/`.
- Use ephemeral ports or framework injection. Signal: tests bind fixed ports that collide under parallel runs.

## Async, Timers, And Shutdown

- Assert rejected promises with the runner's rejection assertion; do not leave background rejections to process handlers.
- Use fake timers only when the repo's runner supports them cleanly and all scheduled work is flushed. Signal: flaky sleeps such as arbitrary `setTimeout` waits.
- Cover graceful shutdown for long-lived services: signal handling, readiness failure, connection close, and hard-deadline behaviour.

## Network And Filesystem

- Unit tests do not call the public internet. Stub network with the repo's chosen mechanism or inject the client.
- Use temporary directories for filesystem tests and clean them after the test. Avoid writing into the repository tree.
- For CLI tests, assert exit code, stdout/stderr contract, and side effects separately.

## Anti-Patterns

- Tests that rely on public network availability
- Fixed ports in parallel tests
- Mutating `process.env` without restore
- Arbitrary sleeps instead of deterministic timer control
- Background promise rejections ignored by the test
- Repository-root temp files left behind
