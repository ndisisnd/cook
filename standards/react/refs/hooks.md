# React Hooks

Reusable custom hooks, rewritten in typed TypeScript. Each is the canonical implementation a reviewer can point to — the correctness note (cleanup, exhaustive deps, SSR-safe access) is what makes it standards-worthy, not the convenience.

## useLocalStorage

Persist state to `localStorage` and keep React in sync with it. Lazy-initialises so the read happens once, wraps every parse and write in `try/catch` (quota limits and private-mode failures must not crash the tree), supports a functional updater against the latest state like `useState`, and is SSR-safe via a `typeof window` guard. Do not use this for tokens or secrets.

```tsx
type SetValue<T> = (value: T | ((prev: T) => T)) => void;

function useLocalStorage<T>(key: string, initial: T): [T, SetValue<T>] {
  const [stored, setStored] = useState<T>(() => {
    if (typeof window === 'undefined') return initial;
    try {
      const item = window.localStorage.getItem(key);
      return item ? (JSON.parse(item) as T) : initial;
    } catch {
      return initial;
    }
  });

  const setValue: SetValue<T> = (value) => {
    setStored((prev) => {
      const next = typeof value === 'function' ? (value as (prev: T) => T)(prev) : value;
      if (typeof window !== 'undefined') {
        try {
          window.localStorage.setItem(key, JSON.stringify(next));
        } catch {
          // ignore write errors (quota exceeded, private mode)
        }
      }
      return next;
    });
  };

  return [stored, setValue];
}
```

## useDebounce

Return a value that only updates after it has stopped changing for `delay` ms — the standard way to throttle search inputs and resize handlers. The timer is created and cleared inside an effect keyed on `[value, delay]`, so each change cancels the previous pending update and nothing leaks on unmount.

```tsx
function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState<T>(value);

  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(id);
  }, [value, delay]);

  return debounced;
}
```

## useWindowSize

Track the viewport dimensions reactively. The `resize` listener is registered once and removed on cleanup, and the initial render is SSR-safe — it starts at `0` and reads `window` only after mount to avoid hydration mismatches.

```tsx
function useWindowSize(): { width: number; height: number } {
  const [size, setSize] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const onResize = () =>
      setSize({ width: window.innerWidth, height: window.innerHeight });
    onResize();
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, []);

  return size;
}
```

## useOnClickOutside

Fire a handler when a click or tap lands outside the referenced element — the basis for dismissible menus and modals. It listens on both `mousedown` and `touchstart` for parity across devices, guards with `contains` so clicks inside the element are ignored, and removes both listeners on cleanup.

```tsx
function useOnClickOutside(
  ref: RefObject<HTMLElement>,
  handler: (event: Event) => void,
): void {
  useEffect(() => {
    const listener = (event: Event) => {
      const el = ref.current;
      if (!el || el.contains(event.target as Node)) return;
      handler(event);
    };
    document.addEventListener('mousedown', listener);
    document.addEventListener('touchstart', listener);
    return () => {
      document.removeEventListener('mousedown', listener);
      document.removeEventListener('touchstart', listener);
    };
  }, [ref, handler]);
}
```

## useIntersectionObserver

Report whether the referenced element is in the viewport — the idiomatic way to drive lazy rendering and infinite scroll without scroll-event spam. The observer is created inside an effect and torn down with `observer.disconnect()` on cleanup, and the effect bails out early when the ref is not yet attached. Memoize `options` before passing it if it is constructed inline.

```tsx
function useIntersectionObserver(
  ref: RefObject<Element>,
  options?: IntersectionObserverInit,
): boolean {
  const [isIntersecting, setIsIntersecting] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => setIsIntersecting(entry.isIntersecting),
      options,
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [ref, options]);

  return isIntersecting;
}
```

## usePrevious

Return the value a prop or state held on the previous commit, for diffing across renders. The ref is updated inside an effect — so it runs *after* render — which means the body still reads last commit's value before the effect overwrites it. Returns `undefined` on first render.

```tsx
function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T | undefined>(undefined);

  useEffect(() => {
    ref.current = value;
  }, [value]);

  return ref.current;
}
```

## useToggle

Manage a boolean with a stable toggle function — the canonical idiom for open/closed and on/off UI state. The toggle is wrapped in `useCallback` with an empty dependency array and uses the functional updater, so its identity stays stable across renders and is safe to pass to memoized children.

```tsx
function useToggle(initial = false): [boolean, () => void] {
  const [value, setValue] = useState(initial);
  const toggle = useCallback(() => setValue((v) => !v), []);
  return [value, toggle];
}
```
