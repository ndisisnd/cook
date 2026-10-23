---
name: react
description: Write correct, idiomatic React with TypeScript. Use when building or reviewing React components, hooks, or JSX — covers hook rules, component structure, TypeScript prop typing, and boundary safety.
metadata:
  targets: "React 19.x (19.3 current) · React Compiler 1.0 · TypeScript with @types/react 19"
  last_reviewed: 2026-10-23
  triggers:
    files:
      - '**/*.tsx'
      - '**/*.jsx'
      - '**/*.test.tsx'
      - '**/*.spec.tsx'
    keywords:
      - component
      - hooks
      - useEffect
      - useState
      - useCallback
      - useMemo
      - useRef
      - useContext
      - useReducer
      - useEffectEvent
      - useSyncExternalStore
      - useId
      - useLayoutEffect
      - JSX
      - ReactNode
      - props
      - render
---
# React

Target: React 19.x with React Compiler 1.0 and `@types/react` 19. Load by default for any `.tsx` or `.jsx` task; pull refs only when the task needs that depth. Framework rules (routing, caching, Server Actions wiring, CSP) live in the framework's skill.

## P0 — Hook Correctness

- Dependency arrays must be exhaustive (`exhaustive-deps`). Never suppress the linter — fix the logic.
- `useEffect` is for syncing with external systems only. Derived data belongs in render; event-specific logic belongs in event handlers. Prefer framework data APIs, route loaders, TanStack Query, or SWR over raw fetch effects.
- Effects must clean up subscriptions, timers, and listeners. Use `AbortController` for cancellable fetches and an `ignore` flag for non-abortable async work.
- Never call hooks inside conditions, loops, nested functions, event handlers, class components, `try`/`catch`/`finally`, or after a conditional return. `use()` is the exception: it may be called conditionally.
- Never read or write `ref.current` during render (except lazy init `if (ref.current === null)`). Read refs in effects and event handlers.
- Lazy-initialize expensive state: `useState(() => compute())`.
- Memoization: when React Compiler is enabled, do not add new `useMemo`, `useCallback`, or `React.memo`; the compiler memoizes. Keep existing manual memoization unless tests and profiling show removal is safe. Without the compiler, memoize only when identity is observable or profiling proves value.
- `useTransition` / `useDeferredValue` for non-urgent updates that must not block input.
- `useEffectEvent` (stable since React 19.2) for effect-local callbacks that need the latest props/state without re-running the effect. Call it only from inside effects; never use it to hide real dependencies.

## P0 — Component Basics

- Function components only. The one exception is an error boundary when no library (`react-error-boundary`) or framework boundary (`error.tsx`) is available.
- One exported component per file; keep small helpers module-local. Prefer named exports — except where a framework requires default exports (Next.js `page`, `layout`, `route`, `error`, `loading`, `not-found`, `default`; React Router route modules; `React.lazy` targets).
- ~250 lines is a review smell. Split by responsibility before a component accumulates unrelated state, effects, or branches.
- No nested component definitions — define components at module scope.
- Use stable IDs as list keys; never array index. Use `useId` for accessibility IDs, never for keys.
- Prefer ternary (`cond ? <A /> : null`) over `&&` when the left side can be `0` or `''`.
- Do not thread props through components that do not use them — use composition, Context, or a store.
- Custom dialogs, menus, tabs, and compound widgets must implement keyboard interaction, focus management, and ARIA semantics, or use a proven accessible primitive.
- Wrap independently failing subtrees in error boundaries. They do not catch errors in event handlers or async code; handle those explicitly.

## P0 — React 19 APIs

- Forms and mutations: use Actions — `<form action={fn}>`, `useActionState` for result/pending state, `useFormStatus` in a child for submit state, `useOptimistic` for optimistic UI.
- `use(promise)` reads a Promise inside `<Suspense>`; create the Promise outside render (in a loader, Server Component, or cache), never inline in the component body.
- Render `<Context value={...}>` directly; `<Context.Provider>` is legacy.
- `<Activity mode="hidden">` keeps state for hidden UI while unmounting its effects. Use it instead of conditional unmount when state must survive.
- `ref` is a regular prop on function components; do not write new `forwardRef` wrappers.

## P0 — Boundary Safety

- Never use `dangerouslySetInnerHTML` without sanitizing through DOMPurify first.
- Never store tokens, JWTs, or secrets in `localStorage`, `sessionStorage`, client stores, or the JS bundle — use `HttpOnly` cookies.
- Block `javascript:` (and untrusted `data:`) URLs in `href` and `src`.
- Never use `eval()` or `new Function(string)`.
- Never enforce permissions on the client. Frontend checks are UX only; the backend validates every request.

## P1 — TypeScript

- Type props with an explicit `interface` or `type`. Avoid `React.FC`.
- Use `ReactNode` for children. Use `React.JSX.Element` only when callers must pass a single element (the global `JSX` namespace is removed in `@types/react` 19).
- `useRef` always takes an argument: `useRef<HTMLDivElement>(null)` for DOM refs, `useRef<number | null>(null)` or `useRef<T | undefined>(undefined)` for mutable values.
- Type `ref` props as `React.Ref<HTMLButtonElement>` or use `ComponentPropsWithRef<'button'>`.
- Extend native elements with `ComponentPropsWithoutRef<'button'>` (or `WithRef` when forwarding `ref`).
- Use discriminated unions for mutually exclusive prop states.
- Avoid `any`. Prefer `unknown` and narrow with a type guard.

## P1 — Conventions

- Never mutate state, props, or values captured by hooks — use spread or Immer.
- Keep components and hooks pure: no side effects, no global mutation during render.
- Hoist static objects and JSX outside the component.
- No runtime `export *` barrel files; they break tree-shaking.

## References

Load only what the current task requires:

- [component-patterns](refs/component-patterns.md) — composition, compound components, controlled vs uncontrolled, polymorphic `as`
- [state-management](refs/state-management.md) — Context, Zustand, Jotai, Redux Toolkit, TanStack Query/SWR, URL state
- [performance](refs/performance.md) — waterfalls, bundle size, React Compiler, virtualization, transitions, profiling
- [testing](refs/testing.md) — RTL, MSW, providers, router, async queries
- [security](refs/security.md) — XSS/DOMPurify, URL validation, token storage, CSRF, serialized state
- [tooling](refs/tooling.md) — Vite, StrictMode, ESLint flat config, React Compiler setup
- [hooks](refs/hooks.md) — `useEffectEvent`, `useSyncExternalStore`, `useLayoutEffect`, SSR-safe storage, stable callbacks, previous value
