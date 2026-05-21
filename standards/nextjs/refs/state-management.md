# State Management

Use this ref when choosing between URL state, server-cache state, client stores, Zustand, Redux, Context, or local component state in Next.js.

## Which State Tool

Default to the narrowest state owner that preserves behavior.

| State type | Default owner | Use when |
|---|---|---|
| Shareable or persistent UI state | URL params | Search, filters, pagination, tabs, modals that should be linkable |
| Server data | RSC fetch, SWR, TanStack Query, or RTK Query | Data comes from server and needs cache/revalidation/loading semantics |
| Complex client-only UI state | Zustand or Jotai in Client Components | Cross-component UI state that is not server data |
| Simple local UI state | `useState` near consumer | Form drafts, dropdowns, toggles |
| Existing large Redux app | Redux Toolkit / existing Redux stack | Preserve current architecture; migrate incrementally |

Do not put server state into client stores just to share it. Fetch in RSCs or use a server-state library.

## URL State

Use URL state for shareable filters, search queries, pagination, sorting, tabs, and modals.

```tsx
'use client';
import { useSearchParams, useRouter } from 'next/navigation';

function SearchFilter() {
  const searchParams = useSearchParams();
  const router = useRouter();

  function updateQuery(term: string) {
    const params = new URLSearchParams(searchParams.toString());
    params.set('q', term);
    router.replace(`?${params.toString()}`);
  }

  return <input onChange={(e) => updateQuery(e.target.value)} />;
}
```

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

    startTransition(() => {
      replace(`${pathname}?${params.toString()}`);
    });
  }

  return (
    <div className="relative">
      <input
        type="text"
        placeholder="Search..."
        defaultValue={searchParams.get('query')?.toString()}
        onChange={(e) => handleSearch(e.target.value)}
      />
      {isPending && <div className="absolute right-3 top-3 animate-spin">...</div>}
    </div>
  );
}
```

In Server Components, read `searchParams` from props and key Suspense boundaries by query values.

```tsx
import { Suspense } from 'react';
import { fetchFilteredData } from '@/lib/data';
import DataList from '@/components/DataList';

export default async function Page({ searchParams }: { searchParams: Promise<{ query?: string; page?: string }> }) {
  const params = await searchParams;
  const query = params.query || '';
  const currentPage = Number(params.page) || 1;

  return (
    <main>
      <h1>Search Results</h1>
      <Suspense key={query + currentPage} fallback={<Skeleton />}>
        <DataList query={query} page={currentPage} />
      </Suspense>
    </main>
  );
}
```

## Server State

Use SWR, TanStack Query, or RTK Query for client-side server cache needs. Do not sync server data into `useState` manually.

```tsx
const { data, error } = useSWR('/api/user', fetcher, {
  refreshInterval: 30000,
});
```

## Zustand

Use Zustand for complex client-only UI state. Keep subscriptions atomic and export custom selector hooks.

```tsx
// store.ts - minimal Zustand store
import { create } from 'zustand';

export const useCartStore = create<CartState>()((set) => ({
  items: [],
  addItem: (item) => set((s) => ({ items: [...s.items, item] })),
}));
```

```tsx
// src/store/useUserStore.ts
import { create } from 'zustand';

interface UserState {
  name: string;
  age: number;
  actions: {
    setName: (name: string) => void;
    incrementAge: () => void;
  };
}

const useUserBase = create<UserState>((set) => ({
  name: '',
  age: 0,
  actions: {
    setName: (name) => set({ name }),
    incrementAge: () => set((state) => ({ age: state.age + 1 })),
  },
}));

export const useUserName = () => useUserBase((state) => state.name);
export const useUserAge = () => useUserBase((state) => state.age);
export const useUserActions = () => useUserBase((state) => state.actions);
```

Hydration-safe client stores should gate browser-only persisted values.

```tsx
// src/hooks/useHasHydrated.ts
import { useState, useEffect } from 'react';

export function useHasHydrated() {
  const [hasHydrated, setHasHydrated] = useState(false);
  useEffect(() => setHasHydrated(true), []);
  return hasHydrated;
}
```

For Pages Router server-initialized Zustand, use a store factory and Context Provider so each request gets a fresh store instance.

```tsx
// src/store/useStore.ts
import { createStore } from 'zustand';

export const createMyStore = (initState: any) => {
  return createStore((set) => ({
    ...initState,
    // actions...
  }));
};
```

```tsx
// src/store/Provider.tsx
import { createContext, useContext, useRef } from 'react';
import { createMyStore } from './useStore';

