# Tooling And Upgrades

Use this ref when configuring Next.js build tooling, Turbopack, Docker standalone output, bundle analysis, environment validation, lint/CI, telemetry, or major-version upgrades.

## Build And Dev

- Use Turbopack (`next dev --turbo`) for faster incremental development builds when supported.
- Use Webpack where legacy config or package compatibility requires it.
- Run `next build` as the production correctness gate.
- Mandate TypeScript checking and Next.js-aware ESLint in CI.

```json
// package.json
"scripts": {
  "dev": "next dev --turbo",
  "lint": "next lint",
  "build": "next build"
}
```

## Docker And Standalone Output

Use standalone output for self-contained Docker deployment.

```js
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  experimental: {
    turbo: {},
  },
};

module.exports = nextConfig;
```

```dockerfile
# Dockerfile snippet
FROM node:18-alpine AS base
# ... install and build
CMD ["node", "server.js"]
```

For complete self-hosting cache and asset-copy notes, see `refs/app-router.md`.

## Environment Variables

- Server-only vars are read at runtime on the server.
- `NEXT_PUBLIC_*` vars are exposed to the browser and baked into the JS bundle.
- Validate environment at startup with Zod or equivalent.

```ts
// lib/env.ts
import { z } from 'zod';

const envSchema = z.object({
  DATABASE_URL: z.string().url(),
  NEXT_PUBLIC_API_URL: z.string().url(),
});

export const env = envSchema.parse(process.env);
```

## Bundle Analysis

- Inspect with `@next/bundle-analyzer` or the built-in analyzer in supported Next.js versions.
- Remove unused dependencies and avoid accidental runtime CSS-in-JS/client-only packages in Server Components.
- For Next.js 16.1+, use `next experimental-analyze`.

## CI/CD

Pipeline shape — fail-fast gating order, required checks before merge, per-job
timeouts and run cancellation — is vendor-neutral; see `global/refs/cicd.md`.
Next.js specifics:

- Run `next build` as the production correctness gate, alongside lint, typecheck, and test.
- Cache `.next/cache` for faster builds.
- Keep telemetry policy explicit; opt out with `next telemetry disable` if privacy requires it.
- Use structured loggers such as Pino or Winston for production; do not ship raw `console.log`.

## Upgrade Protocol

Use this when migrating Next.js to a new major version.

1. Check current `next`, `react`, and `react-dom` versions in `package.json`.
2. Plan an incremental path; do not skip majors, such as v13 -> v14 -> v15.
3. Run official codemods first: `npx @next/codemod@latest <transform> <path>`.
4. Update dependencies.
5. Verify async APIs: `params`, `searchParams`, `cookies()`, and `headers()` are awaited in Next.js 15+.
6. Audit `fetch` caching; v15 defaults changed, so add `force-cache` where static behavior is required.
7. Run `next dev` and `next build` after each incremental step.
8. Report codemod failures and manual fixes.

```bash
npm install next@latest react@latest react-dom@latest
npm install --save-dev @types/react@latest @types/react-dom@latest
```

Breaking-change notes:

- `next-async-request-api` codemod addresses async request APIs, but manual fixes may remain.
- React and React DOM versions must match Next.js peer requirements, such as React 19 for Next.js 15.
- Hydration and Turbopack errors must be fixed before completing the migration.

## Debugging Cross-Reference

Route-specific build debugging and Next.js MCP details live in `refs/architecture.md`.

## Anti-Patterns

- `npm run start` for development instead of `next dev`.
- Uninspected bundle growth.
- Custom ESLint rules replacing `eslint-plugin-next` for Next.js-specific checks.
- Raw `console.log` in production.
- Major-version skipping.
- Manual breaking-change fixes before official codemods.
- Assumed caching behavior after upgrades.
- Async default page functions in Pages Router.
