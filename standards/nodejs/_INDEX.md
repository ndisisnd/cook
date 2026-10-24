<!-- Hand-maintained routing index. Keep in sync with SKILL.md frontmatter. -->
# nodejs Skills Index

## File Match (auto-check against the file you are editing)

| Skill | File pattern | Keywords |
| ----- | ------------ | -------- |
| **nodejs** | `server.{ts,js,mjs,cjs}`, `app.{ts,js,mjs,cjs}`, `**/*.server.{ts,js,mjs,cjs}`, `**/*.cjs`, `**/server/**`, `.nvmrc`, `.node-version` | nodejs, expressjs, express.js, fastify, nestjs, hono, elysia, node:http, process, event loop, readable stream, backpressure, worker_threads, graceful shutdown, npm ci, unhandledRejection, Buffer.from, dotenv, node:fs, --env-file, permission model, require(esm), pino, winston |
| nodejs → tooling ref | `package.json`, `.nvmrc`, `.node-version`, `.npmrc`, `.env.example` | npm ci, lockfile, dotenv, --env-file, pino, winston |
| nodejs → testing ref | `**/*.test.{ts,js,mjs,cjs}`, `**/*.spec.{ts,js,mjs,cjs}`, `**/__tests__/**`, `content:node:test`, `content:supertest` | node:test, supertest |

> Concept refs (`runtime-safety`, `async-errors`) have no row and no file pattern: they always load under a bare `--nodejs`. Structural refs (`tooling`, `testing`) carry file patterns.

> Load `<SKILLS>/nodejs/SKILL.md` for Node runtime work.
> Load `<SKILLS>/nodejs/refs/runtime-safety.md` for event-loop, stream, buffer, worker, shutdown, or Express hardening middleware work.
> Load `<SKILLS>/nodejs/refs/async-errors.md` for promise rejection, callback-boundary, timeout, or global-handler work.
> Load `<SKILLS>/nodejs/refs/tooling.md` for Node/package-manager pinning, installs, env boot validation, or logging setup.
> Load `<SKILLS>/nodejs/refs/testing.md` for Node service, CLI, integration, or network-boundary testing.
