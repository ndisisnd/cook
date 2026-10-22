---
last_reviewed: 2026-10-18
---

# Node.js Tooling

CI topology lives in `global/refs/cicd.md`; secret policy in `global/refs/security.md`.

## Runtime And Package Manager Pinning

- Pin a maintained LTS Node for production via `engines.node`, `.nvmrc`, `.node-version`, Volta/asdf/mise, Docker base image, or CI setup. Keep Docker and CI aligned with the repo pin. Signal: `.nvmrc` says one major, Docker/CI another.
- Pin the package manager with `packageManager` or the repo's toolchain config. Corepack is not bundled from Node 25 on: install it explicitly (`npm install -g corepack`) in CI and Docker, or use the package manager's own pinning. Signal: pnpm/yarn repo with no committed version, or a Node 25+ image assuming `corepack enable` works.

## Frozen Installs

- Immutable installs in CI and production (`npm ci`, `pnpm install --frozen-lockfile`, `yarn install --immutable`) with the committed lockfile. No `npm install` in Dockerfiles or CI without a documented reason.

## Environment Boot Validation

- Validate required env vars at boot, before accepting traffic or running jobs; fail fast, with no insecure defaults for production secrets. Signal: required env first read lazily in a handler or job body.
- `.env` is local development only; never commit it.
- Load with `node --env-file=.env` (`--env-file-if-exists` when optional) or `process.loadEnvFile()`; no `dotenv` needed.
- Validate with a schema, e.g. Zod 4: `z.object({ DATABASE_URL: z.url() }).parse(process.env)`.

## Structured Logging

- Structured logs with levels and request/job context for long-lived services; stay vendor-neutral (`pino`, `winston`) unless the repo has a standard.
- No `console.log` in production request paths; CLIs, migrations, and scripts may write to stdout/stderr.
- Never log secrets, raw tokens, or full authorization headers.
- No blocking transports on hot paths. Signal: sync file or network logging during request handling.

## Permission Model And Modules

- **Permission model.** Run scripts, build steps, and tools that need limited access with `--permission` plus explicit `--allow-fs-read` / `--allow-fs-write` grants. It limits mistakes by trusted code; it is not a sandbox for untrusted code.
- **Module system.** Prefer ESM for new packages. CommonJS code can `require()` a synchronous ES module (no top-level `await`), so a CJS consumer no longer forces a dual build. Do not mix `require` and `import` inside one ESM file; keep CJS interop at a clear boundary. Signal: `require()` in an ESM package, or `createRequire` used to dodge an ESM dependency.
- **Built-ins.** Use the `node:` prefix for core modules and global `fetch` before adding an HTTP client.
