---
last_reviewed: 2026-10-23
---

# Architecture

Use this ref when organizing a Next.js project, enforcing import boundaries, handling package compatibility, choosing runtime, or debugging build/hydration issues.

## Structure

- Use Feature-Sliced Design (FSD) only for apps expected to grow past about 20 features. Smaller apps: module-based folders, thin pages.
- FSD layers import downward only: `app` -> `widgets` -> `features` -> `entities` -> `shared`. No same-layer cross-slice imports. Each slice exposes a public `index.ts`.
- Inside slices use semantic segments (`ui/`, `model/`, `api/`, `lib/`, `config/`). Do not create `components/`, `hooks/`, or `services/` folders.
- `app/` holds Next.js routing files only. `page.tsx` and `layout.tsx` stay thin wrappers: no business logic, direct fetch, or `useEffect`.
- Start logic in `features/` or route-local modules. Move to `entities/` only when several features reuse it. Session/token helpers belong in `shared/auth`, not `entities/user`. Plain CRUD endpoints belong in `shared/api/endpoints/`.
- Placement: Server Actions in `features/<feature>/model/actions.ts`; DAL in `features/*/model` or `shared/api` (use `entities/<entity>/model/dal.ts` only when truly reused); base UI in `shared/ui`.
- RSC and `'use client'` serialization rules live in `refs/server-components.md`. A Client Component must not import server-only DAL modules across slices.

## Server-Only Code

- Mark DAL, secrets, and DB modules with `import 'server-only'`. Mark browser-only modules with `import 'client-only'`. The build then fails on a wrong-side import.
- Packages that touch `window` fail in Server Components (`window is not defined`, `Can't resolve 'fs'`). Wrap them in a `'use client'` component, or load with `next/dynamic` and `ssr: false` (allowed only inside a Client Component).
- Do not hide Node-only imports in client bundles with `resolveAlias` stubs; refactor the import instead.

## Bundling

- Turbopack is the default bundler for `next dev` and `next build` in 16. A custom `webpack` config fails the build unless you pass `--webpack` (or `--turbopack` to ignore it).
- `serverExternalPackages: ['pkg']` keeps native or non-bundleable packages (for example `bcrypt`) out of the server bundle.
- `transpilePackages: ['pkg']` compiles untranspiled ESM/TS packages.
- `experimental.optimizePackageImports` trims barrel imports for icon/utility libraries.
- Analyze size: `next analyze` (Turbopack, 16.1+; `--output` writes `.next/diagnostics/analyze`). Webpack builds use `@next/bundle-analyzer` with `ANALYZE=true`. The old `experimental-analyze` name is gone.
- Move heavy render-only work (syntax highlighting, markdown, charts without interaction) into Server Components.
- Use `import './styles.css'` or CSS Modules, never manual `<link>` tags. Do not load polyfill.io-style polyfills.
- For lazy loading, use `next/dynamic`; the underlying rule is in `react/refs/performance.md`.

## Runtime Selection

- Default to Node.js. Use Edge only for an established latency or geography requirement with every dependency Edge-compatible.
- `proxy.ts` (renamed from `middleware.ts`) always runs on Node.js in 16 and cannot be configured. For Edge middleware, keep `middleware.ts`; do not rename it blindly.
- `export const runtime = 'edge'` is deprecated. Cache Components requires Node.js and rejects any `runtime` export; remove it before enabling `cacheComponents`.

## Debugging

- Next.js 16+ serves an MCP endpoint at `/_next/mcp` (tools: `get_errors`, `get_routes`, `get_page_metadata`, `get_logs`).
- Isolate a failing route: `next build --debug-build-paths "/blog/[slug]"`.
- Hydration errors come from browser-only APIs in render, invalid HTML nesting, or browser extensions. Hook rules are in `react/refs/hooks.md`.

## Anti-Patterns

- Cross-slice imports in the same layer.
- Business logic in `page.tsx`.
- File-type folders instead of business-domain slices.
- Premature `entities/`.
- Client Components importing server-only DAL modules.
- Edge runtime without a concrete requirement and dependency audit.
