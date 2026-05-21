---
name: nextjs
description: Write and review modern Next.js App Router code with secure RSC boundaries, direct server data access, async route APIs, Server Actions, rendering/cache strategy, and legacy Pages Router awareness.
metadata:
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
      - hydration
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

## Invocation Protocol

When invoked directly as `/nextjs`, read this file first and apply the critical rules below before editing. Then read `standards/nextjs/_INDEX.md` and load only the additional `refs/*.md` entries whose file patterns or keywords match the task.

If both App Router and Pages Router signals appear, apply the Router Decision below before loading App Router-specific refs. For a Pages Router-only project, load `refs/pages-router.md` and treat App Router refs as informational unless the migration explicitly touches `app/`.

## Router Decision

App Router is the default for new work. If the project uses `pages/`, treat App Router rules as informational and load `refs/pages-router.md`; do not apply `app/` conventions, Server Components, or Server Actions to a Pages Router-only project.

## P0 - Server & Client Components

- App Router uses React Server Components by default. Keep pages and layouts as Server Components unless they need hooks, browser APIs, or event handlers.
- Push `'use client'` to interactive leaves such as buttons, forms, charts, and wrappers. Do not mark the tree root client-side.
- Compose Server Components through Client Component `children`; never import a Server Component into a Client Component.
- Server-to-Client props must be serializable: strings, numbers, booleans, plain objects, and arrays. Convert `Date` to strings and avoid functions, classes, `Map`, `Set`, and `Symbol` values except Server Actions marked `'use server'`.
- Never pass secrets, raw ORM models, or full DB objects to the client. Use DTOs and `server-only` for sensitive modules.
- Avoid browser-only values (`window`, `Date.now()`, layout reads) in initial render; defer with a mounted state when needed.

Detail -> `refs/server-components.md`

## P0 - Data Fetching & Access

- Fetch directly in async Server Components or call DB/service/DAL functions directly. Never fetch your own `/api` route from RSCs or server-side hooks.
- Pick cache behavior deliberately: `cache: 'force-cache'` for static data, `next: { revalidate: N }` for ISR, and `cache: 'no-store'` for request-time data.
- Parallelize independent work with `Promise.all()` and push slow fetches down behind `<Suspense>` instead of blocking the page root.
- Centralize secure data access in `services/`, `lib/data.ts`, or `dal/` modules with `import 'server-only'`.
- Verify auth inside every DAL function, transform raw DB/API data into DTOs, and wrap shared reads with React `cache()` where render-cycle deduplication is needed.
- Use Server Actions or Route Handlers as bridges for Client Components; Client Components must not import DAL modules.

Detail -> `refs/data-fetching.md`

## P0 - App Router Conventions

- `page.tsx` renders route UI; `layout.tsx` wraps children and persists across navigation; `loading.tsx` creates a Suspense boundary; `error.tsx` is a Client Component error boundary; `route.ts` defines server endpoints.
- In Next.js 15+, always `await` `params`, `searchParams`, `cookies()`, and `headers()`.
- Add `error.tsx` with `'use client'` and a `reset` prop for route segments that need local recovery.
- Use route groups `(auth)`, dynamic segments `[slug]`, catch-all segments `[...slug]`, private folders `_lib`, parallel routes `@modal`, and intercepting routes only when the structure calls for them.
- Keep route files thin: routing and composition live in `app/`; business logic belongs in features, widgets, services, DAL, or Server Actions.

Detail -> `refs/app-router.md`

## P0 - Security & Auth

- Store tokens only in `HttpOnly`, `Secure` cookies with `SameSite: 'Lax'` or `'Strict'`; never use `localStorage` or `sessionStorage` for tokens.
- Use `middleware.ts` for edge-side auth redirection, RBAC checks, and security headers. Do not rely on shared layouts for authorization.
- Validate every Server Action and Route Handler input with Zod or equivalent, verify `Origin`/`Referer` where CSRF matters, and run `auth()` inside the action or handler.
- Use `server-only` for modules with DB clients, secrets, or token verification. Guard sensitive objects with taint APIs where available.
- Escape user content; never use `dangerouslySetInnerHTML` without a sanitizer such as DOMPurify.
- Pass session state to clients, never raw tokens or full user records.

Detail -> `refs/security.md`

## P1 - Rendering & Caching

