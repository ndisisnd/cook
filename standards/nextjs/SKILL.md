---
name: nextjs
description: Write and review modern Next.js App Router code with secure RSC boundaries, direct server data access, async route APIs, Server Actions, rendering/cache strategy, and legacy Pages Router awareness.
metadata:
  targets: "Next.js 16.x (16.4 current) · React 19.x · Node.js 24 LTS recommended (Next minimum 20.9, EOL)"
  last_reviewed: 2026-10-23
  triggers:
    files:
      - 'app/**/*.tsx'
      - 'src/app/**/*.tsx'
      - 'app/**/*.jsx'
      - 'src/app/**/*.jsx'
      - 'app/**/page.tsx'
      - 'app/**/layout.tsx'
      - 'app/**/loading.tsx'
      - 'app/**/actions.ts'
      - 'src/app/**/actions.ts'
      - 'pages/**/*.tsx'
      - 'pages/**/*.ts'
      - 'proxy.ts'
      - 'middleware.ts'
      - '**/auth.ts'
      - '**/login/page.tsx'
      - '**/lib/data.ts'
      - '**/services/*.ts'
      - '**/dal/**'
      - '**/service.ts'
      - '**/*.css'
      - 'tailwind.config.ts'
      - '**/components/ui/*.tsx'
      - '**/*.test.{ts,tsx}'
      - 'cypress/**'
      - 'tests/**'
      - 'jest.config.*'
      - 'next.config.js'
      - 'next.config.ts'
      - 'package.json'
      - 'messages/*.json'
    keywords:
      - Next.js
      - App Router
      - Pages Router
      - Server Component
      - Client Component
      - Server Action
      - use client
      - use server
      - use cache
      - hydration
      - proxy
      - middleware
      - cache
      - revalidateTag
      - revalidatePath
      - force-cache
      - no-store
      - generateStaticParams
      - PPR
      - next/image
      - next/font
      - next-intl
      - Turbopack
---

# Next.js

Targets Next.js 16.x, React 19.x, Node.js 24 LTS (Next requires 20.9+, which is EOL). Generic React rules: `react/SKILL.md`.

Apply the rules below, then load only the `refs/*.md` that `_INDEX.md` matches. App Router is the default; for a `pages/`-only project load `refs/pages-router.md` and apply no `app/` rules.

## Cache Model Decision

Check `next.config.*` for `cacheComponents: true` before writing caching code. One model per project.

- **On** - data is dynamic by default. Cache with `'use cache'` + `cacheLife()` + `cacheTag()`. Do not export `dynamic`, `revalidate`, `fetchCache`, `dynamicParams`, `runtime`. Wrap request-time reads (`cookies()`, `headers()`, `searchParams`) in `<Suspense>`.
- **Off (legacy)** - cache with `fetch` options (`force-cache`, `next: { revalidate, tags }`) and segment config; no `'use cache'`.

Invalidation: `revalidateTag(tag, 'max')` (two arguments required in 16), `updateTag(tag)` and `refresh()` (Server Actions only), `revalidatePath(path)`.

## P0 - Server & Client Components

- Keep pages and layouts as Server Components unless they need hooks, browser APIs, or event handlers. Push `'use client'` to interactive leaves.
- Compose Server Components through Client Component `children`; never import one into a Client Component.
- Server-to-Client props must be React-serializable. Allowed: primitives, `bigint`, `Symbol.for()` symbols, plain objects, arrays, `Date`, `Map`, `Set`, typed arrays, Promises, JSX, and Server Functions. Forbidden: class instances, non-Server functions, unregistered symbols, and null-prototype objects.
- Never pass secrets or raw ORM/DB objects to the client. Use DTOs and `import 'server-only'`.
- Avoid browser-only or non-deterministic values (`window`, `Date.now()`, `Math.random()`) in initial render.

## P0 - Data Fetching & Access

- Fetch in async Server Components or call DAL/service functions directly. Never fetch your own `/api` route from server code.
- Use `server-only` DAL modules that verify auth, return DTOs, and dedupe with React `cache()`.
- Client Components reach the server only through Server Actions or Route Handlers.

## P0 - App Router Conventions

- `page.tsx` renders a route; `layout.tsx` persists across navigation; `loading.tsx` is a Suspense boundary; `error.tsx` is a Client Component error boundary; `route.ts` is an endpoint; `proxy.ts` (formerly `middleware.ts`) runs before routing.
- Always `await` `params`, `searchParams`, `cookies()`, `headers()`, `draftMode()`; sync access is removed in 16.
- Every parallel route slot (`@modal`) needs a `default.tsx`; builds fail without it.
- Exports: prefer named, except where Next.js requires default (`page`, `layout`, `template`, `loading`, `error`, `global-error`, `not-found`, `default`, metadata image files, `next.config.ts`). `route.ts` exports named HTTP methods; `proxy.ts` exports `proxy`.
- Keep route files thin; logic lives in services, DAL, or actions.

## P0 - Security & Auth

- Use `proxy.ts` (Node.js runtime only) for optimistic auth redirects and security headers. It does not replace auth checks in DAL, Server Actions, and Route Handlers.
- Every Server Action is a public POST endpoint: start with `'use server'`, validate input with Zod or equivalent, then authenticate and authorize inside the action.
- Set auth cookies with `(await cookies()).set(...)` using `httpOnly`, `secure`, `sameSite`. Token storage: `react/SKILL.md`.
- Only `NEXT_PUBLIC_*` env vars reach the client.

## P1 - Rendering & Caching

- Stream slow or dynamic regions with `<Suspense>`; avoid root-level sequential awaits.
- Do not cache user-specific data in shared caches; pass request values as arguments instead of reading `cookies()` inside cached functions.

## P1 - Server Actions

- Define actions in `actions.ts` files marked `'use server'`; avoid inline actions that close over component scope.
- Flow: validate -> auth -> mutate -> `updateTag()` / `revalidateTag(tag, 'max')` / `revalidatePath()` -> return a minimal result or `redirect()`.
- Do not wrap `redirect()` in a `try/catch` that swallows it. Form hooks: `react/SKILL.md`.

## Anti-Patterns

- `'use client'` at the app root, layouts, or pages when only a leaf is interactive.
- Unvalidated or unauthenticated Server Actions and Route Handlers; auth only in layouts or proxy.
- New `middleware.ts` or `export function middleware` on Next.js 16; use `proxy.ts`.
- `router.refresh()` as primary invalidation.
- `<img>` over `next/image`; Google Fonts `<link>` over `next/font`.

## References

Load only what the task needs.

### P0 Detail

- [server-components](refs/server-components.md) - RSC/Client composition, serialization, `server-only`, hydration
- [data-fetching](refs/data-fetching.md) - fetch per cache model, DAL, DTOs
- [app-router](refs/app-router.md) - file conventions, `proxy.ts`, self-hosting
- [security](refs/security.md) - proxy auth, CSRF, CSP
- [pages-router](refs/pages-router.md) - legacy `pages/`

### P1 Detail

- [rendering-and-caching](refs/rendering-and-caching.md) - cache models, streaming
- [server-actions](refs/server-actions.md) - mutations, forms, cache refresh
- [styling-and-optimization](refs/styling-and-optimization.md) - CSS, `next/image`, `next/font`
- [testing](refs/testing.md) - Jest/Vitest, Playwright, MSW

### P2 Detail

- [architecture](refs/architecture.md) - FSD, bundling, runtime
- [i18n](refs/i18n.md) - locale routing, next-intl
- [state-management](refs/state-management.md) - URL state, stores
- [tooling](refs/tooling.md) - Turbopack, ESLint, Docker, upgrades
