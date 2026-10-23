---
last_reviewed: 2026-10-23
---

# Rendering And Caching

Use this ref when selecting static, cached, or request-time rendering, streaming, PPR, cache directives, or invalidation.

## Pick One Cache Model

Read `next.config.*` first. Never mix the two models in one project.

| Need | `cacheComponents: true` | `cacheComponents` off (legacy) |
|---|---|---|
| Static, rarely changes | `'use cache'` + `cacheLife('max')` | `fetch(url, { cache: 'force-cache' })`, `generateStaticParams()` |
| Periodic refresh | `'use cache'` + `cacheLife('hours')` | `next: { revalidate: N }` or `export const revalidate = N` |
| Invalidate on mutation | `cacheTag('posts')` + `updateTag` / `revalidateTag` | `next: { tags: ['posts'] }` + same APIs |
| Per-request / personalized | Default (uncached); wrap in `<Suspense>` | `cache: 'no-store'`, `cookies()`, `headers()`, `dynamic = 'force-dynamic'` |
| Static shell + dynamic holes | Default (PPR) | Not available; stream with `<Suspense>` |

Cache Components rules:

- Enable with `cacheComponents: true`. Next.js 16.4 docs also set `partialPrefetching: true` explicitly; leaving it unset logs a warning. Set it `false` only while migrating an app that adopted Cache Components earlier.
- Remove segment configs `dynamic`, `revalidate`, `fetchCache`, `dynamicParams`, and `runtime` (build errors). `experimental_ppr`, `experimental.ppr`, `experimental.dynamicIO`, and `experimental.useCache` are removed.
- `generateStaticParams` must return at least one param; an empty array errors.
- `'use cache'` functions must be async; arguments and return values must be serializable.
- Do not read `cookies()`, `headers()`, or `searchParams` inside `'use cache'`. Read them outside and pass values as arguments.
- Set `cacheLife()` in every cached scope. Profiles: `'seconds'`, `'minutes'`, `'hours'`, `'days'`, `'weeks'`, `'max'`, `'default'`.
- Cache Components need the Node.js runtime.
- `new Date()`, `Date.now()`, `Math.random()`, and `crypto.randomUUID()` during prerender fail the build. Wrap the reader in `<Suspense>` and `await connection()` (from `next/server`) first, or move it to a Client Component.
- `'use cache'` entries are in-memory per deployment. Use `'use cache: remote'` or a `cacheHandlers` config when entries must be shared across instances.
- `unstable_cache` and `fetch` cache options keep working; migrating is optional.

```tsx
// lib/posts.ts
import 'server-only';
import { cacheLife, cacheTag } from 'next/cache';

export async function getPosts() {
  'use cache';
  cacheLife('hours');
  cacheTag('posts');
  return db.post.findMany({ orderBy: { createdAt: 'desc' } });
}
```

Static shell with streaming holes: wrap each request-time child (for example one that reads `cookies()`) in its own `<Suspense fallback={...}>`. The legacy model streams the same way; only the data function changes to `fetch(url, { next: { revalidate: 3600, tags: ['posts'] } })`.

## Invalidation

| API | Where | Semantics |
|---|---|---|
| `updateTag(tag)` | Server Actions only | Expire now; next read waits for fresh data (read-your-writes) |
| `revalidateTag(tag, 'max')` | Server Actions, Route Handlers | Stale-while-revalidate; profile argument required in 16 |
| `revalidatePath(path)` | Server Actions, Route Handlers | Invalidate a route path |
| `refresh()` | Server Actions only | Refresh the client router without touching tags |

Use `updateTag` after user mutations the user must see. Use `revalidateTag(tag, 'max')` from webhooks and where brief staleness is fine.

## Streaming

- With Cache Components, pass the `params` / `searchParams` promise into the `<Suspense>`-wrapped child and `await` it there. With `generateStaticParams` and no Partial Prefetching, await `params` outside `<Suspense>` to keep ISR for unlisted paths.
- `useSearchParams()` always needs a `<Suspense>` boundary in prerendered routes.
- With Cache Components, `usePathname()`, `useParams()`, and `useSelectedLayoutSegment(s)()` suspend when the path has unknown dynamic params; wrap the reading leaf in `<Suspense>` or the build fails.
- Waterfalls: `react/refs/performance.md`.

## Navigation State

With Cache Components, recently visited routes stay mounted in `<Activity mode="hidden">`. `useState` and form inputs persist on back-navigation; effects clean up and re-run. Reset dropdowns, dialogs, and post-submit form state explicitly.

## Anti-Patterns

- Mixing `'use cache'` with `fetch` cache options or segment `revalidate`.
- `revalidateTag(tag)` without the second argument.
- `updateTag` or `refresh` called outside a Server Action.
- `cookies()` / `headers()` inside a `'use cache'` scope.
- Long-lived caches without `cacheTag()` or fetch tags.
- `router.refresh()` as primary invalidation.
