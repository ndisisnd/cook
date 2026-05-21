---
name: react
description: Write correct, idiomatic React with TypeScript. Use when building or reviewing React components, hooks, or JSX — covers hook rules, component structure, TypeScript prop typing, and boundary safety.
metadata:
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

Load this file by default for any `.tsx` or `.jsx` task. Pull refs only when the task explicitly requires that depth — see the References section.

## P0 — Hook Correctness

- Dependency arrays must be exhaustive (`exhaustive-deps`). Never suppress the linter to silence a warning — fix the logic.
- Objects, arrays, and functions in dependency arrays: first move creation inside the effect, hoist constants, or remove the effect. Use `useMemo`/`useCallback` only when identity stability is required or measured work is expensive.
- `useEffect` is for syncing with external systems only. Derived data belongs in render; event-specific logic belongs in event handlers. Prefer framework data APIs, route loaders, TanStack Query, or SWR over raw fetch effects when available.
- Effects must clean up subscriptions, timers, and event listeners. Use `AbortController` for cancellable fetches and stale-response guards for non-abortable async work.
- Never call hooks inside conditions, loops, nested functions, event handlers, class components, callbacks passed to hooks, `try`/`catch`/`finally`, or after a conditional return.
- Do not use `useEffect` to sync derived state — compute it during render instead.
- Lazy-initialize expensive state: `useState(() => compute())`.
- `useMemo` and `useCallback`: measure before adding. React Compiler may reduce manual memoization; keep manual memoization where identity is observable or profiling proves value.
- `useRef` for mutable values that must not trigger re-renders (DOM nodes, timers, previous-value tracking).
- `useTransition` / `useDeferredValue` for non-blocking UI updates that should not block input.
- React 19+: use `useEffectEvent` for effect-local callbacks that need latest committed values without re-synchronizing the effect. Do not use it to hide real dependencies. For older React or non-effect callbacks, use the latest-ref pattern.

## P0 — Component Basics

- Function components only. No class components.
- One exported component per file; keep small helper components module-local when they only serve that file. Prefer named exports. PascalCase names.
- Treat ~250 lines as a review smell, not a hard rule. Split by responsibility before a component accumulates unrelated state, effects, or rendering branches.
- No nested component definitions — define at module scope.
- Use stable IDs as list keys; never use array index.
- Use `useId` for generated accessibility IDs; never use it for list keys.
- Prefer ternary (`cond ? <A /> : <B />`) over `&&` for conditional rendering — `&&` renders `0` when the left side is falsy.
- Define event handlers before the return statement; avoid non-trivial inline arrow functions in JSX props.
- Do not thread props through components that do not use them — use composition, Context API, or a state manager when state crosses several layers.
- Custom accordions, dialogs, menus, tabs, and compound widgets must implement keyboard interaction, focus management, and ARIA semantics or use a proven accessible primitive.

## P0 — Boundary Safety

- Never use `dangerouslySetInnerHTML` without sanitizing input through DOMPurify first.
- Never store tokens, JWTs, or secrets in `localStorage` or in the JS bundle — use `HttpOnly` cookies.
- Avoid `javascript:` URIs in `href` or `src`.
- Never use `eval()` or `new Function(string)` — remote code execution risk.
- Never enforce permissions on the client. Frontend checks are UX only; the backend must validate every request.

## P1 — TypeScript

- Type props with an explicit `interface` or `type`. Avoid `React.FC` — it provides no value over a plain function and historically caused implicit-children confusion.
- Use `ReactNode` for children props. Use `JSX.Element` only when callers must provide a single React element.
- Type event handlers with specific React types: `React.ChangeEvent<HTMLInputElement>`, `React.FormEvent<HTMLFormElement>`, etc.
- DOM refs: `useRef<HTMLDivElement>(null)` (nullable). Mutable value refs: `useRef<ReturnType<typeof setTimeout>>(undefined)`.
- React 19 can accept `ref` as a prop; older React still needs `forwardRef` for ref-passing components. Type refs according to the target React version.
- State: `useState<User | null>(null)` — use generics for types that cannot be inferred from the initial value.
- Extend native elements with `ComponentPropsWithoutRef<'button'>` rather than reimplementing their attribute types.
- Generic components: `function List<T>({ items, render }: ListProps<T>)`.
- Use discriminated unions for mutually exclusive prop states (e.g., `{ status: 'success'; data: T } | { status: 'error'; error: Error }`).
- Use `Omit`, `Pick`, `Partial` to derive prop interfaces — avoid duplicating shapes manually.
- Avoid `any`. Prefer `unknown` and narrow with a type guard or assertion.

## P1 — Conventions

- Custom hooks must start with `use` and return only what callers need.
- Naming: PascalCase for components, camelCase for hooks and handlers, `is`/`has`/`can` prefix for boolean props.
- Never mutate state directly — use spread or Immer.
- Extract static objects and JSX outside component scope to prevent accidental recreation on each render.

## Anti-Patterns

- Missing or suppressed hook dependency warnings.
- `useEffect` used to sync derived state.
- Hooks after conditional returns or inside `try`/`catch`/`finally`.
- Prop drilling beyond two levels.
- Array index used as list key.
- `React.FC` type annotation.
- `any` in TypeScript.
- Nested component definitions.
- `dangerouslySetInnerHTML` without DOMPurify sanitization.
- Tokens or secrets in `localStorage`.
- Inline object literals as props on memoized children (`style={{}}`).
- Broad runtime `export *` barrel files that break tree-shaking.

## References

Load only what the current task requires:

- [component-patterns](refs/component-patterns.md) — designing reusable component APIs: composition, compound components, HOC, render props, controlled vs uncontrolled
- [state-management](refs/state-management.md) — choosing or implementing state: Context, Zustand, Redux Toolkit, React Query/SWR
- [performance](refs/performance.md) — eliminating data waterfalls, reducing bundle size, virtualization, web workers, `startTransition`
- [testing](refs/testing.md) — writing RTL tests, MSW mocking, form/context/router testing patterns
- [security](refs/security.md) — XSS/DOMPurify depth, auth flows, CSRF tokens, CSP headers, OAuth/JWT
- [tooling](refs/tooling.md) — Vite config, DevTools profiling, bundle analysis, `why-did-you-render`, ESLint setup
- [hooks](refs/hooks.md) — reusable custom hooks: useLocalStorage, useDebounce, useWindowSize, useOnClickOutside, useIntersectionObserver, usePrevious, useToggle