const StoreContext = createContext(null);

export const StoreProvider = ({ children, initialState }) => {
  const storeRef = useRef();
  if (!storeRef.current) {
    storeRef.current = createMyStore(initialState);
  }
  return <StoreContext.Provider value={storeRef.current}>{children}</StoreContext.Provider>;
};

export const useStore = (selector) => {
  const store = useContext(StoreContext);
  return store(selector);
};
```

```tsx
// pages/_app.tsx
import { StoreProvider } from '@/store/Provider';

export default function App({ Component, pageProps }) {
  return (
    <StoreProvider initialState={pageProps.initialZustandState}>
      <Component {...pageProps} />
    </StoreProvider>
  );
}
```

## Redux Legacy And RTK

If a project already uses Redux, do not add another state library casually. Prefer Redux Toolkit for new Redux code and migrate incrementally.

Core rules:

- Use `createSlice` and `configureStore`; avoid manual action creators and reducers.
- Keep store state minimal and derive with selectors.
- Treat actions as events, not setters.
- Put logic in reducers or thunks instead of components.
- Never put promises, symbols, functions, or other non-serializable values into Redux state.
- Use `useSelector` and `useDispatch` hooks; avoid `connect` HOC for new work.
- Define typed `RootState` and `AppDispatch`.

App Router per-request store:

```tsx
// src/lib/store.ts
import { configureStore } from '@reduxjs/toolkit';
import authReducer from '@/features/auth/authSlice';

export const makeStore = () => {
  return configureStore({ reducer: { auth: authReducer } });
};

export type AppStore = ReturnType<typeof makeStore>;
export type RootState = ReturnType<AppStore['getState']>;
export type AppDispatch = AppStore['dispatch'];
```

```tsx
// src/app/StoreProvider.tsx
'use client';
import { useRef } from 'react';
import { Provider } from 'react-redux';
import { makeStore, AppStore } from '@/lib/store';

export default function StoreProvider({ children }: { children: React.ReactNode }) {
  const storeRef = useRef<AppStore>();
  if (!storeRef.current) storeRef.current = makeStore();
  return <Provider store={storeRef.current}>{children}</Provider>;
}
```

Pages Router projects can use `next-redux-wrapper` and handle `HYDRATE` in reducers. Prefer RTK Query for server-state fetching instead of manual `useEffect` or thunks.

```tsx
// src/store/index.ts
import { configureStore } from '@reduxjs/toolkit';
import { createWrapper } from 'next-redux-wrapper';
import authReducer from './authSlice';

export const makeStore = () =>
  configureStore({
    reducer: {
      auth: authReducer,
    },
  });

export const wrapper = createWrapper(makeStore);
```

```tsx
// src/store/authSlice.ts
import { createSlice } from '@reduxjs/toolkit';
import { HYDRATE } from 'next-redux-wrapper';

export const authSlice = createSlice({
  name: 'auth',
  initialState: { user: null },
  reducers: {},
  extraReducers: (builder) => {
    builder.addCase(HYDRATE, (state, action: any) => {
      return {
        ...state,
        ...action.payload.auth,
      };
    });
  },
});
```

```tsx
// pages/profile.tsx
import { wrapper } from '../store';

export const getServerSideProps = wrapper.getServerSideProps(
  (store) => async (context) => {
    await store.dispatch(fetchUser(context.params.id));
    return { props: {} };
  },
);
```

```tsx
// src/features/api/apiSlice.ts
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({ baseUrl: '/api' }),
  endpoints: (builder) => ({
    getUsers: builder.query({ query: () => '/users' }),
  }),
});

export const { useGetUsersQuery } = apiSlice;
```

## URL vs Local State

| State Type | Storage Location | Shareable? | Example |
|---|---|---|---|
| Search/filter | URL params | Yes | `?q=laptop&sort=price_asc` |
| Pagination | URL params | Yes | `?page=3` |
| Tabs/modals | URL params optional | Yes | `?tab=specs` |
| Form input | Local state | No | uncommitted text |
| UI toggles | Local state | No | dropdown open |
| Global UI | Context/Zustand | No | theme, sidebar open |

## Anti-Patterns

- Global store for simple local state.
- Large objects in state causing broad re-renders.
- `useEffect` for server data fetching.
- Server state in client stores.
- Duplicating state in both URL and `useState`.
- Missing `<Suspense>` around `useSearchParams()` consumers in static routes.
- String-concatenated URLs instead of `URLSearchParams`.
- Zustand hooks that subscribe to the entire store.
- Static global Redux stores in SSR.
