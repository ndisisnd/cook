# Data Fetching And Data Access

Use this ref when fetching data, choosing cache behavior for a fetch, centralizing secure data access, or building DTO-returning DAL functions.

## App Router Fetch Strategies

Fetch data directly in Server Components with `async`/`await`.

| Strategy | Use For | Directive |
|---|---|---|
| Static | build-time/shared content | `fetch(url, { cache: 'force-cache' })` |
| Revalidated | periodically fresh content | `fetch(url, { next: { revalidate: 60 } })` |
| Dynamic | personalized or request-time data | `fetch(url, { cache: 'no-store' })` or dynamic APIs like `cookies()` |

For Pages Router projects, use `getServerSideProps`, `getStaticProps`, and `getStaticPaths` instead; see `refs/pages-router.md`.

## Direct Access

Do not fetch your own `/api` routes from Server Components or server-side data hooks. Call the database, service layer, or DAL directly.

```tsx
// lib/db.ts
export async function getPosts() {
  'use cache';
  return db.posts.findMany();
}

// app/posts/page.tsx
export default async function Page() {
  const posts = await getPosts();
  return <PostList posts={posts} />;
}
```

## Parallel Fetching

Use `Promise.all()` to prevent waterfalls when resources are independent.

```tsx
const [user, posts] = await Promise.all([getUser(id), getPosts()]);
```

If a fetch is slow and not required for the static shell, move it into a child Server Component behind `<Suspense>` instead of blocking the page root.

## Client-Side Fetching

Use SWR, TanStack Query, or React Query for live or user-specific data that does not require SEO and must update client-side.

```tsx
'use client';
import useSWR from 'swr';

function UserProfile() {
  const { data, error } = useSWR('/api/user', fetcher);
  if (error) return <div>Failed to load</div>;
  if (!data) return <div>Loading...</div>;
  return <div>Hello {data.name}!</div>;
}
```

## Revalidation

Use on-demand revalidation after mutations.

- `revalidatePath('/path')` purges cache for a route path.
- `revalidateTag('key')` purges cache by tag.
- In Next.js 16 Cache Components, use `updateTag(tag)` for immediate same-request updates and `revalidateTag(tag)` for background stale-while-revalidate.

See `refs/rendering-and-caching.md` for the rendering/cache decision table and cache-layer detail.

## Data Access Layer

Centralize database and upstream API reads in `services/`, `lib/data.ts`, or `dal/` modules so security, authorization, and DTO mapping are consistent.

### Workflow

1. Create a DAL module with `import 'server-only'`.
2. Verify auth inside every DAL function with `await auth()` or project equivalent.
3. Transform raw DB/API results into plain DTOs before returning.
4. Wrap shared reads with React `cache()` to deduplicate within a render cycle.
5. Use taint APIs where available to prevent accidental sensitive-object exposure.

### Secure Direct Database DAL

```ts
// lib/dal/users.ts
import 'server-only';
import { cache } from 'react';
import { auth } from '@/auth';
import { db } from '@/db';

export const getUser = cache(async (id: string) => {
  const session = await auth();
  if (!session) throw new UnauthorizedError();

  const user = await db.user.findUnique({ where: { id } });
  if (!user) throw new NotFoundError();

  return { id: user.id, name: user.name, email: user.email };
});
```

## Pattern A: API Gateway / BFF

Use when Next.js is a frontend for a separate backend such as NestJS or Go.

```ts
import 'server-only';
import { cache } from 'react';
import { getToken } from '@/lib/auth';

const API_URL = process.env.API_GATEWAY_URL;

export const getProjectDetails = cache(async (id: string) => {
  const token = await getToken();

  const res = await fetch(`${API_URL}/projects/${id}`, {
    headers: { Authorization: `Bearer ${token}` },
    next: { tags: [`project-${id}`] },
  });

  if (!res.ok) {
    if (res.status === 404) return null;
    throw new Error('Upstream API Failed');
  }

  const data = await res.json();

  return {
    title: data.attributes.title,
    isActive: data.status === 'published',
  };
});
```

## Pattern B: Direct Database

Use when Next.js owns the data.

```ts
import 'server-only';
import { cache } from 'react';
import { verifySession } from '@/lib/auth';
import { db } from '@/lib/prisma';

export const getSafeUserProfile = cache(async (slug: string) => {
  const session = await verifySession();

  const canView = session.role === 'admin' || session.slug === slug;
  if (!canView) throw new Error('Unauthorized');

  const data = await db.user.findUnique({ where: { slug } });
  if (!data) return null;

  return {
    id: data.id,
    name: data.name,
    avatar: data.avatarUrl,
  };
});
```

## Limitations

Client Components cannot import DAL files. Use Server Actions or Route Handlers as bridges.

## Anti-Patterns

- Fetching `localhost/api` or any own `/api` route from Server Components or server-side hooks.
- Auth checks outside the DAL while DAL functions return privileged data.
- Returning raw ORM model instances instead of DTOs.
- Importing DAL files into Client Components.
- Root-level slow awaits that should be streamed or parallelized.
- `useEffect` for server data fetching when RSC, SWR, or TanStack Query owns the problem.
