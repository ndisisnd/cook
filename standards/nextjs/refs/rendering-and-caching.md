# Rendering And Caching

Use this ref when selecting SSG, SSR, ISR, Streaming, PPR, Cache Components, fetch directives, or cache invalidation.

## Freshness Decision Table

Choose rendering and cache behavior from data freshness and personalization.

| Data freshness need | Strategy | Cache directive / API | Notes |
|---|---|---|---|
| Same for all users, changes rarely | SSG | `fetch(url, { cache: 'force-cache' })`, `generateStaticParams()` | Fastest; CDN/static shell |
| Same for all users, changes periodically | ISR | `fetch(url, { next: { revalidate: N } })`, `export const revalidate = N` | Background refresh after interval |
| Same for all users, invalidated by mutation | ISR + on-demand | `next: { tags: ['posts'] }`, `revalidateTag('posts')`, `revalidatePath('/posts')` | Tag cacheable reads and invalidate in Server Actions |
| Personalized or must be fresh per request | SSR / dynamic | `fetch(url, { cache: 'no-store' })`, `cookies()`, `headers()`, `export const dynamic = 'force-dynamic'` | Higher compute cost; stream slow regions |
| Static shell with dynamic personalized holes | PPR / Streaming | `cacheComponents: true`, `'use cache'`, `cacheLife()`, `<Suspense>` | Use Cache Components in Next.js 16+ |

See `refs/data-fetching.md` for DAL-level revalidation examples and `refs/server-actions.md` for mutation flows.

## Strategy Matrix

| Strategy | Ideal For | Data Freshness | TTFB | Scaling Risk |
|---|---|---|---|---|
| SSG | Marketing, docs, blogs | Build time | Instant (CDN) | None |
| ISR | E-commerce, CMS | Periodic | Instant (CDN) | Low |
| SSR | Dashboards, auth gates | Real-time request | Slower | Critical: one request equals one compute path |
| PPR | Personalized apps | Hybrid | Instant shell | Medium: streamed holes |

## Strategy Guide

### SSG

Use when content changes infrequently, all users see the same content, maximum performance matters, and scaling cost should be near zero.

```tsx
export async function generateStaticParams() {
  const posts = await getPosts();
  return posts.map((post) => ({ slug: post.slug }));
}

export default async function PostPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const post = await getPost(slug, { next: { revalidate: 3600 } });
  return <article>{post.title}</article>;
}
```

### SSR

Use when data must be fresh on every request or user-specific and cannot be cached.

SSR triggers include:

- `cookies()`, `headers()`, and request `searchParams`.
- `fetch(..., { cache: 'no-store' })`.
- `export const dynamic = 'force-dynamic'`.

### ISR

Use when content updates periodically but not in real time.

- Time-based: `export const revalidate = 3600`.
- Fetch-based: `fetch(url, { next: { revalidate: 3600 } })`.
- On-demand: `revalidatePath('/posts')` or `revalidateTag('posts')` from Server Actions or webhooks.

### Streaming

Wrap slow async components in `<Suspense>` so the shell can render before all data is ready.

```tsx
export default function Page() {
  return (
    <div>
      <Header />
      <Suspense fallback={<Skeleton />}>
        <UserSection />
      </Suspense>
      <Suspense fallback={<Skeleton />}>
        <DataSection />
      </Suspense>
    </div>
  );
}

async function UserSection() {
  const user = await fetchUser();
  return <Profile user={user} />;
}
```

### PPR And Cache Components

Use PPR for a static shell with dynamic regions in one HTTP response. In Next.js 16+, enable Cache Components.

```ts
// next.config.ts
const nextConfig = {
  cacheComponents: true,
};

export default nextConfig;
```

```tsx
async function BlogPosts() {
  'use cache';
  cacheLife('hours');
  const posts = await db.posts.findMany();
  return <PostList posts={posts} />;
}
```

Content boundaries:

- Static: synchronous pure computations prerendered at build time.
- Cached: async data that does not need request-fresh reads; use `'use cache'`.
- Dynamic: cookies, headers, and search params; wrap in `<Suspense>`.

Cache life options include `'default'`, `'hours'`, `'days'`, `'max'`, or an inline object.

