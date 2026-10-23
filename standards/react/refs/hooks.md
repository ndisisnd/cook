---
last_reviewed: 2026-10-23
---

# React Hooks

Generic hook recipes (`useDebounce`, `useOnClickOutside`, `useInView`, `useWindowSize`) are not listed: write them directly and apply the rules below.

## Async Effects

Guard stale results even when the work cannot be aborted (pair with `AbortController` when it can):

```tsx
useEffect(() => {
  let ignore = false;
  fetchUser(userId).then((result) => {
    if (!ignore) setUser(result);
  });
  return () => { ignore = true; };
}, [userId]);
```

## useEffectEvent

Stable since React 19.2 (the `eslint-plugin-react-hooks` lint enforces the rules below).

- Call it only from `useEffect`, `useLayoutEffect`, `useInsertionEffect`, or another Effect Event. Calling it in render or in an event handler throws.
- Never list it in a dependency array; its identity changes every render on purpose.
- Never pass it to child components or other hooks. Use `useCallback` or a plain function for those.
- Never use it to skip a real dependency. A value that should re-run the effect stays in the array.
- Inside a custom hook it can wrap a callback the hook receives, so callers may pass inline functions without resubscribing.

```tsx
function useInterval(callback: () => void, delay: number | null) {
  const onTick = useEffectEvent(callback);
  useEffect(() => {
    if (delay === null) return;
    const id = setInterval(() => onTick(), delay);
    return () => clearInterval(id);
  }, [delay]);
}
```

Do not write a `useLatest` ref fallback on React 19.2+.

## useSyncExternalStore

Use it for external subscriptions (online status, `matchMedia`, window size, third-party stores) instead of `useState` plus an effect.

- Define `subscribe` at module scope so its identity is stable; an inline `subscribe` resubscribes every render.
- `getSnapshot` must return a cached or primitive value. A new object each call loops forever.
- Always pass `getServerSnapshot` when the component renders on the server.

```tsx
function subscribe(cb: () => void) {
  window.addEventListener('online', cb);
  window.addEventListener('offline', cb);
  return () => {
    window.removeEventListener('online', cb);
    window.removeEventListener('offline', cb);
  };
}
export const useOnlineStatus = () =>
  useSyncExternalStore(subscribe, () => navigator.onLine, () => true);
```

## useLayoutEffect

Use it only when DOM measurement or a synchronous visual adjustment must happen before paint. Default to `useEffect`. Do not rely on it for server-rendered output; it does not run on the server.

## Browser Storage In Hooks

- Never read `localStorage` or `window` in a `useState` initializer on code that server-renders; the first client render differs from the server and causes a hydration mismatch. Render the stored value after mount, or use `useSyncExternalStore` with a server snapshot.
- Wrap storage parse and write in `try/catch`; quota and private-mode failures must not crash the tree.
- Never store tokens or secrets in storage.

## Cleanup And Stable Inputs

- Every effect that adds a listener, timer, observer, or subscription returns its cleanup (`removeEventListener`, `clearTimeout`, `observer.disconnect()`).
- Do not take inline object options (such as `IntersectionObserver` init) as effect dependencies; accept primitives (`rootMargin`, `threshold`) instead.
- A custom hook that takes a callback wraps it in `useEffectEvent`, not a ref read during render.

## Previous Value

Never write a `usePrevious` that returns `ref.current`; it reads a ref during render, which the compiler and `react-hooks/refs` reject. Store the previous value in state and update it during render:

```tsx
const [prevCount, setPrevCount] = useState(count);
if (prevCount !== count) {
  setPrevCount(count);
  setTrend(count > prevCount ? 'up' : 'down');
}
```

Often it is cleaner to compute the comparison in the event handler that changes the value.
