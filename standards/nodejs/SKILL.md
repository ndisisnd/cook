---
name: nodejs
description: Node.js runtime standards for event loop safety, process lifecycle, streams/backpressure, Buffer memory safety, runtime pinning, package installs, environment loading, native TypeScript execution, and production logging. Use for Node service, CLI, worker, or server runtime implementation and review; co-loads with TypeScript when code is TypeScript.
metadata:
  targets: "Node.js 24 LTS (26 LTS from 2026-10-28) · Node 20 is EOL"
  last_reviewed: 2026-10-18
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
      - dotenv
---

# Node.js Standards

Target: Node.js 24 LTS. Node 26 becomes LTS on 2026-10-28; Node 20 reached end of life on 2026-04-30.

Default load: this file only. Pull `refs/runtime-safety.md`, `refs/async-errors.md`, `refs/tooling.md`, or `refs/testing.md` only when the task needs that depth.

Node.js owns runtime failure modes only: event loop, promise rejections, streams/backpressure, workers, signals, Buffer safety, installs, boot-time env. TypeScript → `standards/typescript/`; API, security, auth, performance, architecture, CI → `standards/global/`; persistence → `standards/database/`.

## Priority: P0 — Runtime Safety

- Every promise is awaited, returned, or has an explicit rejection handler; no floating promises. Node exits on unhandled rejections by default, and unobserved rejections still make failures nondeterministic. `void` is allowed only for a documented fire-and-forget call that attaches `.catch()` or routes through a helper that centralizes rejection logging. Signal: a call returning a Promise on a statement line with no `await`, `return`, `.catch`, or approved fire-and-forget helper.
- Global `unhandledRejection` / `uncaughtException` handlers are last-resort logging plus graceful exit, never primary control flow, and never resume normal operation after `uncaughtException`. Catch errors where they occur. Signal: business logic such as retry, fallback, or response handling inside a `process.on('uncaughtException')` handler, or a handler that logs and keeps serving indefinitely.
- Throws across callback, timer, and event boundaries are caught locally and converted to rejections or error events. Throws in `setTimeout`, `EventEmitter`, or stream callbacks escape the original `.catch()`.
- Handle `SIGTERM` and `SIGINT` for graceful shutdown: fail readiness or stop accepting connections, drain in-flight work up to a fixed deadline, close DB/Redis/pool resources, then exit before the orchestrator kills the process. Signal: no signal handler or shutdown timeout; `process.exit()` in a request handler.
- Never block the event loop on the request path. No synchronous CPU work such as large `JSON.parse`, `crypto.pbkdf2Sync`, compression, image transforms, and no sync fs such as `readFileSync` or `existsSync` in a hot handler; offload CPU work to `worker_threads` or a queue, and use async APIs for I/O.
- Respect stream backpressure. Prefer `stream.pipeline()` or `stream/promises.pipeline()` for multi-stream flows so errors and cleanup propagate; `.pipe()` is acceptable only when error and cleanup paths are handled. Honour `write()` returning `false` and wait for `'drain'`. Signal: `a.pipe(b)` with no error handling, or `.write()` in a loop ignoring the return value.
- Use `Buffer.alloc` for buffers that may be read before full overwrite; use `Buffer.allocUnsafe` only when every byte is overwritten before any read, response, log, persistence, crypto/compression input, or serialization. Unsafe buffers can leak prior heap contents. Signal: `Buffer.allocUnsafe` or `allocUnsafeSlow` flowing to an external sink without a complete overwrite first.

## Priority: P0 — Supply Chain & Secrets

- Run a maintained LTS Node line in production; pin the runtime and package manager (`engines.node`, `.nvmrc`, `.node-version`, Volta/asdf/mise, Docker base image, CI setup, plus `packageManager`). Corepack is not bundled from Node 25 on: install it explicitly (`npm install -g corepack`) or use the package manager's own version pinning. Signal: no production Node pin, a pinned EOL major, or CI/Docker drifting from local.
- Use frozen lockfile installs in CI and production, never mutable installs: `npm ci`, `pnpm install --frozen-lockfile`, `yarn install --immutable`, or the repo's equivalent with a committed lockfile.
- Secrets load from the environment or a secret manager, validated at boot, and fail fast. Never hardcode secrets and never commit `.env`. Signal: a literal key/token in source; required env read lazily mid-request with no startup check. Secret policy lives in `global/refs/security.md`; this is the Node loading mechanic.

## Priority: P1 — Conventions

- **Native TypeScript.** Node 24 runs `.ts` directly through type stripping (default; stable from 24.12). It only erases types: no type check, no `tsconfig.json`, no `enum`, runtime `namespace`, or parameter properties. Keep `tsc --noEmit` in CI; set `erasableSyntaxOnly`. `--experimental-transform-types` is removed in Node 26 — do not depend on it.
- Built-ins (`node:` prefix), env files, permission model, ESM/CJS, logging: `refs/tooling.md`.
- Every outbound I/O call is bounded by the client's supported timeout or cancellation mechanism. Use `AbortController`/`AbortSignal` for `fetch` and compatible SDKs; use driver-level query, statement, acquisition, or request timeouts for DBs and clients that do not support abort signals. Signal: external `fetch`, SDK, or DB call with no timeout, deadline, or cancellation path.
- **P1 (design):** keep handlers thin: parse and validate at the edge, push logic into services, isolate third-party SDKs behind a thin wrapper. See `global/refs/architecture.md`.

## References

Load only what the current task requires:

- [runtime-safety](refs/runtime-safety.md) — event loop budget, streams/backpressure, worker threads, Buffer safety, graceful shutdown, or Express hardening middleware
- [async-errors](refs/async-errors.md) — promise rejection lifecycle, callback-boundary throws, global process handlers, or timeout/cancellation patterns
- [tooling](refs/tooling.md) — Node/package-manager pinning, frozen installs, environment boot validation, or structured logging setup
- [testing](refs/testing.md) — Node service, CLI, integration, or network-boundary tests

Do not load refs for ordinary TypeScript typing, API, auth, database, or general security work.
