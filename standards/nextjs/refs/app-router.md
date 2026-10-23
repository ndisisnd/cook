---
last_reviewed: 2026-10-23
---

# App Router

Use this ref when creating routes, layouts, error/loading states, parallel/intercepting routes, Route Handlers, `proxy.ts`, or self-hosting-sensitive features.

## File Conventions

- `error.tsx` must be a Client Component. `global-error.tsx` replaces the root layout and renders its own `<html>` and `<body>`.
- Only the root `app/layout.tsx` has `<html>` and `<body>`.
- `default.tsx` is required for every parallel route slot (`@modal`); builds fail without it. Return `null` or call `notFound()`.
- `proxy.ts` (project root or `src/`) replaces `middleware.ts` in Next.js 16. Export `proxy`. It runs on the Node.js runtime only and cannot be configured; keep `middleware.ts` only if you need the Edge runtime. Without a `matcher` it runs on every request, including `_next/static`, `_next/image`, and `public/`; exclude those. Server Action calls are POSTs to the page route, so a matcher that skips the path skips them too. Security depth: `refs/security.md`.
- Default exports are required for `page`, `layout`, `template`, `loading`, `error`, `global-error`, `not-found`, `default`, and metadata image files. `route.ts` uses named HTTP-method exports (`GET`, `POST`).
- Route groups `(auth)` and private folders `_lib` do not change the URL. Colocate route-only code in the route folder.

## Async Route APIs

- Synchronous `params`, `searchParams`, `cookies()`, `headers()`, and `draftMode()` are removed in Next.js 16. Always `await`.
- Metadata image functions (`opengraph-image`, `icon`) receive `params` and `id` as Promises; `sitemap` receives `id` as a Promise. `generateImageMetadata` still receives sync `params`.
- Type props with generated helpers (`PageProps<'/blog/[slug]'>`, `LayoutProps`, `RouteContext`); run `next typegen` in CI.

```tsx
// app/blog/[slug]/page.tsx
export default async function Page(props: PageProps<'/blog/[slug]'>) {
  const { slug } = await props.params;
  return <Post slug={slug} />;
}
```

## Handlers, Auth Interrupts, After

- Secure every `route.ts` handler with auth, validation, and rate limiting.
- `forbidden()` (403) and `unauthorized()` (401) from `next/navigation` are still experimental: they need `experimental.authInterrupts: true`. Do not call them in the root layout or inside a `try/catch`.
- `after(cb)` from `next/server` runs work after the response. In Server Components, read `cookies()` / `headers()` before `after` and pass values in; reading them inside the callback throws. Handlers and Server Actions may read them inside.

## Self-Hosting

- `output: 'standalone'`: copy `public/` and `.next/static/` into the standalone directory.
- The default cache is per instance. For multiple instances, set a shared `cacheHandler` (legacy ISR / fetch cache) and `cacheHandlers` (`'use cache'`), for example backed by Redis. Set `NEXT_SERVER_ACTIONS_ENCRYPTION_KEY` so all instances share one Server Action key.
- `NEXT_PUBLIC_*` values are inlined at build time. Call `await connection()` before reading `process.env` when the value must be read at runtime.
- Image optimization works in Docker (uses `sharp`). Use a custom `loader` for an external image CDN at scale.

## Anti-Patterns

- Unawaited async route APIs.
- Parallel route slots without `default.tsx`.
- `<html>` or `<body>` in nested layouts.
- Route Handlers without auth, validation, and rate limiting.
