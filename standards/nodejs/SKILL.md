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

Default load: this file only. Pull `refs/runtime-safety.md`, `refs/async-errors.md`, `refs/tooling.md`, or `refs/testing.md` only when the task explicitly needs that depth.

Node.js owns runtime failure modes only: event-loop behaviour, promise rejection lifecycle in the process, streams/backpressure, worker threads, process signals, Buffer memory safety, dependency install mechanics, and boot-time environment loading. TypeScript rules stay in `standards/typescript/`; API contracts, security policy, auth, performance strategy, architecture, CI shape, and database persistence stay in their global or database refs and should be linked rather than copied.

## Priority: P0 — Runtime Safety

- Every promise is awaited, returned, or has an explicit rejection handler; no floating promises. Node exits on unhandled rejections by default, and unobserved rejections still make failures nondeterministic. `void` is allowed only for a documented fire-and-forget call that attaches `.catch()` or routes through a helper that centralizes rejection logging. Signal: a call returning a Promise on a statement line with no `await`, `return`, `.catch`, or approved fire-and-forget helper.
- Global `unhandledRejection` / `uncaughtException` handlers are last-resort logging plus graceful exit, never primary control flow, and never resume normal operation after `uncaughtException`. Catch errors where they occur. Signal: business logic such as retry, fallback, or response handling inside a `process.on('uncaughtException')` handler, or a handler that logs and keeps serving indefinitely.
- Throws across callback, timer, and event boundaries are caught locally and converted to rejections or error events. Normal throws inside an `async` function become promise rejections; throws in later callbacks (`setTimeout`, `EventEmitter`, stream callbacks) escape the original `.catch()`. Signal: a `throw` inside a bare `setTimeout`, `emitter.on`, or stream callback with no try/catch or error propagation.
- Handle `SIGTERM` and `SIGINT` for graceful shutdown: fail readiness or stop accepting connections, drain in-flight work up to a fixed deadline, close DB/Redis/pool resources, then exit before the orchestrator kills the process. Signal: a long-lived server with no signal handler, no shutdown timeout, or `process.exit()` called inside a request handler.
- Never block the event loop on the request path. No synchronous CPU work such as large `JSON.parse`, `crypto.pbkdf2Sync`, compression, image transforms, and no sync fs such as `readFileSync` or `existsSync` in a hot handler; offload CPU work to `worker_threads` or a queue, and use async APIs for I/O. Signal: a `*Sync` call or tight CPU loop inside a request handler.
- Respect stream backpressure. Prefer `stream.pipeline()` or `stream/promises.pipeline()` for multi-stream flows so errors and cleanup propagate; `.pipe()` is acceptable only when error and cleanup paths are handled. Honour `write()` returning `false` and wait for `'drain'`. Signal: `a.pipe(b)` with no error handling, or `.write()` in a loop ignoring the return value.
- Use `Buffer.alloc` for buffers that may be read before full overwrite; use `Buffer.allocUnsafe` only when every byte is overwritten before any read, response, log, persistence, crypto/compression input, or serialization. Unsafe buffers can leak prior heap contents. Signal: `Buffer.allocUnsafe` or `allocUnsafeSlow` flowing to an external sink without a complete overwrite first.

## Priority: P0 — Supply Chain & Secrets

- Run a maintained LTS Node line in production; pin the runtime and package manager. Use the repo's mechanism (`engines.node`, `.nvmrc`, `.node-version`, Volta/asdf/mise, Docker base image, CI setup) plus `packageManager`. Corepack is not bundled from Node 25 on: install it explicitly (`npm install -g corepack`) or use the package manager's own version pinning. Signal: no production Node pin, a pinned EOL major (20 or older), or a CI/Docker runtime that can drift from local tooling.
- Use frozen lockfile installs in CI and production, never mutable installs. Use `npm ci`, `pnpm install --frozen-lockfile`, `yarn install --immutable`, or the repo's equivalent with a committed lockfile. Signal: `npm install` in a Dockerfile or CI step; missing/uncommitted lockfile.
- Secrets load from the environment or a secret manager, validated at boot, and fail fast. Never hardcode secrets and never commit `.env`. Signal: a literal key/token in source; required env read lazily mid-request with no startup check. Secret policy lives in `global/refs/security.md`; this is the Node loading mechanic.

## Priority: P1 — Conventions

- **Native TypeScript.** Node 24 runs `.ts` files directly through type stripping (on by default; stable from 24.12). It only erases types: no type check, no `tsconfig.json`, and no `enum`, runtime `namespace`, or parameter properties. Keep `tsc --noEmit` in CI and set `erasableSyntaxOnly`. `--experimental-transform-types` is experimental and removed in Node 26 — do not depend on it. Signal: a `.ts` entry point that uses `enum` or `paths` aliases under plain `node`.
- **Env files.** Load local `.env` files with `node --env-file=.env` (or `--env-file-if-exists`) or `process.loadEnvFile()` instead of adding `dotenv`. Validate the result at boot like any other env source.
- **Built-ins.** Import core modules with the `node:` prefix (`node:fs/promises`). Use the global `fetch` before adding an HTTP client dependency.
- **Permission model.** Run scripts, build steps, and tools that need limited access with `--permission` plus explicit `--allow-fs-read` / `--allow-fs-write` grants. It limits mistakes by trusted code; it is not a sandbox for untrusted code.
- **Module system.** Prefer ESM for new packages. CommonJS code can `require()` a synchronous ES module (no top-level `await`), so a CJS consumer no longer forces a dual build. Do not mix `require` and `import` inside one ESM file; keep CJS interop at a clear boundary. Signal: `require()` in an ESM package, or `createRequire` used to dodge an ESM dependency.
- Structured logging with levels and request context for long-lived services; no `console.log` in production request paths; never log secrets or raw tokens. CLIs, scripts, and migrations may intentionally write to stdout/stderr. Logging itself must not block; use an async transport rather than sync writes in the hot path. Signal: `console.log` in a request handler or raw token values passed to logs.
- Every outbound I/O call is bounded by the client's supported timeout or cancellation mechanism. Use `AbortController`/`AbortSignal` for `fetch` and compatible SDKs; use driver-level query, statement, acquisition, or request timeouts for DBs and clients that do not support abort signals. Signal: external `fetch`, SDK, or DB call with no timeout, deadline, or cancellation path.
- **P1 (design):** keep handlers thin: parse and validate at the edge, push logic into services, and isolate third-party SDKs behind a thin wrapper so a breaking upgrade is contained. Layering detail lives in `global/refs/architecture.md`.

## Anti-Patterns

Each rule above names its own Signal; each ref ends with its full list. The ones reviewers miss most:

- Continuing after `uncaughtException`
- Graceful shutdown with no deadline
- `*Sync` fs/crypto on the event loop
- Unbounded outbound I/O

## References

Load only what the current task requires:

- [runtime-safety](refs/runtime-safety.md) — event loop budget, streams/backpressure, worker threads, Buffer safety, graceful shutdown, or Express hardening middleware
- [async-errors](refs/async-errors.md) — promise rejection lifecycle, callback-boundary throws, global process handlers, or timeout/cancellation patterns
- [tooling](refs/tooling.md) — Node/package-manager pinning, frozen installs, environment boot validation, or structured logging setup
- [testing](refs/testing.md) — Node service, CLI, integration, or network-boundary tests

Do not load refs for ordinary TypeScript typing, API contract, auth, database, or general security work unless the task also touches the Node runtime mechanic.
