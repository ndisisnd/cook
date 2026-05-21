# Server Components

Use this ref when deciding Server Component vs Client Component boundaries, passing data across that boundary, or debugging hydration and serialization failures.

## RSC Defaults

App Router uses React Server Components by default.

- Fetch directly in async Server Components.
- Push `'use client'` to interactive leaf nodes only.
- Keep layouts and pages server-side unless they need hooks, browser APIs, or event handlers.
- Wrap slow async children in `<Suspense>` and use `loading.tsx` for route-level skeletons.
- Server Components add zero JavaScript to the client bundle; Client Components hydrate on the client.

## Composition

You cannot import a Server Component directly into a Client Component. Pass the Server Component as `children` instead.

```tsx
// app/dashboard/page.tsx (Server Component)
import { ClientTabs } from './client-tabs';

export default async function Dashboard() {
  const data = await db.metrics.findMany();
  return (
    <ClientTabs>
      <MetricsTable data={data} />
    </ClientTabs>
  );
}

// app/dashboard/client-tabs.tsx
'use client';
import { useState } from 'react';

export function ClientTabs({ children }: { children: React.ReactNode }) {
  const [tab, setTab] = useState(0);
  return <div>{tab === 0 ? children : <Settings />}</div>;
}
```

```tsx
// Page.tsx (Server Component)
import ClientWrapper from './ClientWrapper';
import ServerContent from './ServerContent';

export default function Page() {
  return (
    <ClientWrapper>
      <ServerContent />
    </ClientWrapper>
  );
}

// ClientWrapper.tsx (Client Component)
'use client';

export default function ClientWrapper({ children }: { children: React.ReactNode }) {
  return <div className="client-context">{children}</div>;
}
```

## Serialization Boundary

Props passed from Server Components to Client Components must be JSON-serializable.

### Forbidden Types

- Functions, except Server Actions exported from a `'use server'` file.
- `Date` objects; convert them with `.toISOString()` on the server.
- Class instances; methods are stripped, so pass plain objects.
- `Map`, `Set`, `Symbol`, and other complex non-JSON values.

### Patterns

```tsx
// Bad: Date object crosses the boundary.
<ClientComponent date={new Date()} />

// Good: convert dates before crossing.
<ClientComponent date={post.createdAt.toISOString()} />
```

```tsx
// Bad: event handlers cannot cross Server -> Client.
<ClientButton onClick={() => console.log('hit')} />;

// Good: keep browser event handlers in a Client Component.
'use client';
export function ClientButton() {
  return <button onClick={() => console.log('hit')}>...</button>;
}
```

```tsx
// Good: Server Actions are the function exception.
import { submitAction } from './actions';

<ClientForm action={submitAction} />;
```

## Security With `server-only`

Prevent accidental bundling of server-side logic, database clients, and API secrets into client-side JavaScript.

```bash
npm install server-only
```

```tsx
// lib/db.ts
import 'server-only';

export const db = new Database();
```

If a Client Component imports `lib/db.ts`, Next.js throws a build error.

## Hydration Rules

Do not read browser-only or non-deterministic values during initial render if the server and client can disagree.

- Avoid `window.innerWidth`, `localStorage`, `Date.now()`, and random values in initial render.
- Use a mounted `useEffect` pattern in Client Components when the value is browser-only.
- Keep serialized server data minimal and deterministic.

## Cross-Reference

Architecture uses this file as the single home of RSC boundary rules. See `refs/architecture.md` for FSD placement and package-boundary debugging.

## Quick Verification

- Are all Server-to-Client props serializable?
- Did you convert dates to strings on the server?
- Are async components limited to Server Components?
- Are sensitive modules protected with `server-only`?
- Is `'use client'` pushed to the smallest interactive leaf?

## Anti-Patterns

- Secrets or full DB objects passed to Client Components.
- `useState` or `useEffect` in Server Components.
- `'use client'` at the tree root.
- Client Components importing Server Components directly.
- Class instances, Dates, functions, `Map`, or `Set` crossing the RSC boundary.
