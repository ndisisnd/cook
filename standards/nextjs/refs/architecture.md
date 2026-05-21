# Architecture

Use this ref when organizing Next.js projects with Feature-Sliced Design, enforcing import boundaries, handling package compatibility, choosing runtime, or debugging build/hydration issues.

## When To Use FSD

Feature-Sliced Design adds boilerplate. Use it for projects expected to grow significantly, such as 20+ features. For small apps, prefer a simpler module-based structure while keeping pages thin.

## Layer Hierarchy

Code may import only from layers below it.

```text
App (app/) -> Widgets -> Features -> Entities -> Shared
```

```ts
// app/dashboard/page.tsx - thin page, imports only widgets/features
import { DashboardWidget } from '@/widgets/dashboard';

export default function DashboardPage() {
  return <DashboardWidget />;
}
```

## Directory Layout

```text
app/                 # App layer: routing and layouts
  (app)/
    page.tsx
  layout.tsx
  globals.css

src/
  widgets/           # compositional blocks
    header/
      ui/
      index.ts

  features/          # user interactions and scenarios
    auth-login/
      ui/
      model/         # Server Actions, schemas, state
      index.ts

  entities/          # reused business concepts
    product/
      ui/
      model/
      index.ts

  shared/            # business-agnostic utilities
    ui/
    lib/
    api/
      client.ts
      endpoints/
        orders.ts
    auth/
      index.ts
    config/
```

## Segment Names

Use semantic segment names inside slices.

| Segment | Purpose | Examples |
|---|---|---|
| `ui/` | visual components | `LoginForm.tsx`, `ProductCard.tsx` |
| `model/` | business logic, state, types | `actions.ts`, `store.ts`, `schema.ts` |
| `api/` | remote data interactions | `fetchProduct()`, `useProductQuery()` |
| `lib/` | helper functions | `formatCurrency.ts`, `dateUtils.ts` |
| `config/` | constants and configuration | `env.ts`, `constants.ts` |

Avoid generic `components`, `hooks`, or `services` folders inside slices when following FSD.

## Layer Responsibilities

1. App: Next.js routing files only. `page.tsx` and `layout.tsx` should be thin wrappers.
2. Widgets: assemble features and entities into blocks such as `Header` or `ProductList`.
3. Features: handle user scenarios such as `AuthByEmail` or `ToggleTheme`; contains forms and Server Actions.
4. Entities: reusable business domain concepts. Avoid anemic entities that are only data types.
5. Shared: UI kit, utilities, config, and simple API clients. No business logic.

## Entity Extraction Rules

- Start logic in `features/` or route-local modules.
- Move to `entities/` only when data or logic is reused across multiple different features.
- User session/token helpers often belong in `shared/auth` or `shared/session`, not `entities/user`.
- Simple CRUD endpoints without complex domain logic belong in `shared/api/endpoints/`.

## Placement

- Server Actions: `features/<feature>/model/actions.ts`.
- DAL: `entities/<entity>/model/dal.ts` only when the entity is truly reused; otherwise `features/*/model` or `shared/api`.
- Base UI: `shared/ui`.
- Feature-specific UI: `features/*/ui`.

## RSC Boundaries

This ref cross-references the single RSC boundary home: `refs/server-components.md`.

Apply those serialization and `'use client'` rules when designing FSD slices. A Client Component should not import server-only DAL modules across slice boundaries.

## Bundling And Package Compatibility

Packages using browser APIs fail in Server Components.

Symptoms:

- `ReferenceError: window is not defined`.
- `Module not found: Can't resolve 'fs'`.

Solutions:

```tsx
import dynamic from 'next/dynamic';

const NoSSRComponent = dynamic(() => import('@/components/heavy-lib'), {
  ssr: false,
});
```

```js
// next.config.js
module.exports = { serverExternalPackages: ['bcrypt'] };
```

Or wrap the library in a `'use client'` component.

For ESM/CommonJS compatibility, use `transpilePackages`.

```js
// next.config.js
module.exports = { transpilePackages: ['some-esm-package'] };
```

Analyze build size in Next.js 16.1+ with:

```bash
next experimental-analyze
# next experimental-analyze --output
```

CSS and polyfills:

- Use `import './styles.css'` or CSS Modules; avoid manual `<link>` tags.
- Do not load external polyfills such as polyfill.io. Next.js includes modern browser primitives by default.

## Runtime Selection

Use Node.js by default. Only use Edge if a specific latency or geographic distribution requirement is already established.

| Feature | Node.js (default) | Edge Runtime |
|---|---|---|
| Cold start | Good | Ultra-fast |
| API support | Full (`fs`, `crypto`, native APIs) | Limited Web APIs |
| Connectivity | Full TCP/UDP | Limited |
| Package support | High | Low; no native bindings |

```tsx
// Only if required
export const runtime = 'edge';
```

Before switching to Edge:

1. Does the project already use it?
2. Is every dependency Edge-compatible?
3. Is latency a critical blocker?

## Debugging

Next.js 16+ exposes an MCP endpoint for app-state inspection.

- Endpoint: `/_next/mcp`.
- Config before v16: `experimental: { mcpServer: true }`.
- Common tools: `get_errors`, `get_routes`, `get_page_metadata`, `get_logs`.

Build specific routes to isolate failures:

```bash
next build --debug-build-paths "/dashboard"
next build --debug-build-paths "/blog/[slug]"
```

Hydration errors usually come from browser-only APIs in render, invalid HTML nesting, or browser extensions. Use a mounted `useEffect` pattern for browser-only content.

## Architecture Checklist

- Do layer imports point only downward?
- Is `page.tsx` thin, with no business logic, `useEffect`, or direct fetch?
- Are RSC and Client boundaries explicit and serializable?
- Does each slice expose a public `index.ts` API?
- Are same-layer cross-slice imports avoided?

## Anti-Patterns

- Cross-slice imports in the same layer.
- Business logic in `page.tsx`.
- File-type folders instead of business-domain slices.
- Premature `entities/` creation.
- Client Components importing server-only DAL modules.
- Edge runtime selected without a concrete requirement and dependency audit.
