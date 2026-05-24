---
name: nodejs
description: Node.js runtime standards for event loop safety, process lifecycle, streams/backpressure, Buffer memory safety, runtime pinning, package installs, environment loading, and production logging. Use for Node service, CLI, worker, or server runtime implementation and review; co-loads with TypeScript when code is TypeScript.
metadata:
  triggers:
    files:
      - 'server.{ts,js,mjs,cjs}'
      - 'app.{ts,js,mjs,cjs}'
      - '**/*.server.{ts,js,mjs,cjs}'
      - '**/*.cjs'
      - '**/server/**'
      - '.nvmrc'
      - '.node-version'
    keywords:
      - node
      - express
      - fastify
      - nestjs
      - hono
      - elysia
      - node:http
      - process
      - event loop
      - stream
      - backpressure
      - worker_threads
      - graceful shutdown
      - npm ci
      - unhandledRejection
      - Buffer
      - AbortController
---

# Node.js Standards

Default load: this file only. Pull `refs/runtime-safety.md`, `refs/async-errors.md`, `refs/tooling.md`, or `refs/testing.md` only when the task explicitly needs that depth.

Node.js owns runtime failure modes only: event-loop behaviour, promise rejection lifecycle in the process, streams/backpressure, worker threads, process signals, Buffer memory safety, dependency install mechanics, and boot-time environment loading. TypeScript rules stay in `standards/typescript/`; API contracts, security policy, auth, performance strategy, architecture, CI shape, and database persistence stay in their global or database refs and should be linked rather than copied.

## Priority: P0 — Runtime Safety

- Every promise is awaited, returned, or has an explicit rejection handler; no floating promises. Node exits on unhandled rejections by default on maintained modern releases, and unobserved rejections still make failures nondeterministic. `void` is allowed only for a documented fire-and-forget call that attaches `.catch()` or routes through a helper that centralizes rejection logging. Signal: a call returning a Promise on a statement line with no `await`, `return`, `.catch`, or approved fire-and-forget helper.
- Global `unhandledRejection` / `uncaughtException` handlers are last-resort logging plus graceful exit, never primary control flow, and never resume normal operation after `uncaughtException`. Catch errors where they occur. Signal: business logic such as retry, fallback, or response handling inside a `process.on('uncaughtException')` handler, or a handler that logs and keeps serving indefinitely.
- Throws across callback, timer, and event boundaries are caught locally and converted to rejections or error events. Normal throws inside an `async` function become promise rejections; throws in later callbacks (`setTimeout`, `EventEmitter`, stream callbacks) escape the original `.catch()`. Signal: a `throw` inside a bare `setTimeout`, `emitter.on`, or stream callback with no try/catch or error propagation.
- Handle `SIGTERM` and `SIGINT` for graceful shutdown: fail readiness or stop accepting connections, drain in-flight work up to a fixed deadline, close DB/Redis/pool resources, then exit before the orchestrator kills the process. Signal: a long-lived server with no signal handler, no shutdown timeout, or `process.exit()` called inside a request handler.
- Never block the event loop on the request path. No synchronous CPU work such as large `JSON.parse`, `crypto.pbkdf2Sync`, compression, image transforms, and no sync fs such as `readFileSync` or `existsSync` in a hot handler; offload CPU work to `worker_threads` or a queue, and use async APIs for I/O. Signal: a `*Sync` call or tight CPU loop inside a request handler.
- Respect stream backpressure. Prefer `stream.pipeline()` or `stream/promises.pipeline()` for multi-stream flows so errors and cleanup propagate; `.pipe()` is acceptable only when error and cleanup paths are handled. Honour `write()` returning `false` and wait for `'drain'`. Signal: `a.pipe(b)` with no error handling, or `.write()` in a loop ignoring the return value.
- Use `Buffer.alloc` for buffers that may be read before full overwrite; use `Buffer.allocUnsafe` only when every byte is overwritten before any read, response, log, persistence, crypto/compression input, or serialization. Unsafe buffers can leak prior heap contents. Signal: `Buffer.allocUnsafe` or `allocUnsafeSlow` flowing to an external sink without a complete overwrite first.

## Priority: P0 — Supply Chain & Secrets

- Run a maintained LTS Node line in production; pin the runtime and package manager. Use the repo's mechanism (`engines.node`, `.nvmrc`, `.node-version`, Volta/asdf/mise, Docker base image, CI setup) plus `packageManager`/Corepack where applicable. Signal: no production Node pin, a pinned EOL major, or a CI/Docker runtime that can drift from local tooling.
- Use frozen lockfile installs in CI and production, never mutable installs. Use `npm ci`, `pnpm install --frozen-lockfile`, `yarn install --immutable`, or the repo's equivalent with a committed lockfile. Signal: `npm install` in a Dockerfile or CI step; missing/uncommitted lockfile; package-manager version not pinned where the repo relies on one.
- Secrets load from the environment or a secret manager, validated at boot, and fail fast. Never hardcode secrets and never commit `.env`. Signal: a literal key/token in source; required env read lazily mid-request with no startup check. Secret policy lives in `global/refs/security.md`; this is the Node loading mechanic.

## Priority: P1 — Conventions

- One module system, stated. Prefer ESM for new packages when tooling supports it, but do not mix `require` and `import` in the same package without an interop boundary. Signal: `require()` in an ESM package, or ad hoc mixed module syntax in runtime code.
- Structured logging with levels and request context for long-lived services; no `console.log` in production request paths; never log secrets or raw tokens. CLIs, scripts, and migrations may intentionally write to stdout/stderr. Logging itself must not block; use an async transport rather than sync writes in the hot path. Signal: `console.log` in a request handler or raw token values passed to logs.
- Every outbound I/O call is bounded by the client's supported timeout or cancellation mechanism. Use `AbortController`/`AbortSignal` for `fetch` and compatible SDKs; use driver-level query, statement, acquisition, or request timeouts for DBs and clients that do not support abort signals. Signal: external `fetch`, SDK, or DB call with no timeout, deadline, or cancellation path.
- **P1 (design):** keep handlers thin: parse and validate at the edge, push logic into services, and isolate third-party SDKs behind a thin wrapper so a breaking upgrade is contained. Layering detail lives in `global/refs/architecture.md`.

## Anti-Patterns

- Floating promises
- Bare `void` promises with no rejection path
- Continuing after `uncaughtException`
- Logic inside `uncaughtException` or `unhandledRejection` handlers
- `process.exit()` in a request handler
- Graceful shutdown with no deadline
- `*Sync` fs/crypto on the event loop
- `.pipe()` with no error handling
- `Buffer.allocUnsafe` without complete overwrite before external use
- Mutable installs in CI or production
- Secrets in source or committed `.env`
- `console.log` in production request paths
- Unbounded outbound I/O
- Ad hoc mixing of `require` and `import`

## References

Load only what the current task requires:

- [runtime-safety](refs/runtime-safety.md) — event loop budget, streams/backpressure, worker threads, Buffer safety, or graceful shutdown
- [async-errors](refs/async-errors.md) — promise rejection lifecycle, callback-boundary throws, global process handlers, or timeout/cancellation patterns
- [tooling](refs/tooling.md) — Node/package-manager pinning, frozen installs, environment boot validation, or structured logging setup
- [testing](refs/testing.md) — Node service, CLI, integration, or network-boundary tests

Do not load refs for ordinary TypeScript typing, API contract, auth, database, or general security work unless the task also touches the Node runtime mechanic.