```tsx
cacheLife({
  stale: 3600,
  revalidate: 7200,
  expire: 86400,
});
```

Constraints:

- Do not use `cookies()` or `headers()` inside `'use cache'`; pass values as arguments when they must be part of the key.
- Cache Components require Node.js; Edge runtime is not supported.
- Use `connection()` from `next/server` to force request-time execution for non-deterministic values.

## Cache Layers

| Layer | Where | Control |
|---|---|---|
| Request Memoization | Server render lifecycle | React `cache()` |
| Data Cache | Server, persistent | `'use cache'`, `fetch` cache options, `revalidateTag()` |
| Full Route Cache | Server output | Static prerendering, ISR, PPR shell |
| Router Cache | Client memory | `router.refresh()` |

Invalidate with tags or paths after mutations.

```ts
// app/posts/actions.ts
'use server';
import { revalidateTag } from 'next/cache';

export async function createPost(data: FormData) {
  await db.post.create({ data: { title: data.get('title') as string } });
  revalidateTag('posts');
}

// app/posts/page.tsx
async function getPosts() {
  return fetch('/api/posts', { next: { tags: ['posts'], revalidate: 60 } });
}
```

In Next.js 16 Cache Components:

- `updateTag(tag)` provides immediate invalidation within the same request.
- `revalidateTag(tag)` performs background stale-while-revalidate.

## Static Shell Pattern

Make the page structure static and stream dynamic content.

```tsx
// app/dashboard/page.tsx
export default function Dashboard() {
  return (
    <div>
      <header>
        <Logo />
        <Navigation />
      </header>

      <main>
        <Suspense fallback={<ProfileSkeleton />}>
          <UserProfile />
        </Suspense>

        <Suspense fallback={<ChartSkeleton />}>
          <LiveChart />
        </Suspense>
      </main>

      <Footer />
    </div>
  );
}
```

Benefits: faster perceived load, parallel fetching, lower server load, and better CDN hit rates.

## Avoid SSR Waterfalls

Sequential root awaits block all HTML.

```tsx
// Bad: all fetches block initial HTML.
export default async function Page() {
  const user = await fetchUser();
  const permissions = await checkAuth();
  const data = await fetchExternal();
  return <Dashboard user={user} permissions={permissions} data={data} />;
}
```

Push fetches down into streamed children or parallelize independent reads.

## ISR Plus Streaming

```tsx
// app/product/[id]/page.tsx
export const revalidate = 3600;

export default function ProductPage({ params }) {
  return (
    <div>
      <ProductImages id={params.id} />
      <ProductDescription id={params.id} />

      <Suspense fallback={<StockSkeleton />}>
        <LiveStockInfo id={params.id} />
      </Suspense>

      <Suspense fallback={<ReviewsSkeleton />}>
        <RecentReviews id={params.id} />
      </Suspense>
    </div>
  );
}
```

## Suspense Bailout Rules

Some hooks force a client-side rendering bailout for static routes unless wrapped in `<Suspense>`.

```tsx
// Bad: entire page can become CSR.
'use client';
import { useSearchParams } from 'next/navigation';
function SearchBar() { /* ... */ }

// Good: wrap the client hook user.
import { Suspense } from 'react';
export default function Page() {
  return (
    <Suspense fallback={<Loading />}>
      <SearchBar />
    </Suspense>
  );
}
```

| Hook | Suspense Required? |
|---|---|
| `useSearchParams()` | Yes, in static routes |
| `usePathname()` | Yes, in dynamic routes unless `generateStaticParams` is used |
| `useParams()` | No |
| `useRouter()` | No |

## Runtime Note

Use `runtime = 'edge'` only for a proven low-latency/geographic need and Edge-compatible dependencies. See `refs/architecture.md` for the runtime selection matrix.

## Anti-Patterns

- SSR for static content.
- Root awaits in `page.tsx` that should be streamed or parallelized.
- `typeof window`, `Date.now()`, or browser-only values in initial render.
- Long-lived caches without `cacheTag()` or fetch tags.
- `router.refresh()` as primary server-data invalidation instead of targeted tags or paths.
- `unstable_cache` in Next.js 16+ when `'use cache'` and `cacheLife()` are available.
