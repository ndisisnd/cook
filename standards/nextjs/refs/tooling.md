---
last_reviewed: 2026-10-23
---

# Tooling And Upgrades

Use this ref when configuring Next.js build tooling, Turbopack, linting, Docker standalone output, bundle analysis, environment validation, CI, or version upgrades.

## Build And Dev

- Turbopack is the default bundler for `next dev` and `next build` in Next.js 16 (filesystem cache on by default). Do not add `--turbo` / `--turbopack` flags.
- Opt out with `--webpack` only when a custom `webpack` config or plugin cannot move to Turbopack. `next build` fails if a `webpack` config exists and you did not choose.
- Turbopack options live under the top-level `turbopack` key (not `experimental.turbo`).
- `next dev` writes to `.next/dev`, so `next dev` and `next build` can run concurrently.
- Next.js requires Node.js 20.9+ (EOL since 2026-04-30) and TypeScript 5.1+. Run Node.js 24 LTS in CI, Docker, and production.

```json
// package.json
"scripts": {
  "dev": "next dev",
  "build": "next build",
  "start": "next start",
  "lint": "eslint .",
  "typecheck": "next typegen && tsc --noEmit"
}
```

## Linting

`next lint` and the `eslint` key in `next.config` are removed in Next.js 16, and `next build` no longer lints. Run the ESLint CLI with a flat config. Migrate with `npx @next/codemod@canary next-lint-to-eslint-cli .`.

```js
// eslint.config.mjs
import { defineConfig } from 'eslint/config';
import nextVitals from 'eslint-config-next/core-web-vitals';
import nextTs from 'eslint-config-next/typescript';

export default defineConfig([...nextVitals, ...nextTs]);
```

`eslint-config-next@16` requires ESLint 9+ (ESLint 10 from `eslint-config-next@16.4.0`). It already bundles `eslint-plugin-react-hooks`; do not register it twice (`react/refs/tooling.md`).

## Docker And Standalone Output

Set `output: 'standalone'` in `next.config.ts`. Turbopack options go under the top-level `turbopack` key.

Base image: `node:24-alpine`; run `node server.js` from `.next/standalone` with `.next/static` and `public` copied in.

Self-hosting cache and asset notes: `refs/app-router.md`.

## Environment Variables

- Validate env at startup with Zod or equivalent in a `server-only` module. `NEXT_PUBLIC_*` inlining: `refs/app-router.md`.
- `serverRuntimeConfig` / `publicRuntimeConfig` are removed; use env vars.

## Bundle Analysis

- `next analyze` (Turbopack) opens an interactive analyzer of client and server bundles; `next analyze --output` writes results to `.next/diagnostics/analyze` without serving.
- `next build` no longer prints `First Load JS` sizes; measure with the analyzer and Core Web Vitals.

## CI/CD

Pipeline shape: `global/refs/cicd.md`. Next.js specifics: run `eslint`, typecheck, tests, and `next build` as separate gates (build no longer lints); cache `.next/cache`; set telemetry policy explicitly (`next telemetry --disable`).

## Upgrade Protocol

1. Read current `next`, `react`, `react-dom`, and `@types/react` versions.
2. Run `npx next upgrade` (Next.js 16.1+) or `npx @next/codemod@canary upgrade latest` from older versions.
3. The upgrade codemod migrates `turbopack` config, `next lint` -> ESLint CLI, `middleware` -> `proxy`, and `unstable_` prefixes. Run `npx @next/codemod@canary next-async-request-api .` separately if sync request APIs remain.
4. Review breaking changes the codemod does not fix: `revalidateTag` second argument, parallel route `default.tsx`, `next/image` defaults, removed AMP and runtime config.
5. Do not enable `cacheComponents` or `reactCompiler` merely to finish an upgrade; adopt them as separate changes.
6. Run `next dev`, `next build`, lint, and tests after each step; report codemod failures and manual fixes.

## Debugging

- `next build --debug-build-paths="app/blog/[slug]/page.tsx"` builds only matching routes (globs and `!` exclusions allowed).
- `next build --debug-prerender` gives readable prerender stack traces. Never deploy its output.
- The Next.js 16 dev server exposes an MCP endpoint at `/_next/mcp` (on by default). Connect agents through the `next-devtools-mcp` package; disable with `experimental.mcpServer: false`.

## Anti-Patterns

- `next dev --turbo`, `next lint`, or `experimental.turbo` on Next.js 16.
- Node.js 18 or 20 base images.
- Skipping official codemods before manual fixes.