- Choose SSG, SSR, ISR, Streaming, or PPR from freshness and personalization requirements, not habit.
- Use `generateStaticParams` and `force-cache` for static content; use `revalidate`/`revalidatePath`/`revalidateTag` for periodic or on-demand freshness; use `no-store`, `cookies()`, or `headers()` for request-time data.
- Stream slow or dynamic regions with `<Suspense>` and `loading.tsx`; avoid root-level sequential awaits that blank the page.
- Know the four cache layers: Request Memoization, Data Cache, Full Route Cache, and Router Cache.
- In Next.js 16+, prefer Cache Components with `'use cache'`, `cacheLife()`, `cacheTag()`, `updateTag()`, and `revalidateTag()` where available.
- Do not cache user-specific data at route level; isolate it in dynamic streamed regions.

Detail -> `refs/rendering-and-caching.md`

## P1 - Server Actions

- Use Server Actions for mutations and form submissions without creating API endpoints.
- Define actions in `actions.ts` or other server-only modules; avoid actions defined inside components because closures add encryption overhead and serialization risk.
- Start action files or functions with `'use server'`, validate `FormData`, perform auth inside the action, mutate, then call `revalidatePath()` or `revalidateTag()`.
- Use `useActionState`, `useFormStatus`, `useTransition`, and `useOptimistic` for pending, non-form trigger, and optimistic UI flows.
- Use `redirect()` for success navigation, but do not catch it in `try/catch`.

Detail -> `refs/server-actions.md`

## Anti-Patterns

- `pages/` projects using App Router features or async default page components.
- `'use client'` at the app root, layouts, or pages when only a leaf needs interactivity.
- Server Components passing functions, `Date`, classes, `Map`, `Set`, raw ORM models, secrets, or full DB objects to Client Components.
- Client Components importing DAL, DB clients, `server-only` modules, or server-only environment values.
- Server Components or Pages Router data hooks fetching their own `/api` routes instead of calling services directly.
- Unawaited `params`, `searchParams`, `cookies()`, or `headers()` in Next.js 15+.
- Root-level sequential awaits that block page streaming when independent data can be parallelized or wrapped in `<Suspense>`.
- `localStorage`/`sessionStorage` token storage or raw tokens in Client Components.
- Unvalidated Server Action or Route Handler inputs and skipped auth checks inside mutations.
- Auth checks only in shared layouts instead of middleware, DAL, actions, or handlers.
- `dangerouslySetInnerHTML` without sanitization.
- Long-lived caches without tags, `router.refresh()` used as the primary server-data invalidation mechanism, or `unstable_cache` in Next.js 16+ when `'use cache'` is available.
- Runtime CSS-in-JS spread across RSC trees; prefer zero-runtime styling unless a Client wrapper is intentional.
- `<img>` without dimensions, Google Fonts CDN links, or metadata in `_document.tsx`.
- Client-side `useEffect` data fetching for server state when RSC, SWR, TanStack Query, or RTK Query is the right owner.
- Cross-slice imports, business logic in `page.tsx`, file-type folders inside FSD slices, and premature `entities/` extraction.

## References

Load only what the current task requires.

### P0 Detail

- [server-components](refs/server-components.md) - RSC/Client composition, serialization, `server-only`, hydration boundaries
- [data-fetching](refs/data-fetching.md) - fetch strategies, direct DB/service access, DAL, DTOs, auth-colocated data reads
- [app-router](refs/app-router.md) - file conventions, route groups, dynamic segments, parallel/intercepting routes, self-hosting
- [security](refs/security.md) - cookies, middleware auth/RBAC, CSP, CSRF, taint APIs, Server Action validation
- [pages-router](refs/pages-router.md) - legacy `pages/` routing, `getServerSideProps`, `getStaticProps`, API routes

### P1 Detail

- [rendering-and-caching](refs/rendering-and-caching.md) - SSG/SSR/ISR/Streaming/PPR, Suspense bailout, cache layers, invalidation
- [server-actions](refs/server-actions.md) - mutations, forms, `useActionState`, `useFormStatus`, optimistic updates, secure actions
- [styling-and-optimization](refs/styling-and-optimization.md) - Tailwind, CSS Modules, Ant Design wrappers, `next/image`, `next/font`, metadata, Core Web Vitals
- [testing](refs/testing.md) - Jest/Vitest, React Testing Library, Playwright, MSW

### P2 Detail

- [architecture](refs/architecture.md) - Feature-Sliced Design, thin pages, bundling, runtime selection, debugging
- [i18n](refs/i18n.md) - locale routing, next-intl, react-intl, next-translate legacy
- [state-management](refs/state-management.md) - URL state, server state, Zustand, Redux legacy
- [tooling](refs/tooling.md) - Turbopack, Docker standalone, bundle analysis, env validation, CI, upgrades, codemods
