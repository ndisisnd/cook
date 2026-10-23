---
last_reviewed: 2026-10-23
---

# Data Fetching And Data Access

Use this ref when choosing cache behavior for a read, centralizing secure data access, or building DTO-returning DAL functions.

## Fetch Strategy Per Cache Model

Apply the Cache Model Decision in `SKILL.md`. Full table: `refs/rendering-and-caching.md`.

| Need | `cacheComponents: true` | Legacy model |
|---|---|---|
| Static / shared | `'use cache'` + `cacheLife('max')` | `fetch(url, { cache: 'force-cache' })` |
| Periodic | `'use cache'` + `cacheLife('hours')` | `fetch(url, { next: { revalidate: 60 } })` |
| Per-request | Uncached by default; wrap in `<Suspense>` | `fetch(url, { cache: 'no-store' })` or `cookies()` |

`'use cache'` only works when `cacheComponents: true`. Pages Router: `refs/pages-router.md`.

## Direct Access

- Never fetch your own `/api` routes from Server Components; call the DAL or service layer directly.
- Parallelize independent reads and use `<Suspense>` for slow ones: `react/refs/performance.md` (Eliminate Data Waterfalls).
- Client-side fetching (TanStack Query, SWR) is only for live, user-specific data: `react/refs/state-management.md`.

## Revalidation

- `updateTag(tag)` - Server Actions only; immediate read-your-writes.
- `revalidateTag(tag, 'max')` - Server Actions or Route Handlers; stale-while-revalidate. The second argument is required.
- `revalidatePath('/path')` - invalidate a route path.

## Data Access Layer

Put DB and upstream reads in `services/`, `lib/data.ts`, or `dal/` modules.

1. Start the module with `import 'server-only'`.
2. Verify auth inside every DAL function, and check authorization against the specific resource (ownership, role).
3. Return minimal DTOs, never raw ORM rows.
4. Wrap shared reads in React `cache()` to dedupe within one render (`react/refs/performance.md`, React Server Components).

```ts
// lib/dal/users.ts
import 'server-only';
import { cache } from 'react';

export const getUserProfile = cache(async (slug: string) => {
  const session = await verifySession();
  if (!session) throw new UnauthorizedError();
  if (session.role !== 'admin' && session.slug !== slug) throw new ForbiddenError();

  const user = await db.user.findUnique({ where: { slug } });
  if (!user) return null;
  return { id: user.id, name: user.name, avatar: user.avatarUrl };
});
```

- Inside a `'use cache'` function, React `cache()` has an isolated scope. Pass data in as arguments.
- Do not call `cookies()` / `headers()` (or an auth helper that reads them) inside `'use cache'`. Authenticate outside and pass the user ID in.
- Backend-for-frontend: same shape (`server-only`, token read server-side, DTO mapping). Tag upstream fetches (`next: { tags }` legacy, `cacheTag()` with `'use cache'`).
- Throw typed errors (`NotFoundError`, `UnauthorizedError`) from the DAL; map them at the route boundary with `notFound()`, `redirect()`, or `error.tsx`.

## Anti-Patterns

- Fetching `localhost/api` or any own `/api` route from server code.
- DAL functions that return privileged data without an auth check.
- Importing DAL files into Client Components; use Server Actions or Route Handlers as the bridge.
