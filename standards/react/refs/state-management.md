---
last_reviewed: 2026-10-23
---
# React State Management

Verified 2026-10: Zustand 5.x, TanStack Query 5.x, Redux Toolkit 2.x, Jotai 3.x (npm registry).

## Choosing the Right Tool

Start at the top and move down only when the lower scope is needed.

| Scope | Tool |
|---|---|
| One component | `useState`; `useReducer` for a state machine |
| Siblings | Lift state to the nearest common parent |
| Low-frequency global (theme, locale, auth session) | Context |
| Small independent shared atoms | Jotai |
| High-frequency or cross-app client state | Zustand; Redux Toolkit only when already present or a large multi-team app needs it |
| Server / async data | TanStack Query or SWR |
| Shareable filter, sort, page | URL search params |

- Never copy server data into `useState`; the query cache owns it.
- Never store derived values; compute them in render or a selector.
- Never persist tokens, JWTs, or secrets in any store, `localStorage`, or `sessionStorage`. Persist non-sensitive preferences only. See `standards/global/refs/auth.md`.

## Context

- Split state and dispatch into two contexts so dispatch-only consumers do not re-render on state change.
- Do not use Context for state that changes per keystroke or scroll.
- Stabilize provider `value` objects (see `component-patterns.md`).

## Zustand

- Always select a slice: `useStore((s) => s.user)`. Never call `useStore()` with no selector.
- A selector that returns a new object or array each call needs `useShallow` (v5 loops infinitely otherwise).
- Use `create<State>()(middleware(...))` (curried) for TypeScript with `devtools`/`persist`.
- Do not use a module-level store for per-request data under SSR.

## Redux Toolkit

- Use only when the project already has Redux or needs it. Do not add it for new small apps.
- Feature slices with granular `useSelector`; derive filtered or sorted data in selectors.
- Mutation syntax is allowed only inside RTK reducers (Immer). Keep state and actions serializable.
- Use RTK Query for Redux-owned server data.

## TanStack Query

- Queries are stale immediately (`staleTime: 0`). Set `staleTime` deliberately to avoid surprise refetches on mount, focus, and reconnect.
- Inactive data stays cached until `gcTime` (default 5 min); `isLoading` is `isPending && isFetching`; v5 has no `cacheTime` or `onSuccess` on queries.
- Query keys must contain every variable that changes the result: `['users', { orgId, page }]`. Build them from a key factory.
- Every mutation must invalidate, update, or remove each affected key: `queryClient.invalidateQueries({ queryKey })`.
- Override `retry` for non-idempotent or user-blocking flows.
- A `queryFn` using `fetch` must throw on `!res.ok`; `fetch` does not reject on HTTP errors.

## URL State

Keep filter, sort, and pagination in search params so links and the back button work. Use the router's search-param hook; do not mirror them into `useState`.
