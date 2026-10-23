---
last_reviewed: 2026-10-23
---

# Server Components

Use this ref when deciding Server vs Client boundaries, passing data across them, or debugging hydration and serialization failures.

## Defaults

- Components are Server Components by default and add no client JavaScript.
- A `'use client'` file pulls every module it imports into the client bundle. Place it on the smallest interactive leaf.
- Wrap slow async children in `<Suspense>`; use `loading.tsx` for route-level skeletons.

## Composition

A Client Component cannot import a Server Component. Pass it as `children` or another JSX prop.

```tsx
// app/dashboard/page.tsx (Server Component)
export default async function Dashboard() {
  const metrics = await getMetrics();
  return (
    <ClientTabs settings={<SettingsPanel />}>
      <MetricsTable data={metrics} />
    </ClientTabs>
  );
}
```

## Serialization Boundary

Server-to-Client props use React's RSC serialization, not JSON.

- Supported: primitives (including `bigint`, `undefined`, `Symbol.for()` symbols), `Array`, `Map`, `Set`, typed arrays, `ArrayBuffer`, `Date`, plain objects, Promises (read with `use()`), JSX, and Server Functions (`'use server'`).
- Forbidden: non-Server functions (inline `onClick`), class instances (including ORM models), null-prototype objects, unregistered symbols (`Symbol('x')`).
- Do not convert `Date`, `Map`, or `Set` to strings or arrays to cross the boundary; React serializes them.
- Arguments to `'use cache'` functions follow stricter rules: `refs/rendering-and-caching.md`.

```tsx
<Timeline createdAt={post.createdAt} tagCounts={tagCounts /* Map */} />   // good
<Comments commentsPromise={getComments(postId)} />                        // good: unwrap with use()
<ClientButton onClick={() => log('hit')} user={ormUser} />                // bad
```

## `server-only`

Add `import 'server-only'` to modules with DB clients, secrets, or token verification. Importing one from a Client Component fails the build.

## Hydration

- No `window`, `localStorage`, `Date.now()`, or random values in initial render when server and client can disagree. Browser-only reads: `react/refs/hooks.md` (Browser Storage In Hooks, `useSyncExternalStore`).
- Keep serialized server data minimal and deterministic.

## Anti-Patterns

- Secrets or full DB objects passed to Client Components.
- `useState` or `useEffect` in Server Components.
- Client Components importing Server Components directly.
