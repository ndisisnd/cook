# React State Management

## Choosing the Right Tool

| Scope | Tool |
|---|---|
| Local UI toggle | `useState` |
| Complex local state machine | `useReducer` |
| Low-frequency global (theme, locale, auth) | Context API |
| Small shared atoms | Jotai |
| High-frequency or cross-app global | Zustand (small–medium) / Redux Toolkit (large) |
| Server / async data | TanStack Query or SWR |
| Shareable URL state | URL Search Params |

Never sync server data into `useState` manually — let TanStack Query or SWR own the cache.

## Context API

Split State and Dispatch contexts so that components reading only dispatch do not re-render when state changes.

```tsx
const CountStateCtx = createContext<number | null>(null);
const CountDispatchCtx = createContext<React.Dispatch<Action> | null>(null);

function CountProvider({ children }: { children: ReactNode }) {
  const [count, dispatch] = useReducer(reducer, 0);
  return (
    <CountStateCtx.Provider value={count}>
      <CountDispatchCtx.Provider value={dispatch}>
        {children}
      </CountDispatchCtx.Provider>
    </CountStateCtx.Provider>
  );
}
```

Use Context for low-frequency data (theme, locale, auth session). For state that changes on every keystroke or scroll event, use Zustand or Redux instead.

When a provider passes an object, array, or function as `value`, memoize it or split the context. A recreated provider value re-renders every consumer even when the meaningful data did not change:

```tsx
function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const logout = useCallback(() => setUser(null), []);
  const value = useMemo(() => ({ user, logout }), [user, logout]);

  return <AuthCtx.Provider value={value}>{children}</AuthCtx.Provider>;
}
```

## Jotai

Use Jotai for small independent atoms where colocated reads/writes are clearer than a central store. Keep atoms minimal, derive values with derived atoms, and do not put server cache or secrets in atoms.

```tsx
const filterAtom = atom('all');
const filteredItemsAtom = atom((get) => filterItems(get(itemsAtom), get(filterAtom)));
```

## Zustand

Minimal boilerplate. No Provider required. Subscribe to slices to prevent unnecessary re-renders.

```tsx
import { create } from 'zustand';

interface AuthStore {
  user: User | null;
  login: (user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  login: (user) => set({ user }),
  logout: () => set({ user: null }),
}));

// Subscribe to a slice — only re-renders when `user` changes
const user = useAuthStore((s) => s.user);
```

Add `devtools` + `persist` middleware when needed:

```tsx
import { devtools, persist } from 'zustand/middleware';

export const useSettingsStore = create<SettingsStore>()(
  devtools(
    persist((set) => ({ theme: 'light', setTheme: (t) => set({ theme: t }) }), {
      name: 'settings',
    })
  )
);
```

Never persist tokens, JWTs, or secrets in Zustand, Redux, `localStorage`, or `sessionStorage`. Persist non-sensitive preferences only; auth tokens belong in `HttpOnly` cookies.

## Redux Toolkit

Use for large apps that need time-travel debugging, complex middleware, or a strict unidirectional data flow across many teams.

```tsx
import { createSlice, configureStore } from '@reduxjs/toolkit';

const cartSlice = createSlice({
  name: 'cart',
  initialState: { items: [] as CartItem[] },
  reducers: {
    addItem: (state, action: PayloadAction<CartItem>) => {
      state.items.push(action.payload); // Immer allows mutation here
    },
    removeItem: (state, action: PayloadAction<string>) => {
      state.items = state.items.filter((i) => i.id !== action.payload);
    },
  },
});

export const { addItem, removeItem } = cartSlice.actions;

export const store = configureStore({ reducer: { cart: cartSlice.reducer } });
```

Redux Toolkit guardrails:

- Use feature slices and selectors; keep `useSelector` granular so broad object selection does not re-render unrelated UI.
- Reducers must stay pure. Immer-style mutation is allowed only inside RTK reducers.
- Do not put non-serializable values in state or actions unless explicitly configured and isolated.
- Store minimal state; derive filtered/sorted/projected values in selectors.
- Use RTK Query for Redux-owned server data instead of hand-rolled fetch state.

## TanStack Query (React Query)

Own the server-state lifecycle: fetching, caching, background revalidation, and mutations.

Important defaults and design rules:

- Queries are stale by default; set `staleTime` intentionally to avoid surprise refetches.
- Stale queries refetch on mount, window focus, and reconnect by default.
- Inactive queries remain cached until `gcTime` expires.
- Failed queries retry by default; override retries for non-idempotent or user-blocking flows.
- Structural sharing keeps stable references when JSON-compatible data has not changed.
- Query keys must include every variable that changes the result: `['users', { orgId, page, filters }]`.
- Mutations must invalidate, update, or remove every affected query key.

```tsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

function UserProfile({ userId }: { userId: string }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetch(`/api/users/${userId}`).then((r) => r.json()),
    staleTime: 5 * 60 * 1000,
  });

  if (isLoading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;
  return <div>{data.name}</div>;
}

function UpdateUser({ userId }: { userId: string }) {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (patch: Partial<User>) =>
      fetch(`/api/users/${userId}`, { method: 'PATCH', body: JSON.stringify(patch) }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['user', userId] }),
  });

  return <button onClick={() => mutation.mutate({ name: 'New Name' })}>Update</button>;
}
```

## URL State

Store filter, sort, and pagination params in the URL so the page is shareable and the browser back button works.

```tsx
import { useSearchParams } from 'react-router-dom';

function ProductList() {
  const [params, setParams] = useSearchParams();
  const sort = params.get('sort') ?? 'newest';

  return (
    <select value={sort} onChange={(e) => setParams({ sort: e.target.value })}>
      <option value="newest">Newest</option>
      <option value="price">Price</option>
    </select>
  );
}
```
