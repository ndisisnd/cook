---
last_reviewed: 2026-10-23
---

# State Management

Use this ref for Next.js-specific state concerns: URL state with `next/navigation`, server state in RSCs, and per-request client stores. Generic rules for Context, Zustand, Jotai, Redux Toolkit, TanStack Query, and SWR live in `react/refs/state-management.md`.

## Which State Owner

| State type | Owner in Next.js |
|---|---|
| Shareable UI state (search, filters, pagination, tabs) | URL search params |
| Server data | Server Components; TanStack Query / SWR only for live client data |
| Complex client-only UI state | Zustand or Jotai inside Client Components |
| Local UI state | `useState` near the consumer |
| Existing Redux app | Redux Toolkit with a per-request store |

Do not copy server data into client stores to share it. Fetch it in RSCs and pass DTOs down.

## URL State

Client side: update the URL with `useRouter().replace` inside a transition.

```tsx
'use client';
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import { useTransition } from 'react';

export function SearchInput() {
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const { replace } = useRouter();
  const [isPending, startTransition] = useTransition();

  function handleSearch(term: string) {
    const params = new URLSearchParams(searchParams);
    if (term) params.set('query', term);
    else params.delete('query');
    startTransition(() => replace(`${pathname}?${params.toString()}`));
  }

  return (
    <input
      defaultValue={searchParams.get('query') ?? ''}
      onChange={(e) => handleSearch(e.target.value)}
      aria-busy={isPending}
    />
  );
}
```

Server side: read `searchParams` from page props and key the `<Suspense>` boundary by the query so the fallback shows on change.

```tsx
import { Suspense } from 'react';

export default async function Page(props: PageProps<'/search'>) {
  const sp = await props.searchParams;
  const query = typeof sp.query === 'string' ? sp.query : '';
  const page = Number(sp.page) || 1;
  return (
    <Suspense key={`${query}-${page}`} fallback={<ResultsSkeleton />}>
      <Results query={query} page={page} />
    </Suspense>
  );
}
```

Wrap every `useSearchParams()` consumer in `<Suspense>` (see `refs/rendering-and-caching.md`).

## Per-Request Stores

Module-level stores are shared across requests on the server and leak user data. Create stores per request inside a Client Component provider.

```tsx
// app/store-provider.tsx
'use client';
import { createContext, useContext, useState, type ReactNode } from 'react';
import { useStore } from 'zustand';
import { createCartStore, type CartState, type CartStore } from '@/lib/cart-store';

const CartStoreContext = createContext<CartStore | null>(null);

export function CartStoreProvider({ children, initial }: { children: ReactNode; initial: CartState }) {
  const [store] = useState(() => createCartStore(initial));
  return <CartStoreContext value={store}>{children}</CartStoreContext>;
}

export function useCartStore<T>(selector: (s: CartState) => T): T {
  const store = useContext(CartStoreContext);
  if (!store) throw new Error('useCartStore must be used inside CartStoreProvider');
  return useStore(store, selector);
}
```

Build the store with a factory (`createStore` from `zustand/vanilla`, returning `(initial) => store`) so each request gets a fresh instance.

Redux Toolkit follows the same shape: export `makeStore()`, create it once per provider with `useState(() => makeStore())` or `useRef<AppStore | null>(null)`, and pass it to `<Provider store={...}>`.

Persisted client stores (`persist` middleware) differ between server and first client render. Gate persisted values until after hydration.

## Anti-Patterns

- Module-level (global) stores on the server.
- Server data copied into client stores.
- Duplicating the same state in the URL and `useState`.
- `useSearchParams()` consumers without `<Suspense>`.
- String-concatenated query strings instead of `URLSearchParams`.
- Pages Router `next-redux-wrapper` / `HYDRATE` patterns in new App Router code.
