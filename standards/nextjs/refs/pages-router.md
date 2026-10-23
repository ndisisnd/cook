---
last_reviewed: 2026-10-23
---

# Pages Router

Use this ref for legacy `pages/` apps. Never add App Router features (`'use client'`, Server Actions, `use cache`, async page components) to a Pages Router project. For a move to App Router, see `refs/app-router.md`.

## Rules

- Server hooks: `getServerSideProps` (request time), `getStaticProps` + `getStaticPaths` (build time). Type props with `InferGetServerSidePropsType<typeof getServerSideProps>`.
- Call services or the DB directly from those hooks. Never fetch your own `/api` routes from them.
- Return `{ notFound: true }` for missing data. Return only serializable props (no `Date`, `undefined`).
- Navigate with `useRouter()` from `next/router`, not `next/navigation`.
- Metadata goes in `next/head`, not `_document.tsx`.
- Global CSS imports only in `_app.tsx`; everywhere else use CSS Modules.
- API Routes live in `pages/api/`. Return consistent status codes and JSON error shapes.
- Keep page files thin: render a feature component and export server hooks only when SEO or auth needs SSR.
- Locale routing uses the `i18n` key in `next.config.js`.
- `next-redux-wrapper` / `HYDRATE` and per-request Zustand factories apply here only. See `refs/state-management.md`.

## Migration

- Next 16 needs Node 20.9+ and drops AMP, `serverRuntimeConfig`/`publicRuntimeConfig`, and `next lint`. Use env vars and ESLint/Biome directly.
- Pages Router and App Router can coexist. A route must exist in only one of them.
- Pages `middleware.ts` becomes `proxy.ts` (Node runtime only).
- Do not make Pages Router default exports `async`.

## Anti-Patterns

- Fetching own `/api` routes from SSR/SSG hooks.
- Global CSS outside `_app.tsx`.
- App Router features in Pages Router projects.
- Giant page files that mix route, UI, state, and business logic.
