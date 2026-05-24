# Node.js Tooling

Use this ref for runtime pinning, package-manager pinning, frozen installs, environment validation at boot, and production logging setup. CI pipeline topology lives in `global/refs/cicd.md`; secret policy lives in `global/refs/security.md`.

## Runtime And Package Manager Pinning

- Pin a maintained LTS Node version for production. Acceptable mechanisms include `engines.node`, `.nvmrc`, `.node-version`, Volta/asdf/mise config, Docker base image, and CI setup. Signal: local, CI, and production can drift across Node majors.
- Pin the package manager with `packageManager` where Corepack-compatible, or with the repo's equivalent toolchain config. Signal: pnpm/yarn repo without a committed package-manager version.
- Keep Docker and CI versions aligned with the repo pin. Signal: `.nvmrc` says one major and Docker/CI uses another.

## Frozen Installs

- Use immutable installs in CI and production: `npm ci`, `pnpm install --frozen-lockfile`, `yarn install --immutable`, or equivalent.
- Commit the matching lockfile for the package manager. Signal: lockfile missing or ignored while CI installs dependencies.
- Do not use `npm install` in Dockerfiles or CI unless the repo has a documented reason. Pipeline ordering and broader gate policy live in `global/refs/cicd.md`.

## Environment Boot Validation

- Read and validate required environment variables at process boot, before accepting traffic or running jobs. Signal: required env is first read lazily in a request handler or job body.
- Fail fast on missing or invalid config. Do not substitute insecure defaults for production secrets.
- `.env` files are local development inputs only. Do not commit them; secret storage policy lives in `global/refs/security.md`.

```js
import { z } from 'zod';

const Env = z.object({
  NODE_ENV: z.enum(['development', 'test', 'production']),
  DATABASE_URL: z.string().url(),
});

export const env = Env.parse(process.env);
```

## Structured Logging

- Use structured logs with levels and request/job context for long-lived services. `pino` and `winston` are common choices; keep the guidance vendor-neutral unless the repo has a standard.
- Avoid `console.log` in production request paths. CLIs, migrations, and scripts may intentionally write to stdout/stderr.
- Never log secrets, raw tokens, or full authorization headers. The general sensitive-data policy lives in `global/refs/security.md`.
- Avoid blocking transports on hot paths. Signal: sync file writes or synchronous network logging during request handling.

## Anti-Patterns

- Floating Node version in production
- Package manager version not pinned
- `npm install` in CI or Dockerfile where a lockfile exists
- Missing lockfile for deployed code
- Env validation deferred until mid-request
- Committed `.env`
- Raw token values in logs
