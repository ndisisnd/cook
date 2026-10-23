---
last_reviewed: 2026-10-23
---

# Styling And Optimization

Use this ref for Next.js-specific styling placement, `next/font`, `next/image`, scripts, metadata, and bundle size. Tailwind, `cn()`, SCSS, and general CSS rules live in `standards/css/`.

## Styling In Next.js

- Prefer Tailwind or CSS Modules: zero-runtime and RSC-compatible.
- Runtime CSS-in-JS (MUI/Emotion, styled-components, Chakra) forces `'use client'` across trees. Avoid by default.
- Global CSS: import in the root layout (`app/layout.tsx`) or `pages/_app.tsx`. Import component CSS Modules next to their component.
- Libraries that inject styles at runtime (Ant Design) need a `'use client'` registry that collects styles with `useServerInsertedHTML` and flushes them during SSR. Do not mix Ant Design with MUI or Bootstrap.

## Fonts

- Use `next/font` (`next/font/google` or `next/font/local`) instead of `<link>` tags. It self-hosts the font and removes layout shift.
- Apply the returned `className` or CSS `variable` on `<html>`/`<body>` in the root layout. Set `subsets`.

## Images

- Use `next/image`, never raw `<img>`. Set `width`/`height`, or `fill` with a sized parent. Set `sizes` for responsive images.
- Above-the-fold image: use `preload` (new in 16; `priority` is deprecated), or `loading="eager"` / `fetchPriority="high"`.
- Remote hosts: `images.remotePatterns` (protocol, hostname, pathname). `images.domains` is deprecated.
- Next.js 16 image defaults changed. Configure these when you need the old behavior:
  - `images.qualities` defaults to `[75]` only. A `quality` prop outside the list is coerced to the nearest entry; direct `/_next/image?q=` requests with other values return 400. Add every quality you use.
  - `images.minimumCacheTTL` defaults to 14400 (4 hours), was 60 seconds.
  - `images.imageSizes` no longer includes `16`.
  - `images.maximumRedirects` defaults to 3.
  - `images.dangerouslyAllowLocalIP` is `false`. Enable only on private networks; it carries SSRF risk.
  - Local images with a query string (`/photo.png?v=1`) need `images.localPatterns` with a matching `search`.
- `next/legacy/image` is deprecated. Use `next/image`.

```ts
// next.config.ts
images: {
  remotePatterns: [{ protocol: 'https', hostname: 'cdn.example.com', pathname: '/img/**' }],
  qualities: [50, 75],
},
```

## Metadata And Scripts

- Use the metadata API (`metadata`, `generateMetadata`), not `_document.tsx` or manual `<head>` tags. `params` is a `Promise` in 16.
- Load third-party scripts with `next/script`: `afterInteractive` for analytics, `lazyOnload` for chat/embeds, `beforeInteractive` only for critical scripts (root layout only).

## Bundle Size

- Analyze with `next analyze` (Turbopack) or `@next/bundle-analyzer` (Webpack). See `refs/architecture.md`.
- Keep heavy libraries out of Client Components. Use `next/dynamic` or `React.lazy` with Suspense for large non-initial UI.
- Static shell plus dynamic islands: Cache Components (`refs/rendering-and-caching.md`).
- `next build` no longer prints `size` or `First Load JS`. Measure with Lighthouse or field Core Web Vitals (LCP < 2.5s, CLS < 0.1, INP < 200ms).

## Anti-Patterns

- Runtime CSS-in-JS broadly in RSC trees.
- `<img>` without dimensions.
- Google Fonts CDN `<link>` tags instead of `next/font`.
- Metadata in `_document.tsx`.
- Third-party scripts inserted manually into `<head>`.
- `quality` values missing from `images.qualities`.
