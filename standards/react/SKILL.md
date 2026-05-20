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
      - JSX
      - ReactNode
      - props
      - render
---
# React

Load this file by default for any `.tsx` or `.jsx` task. Pull refs only when the task explicitly requires that depth — see the References section.

## P0 — Hook Correctness

- Dependency arrays must be exhaustive (`exhaustive-deps`). Never suppress the linter to silence a warning — fix the logic.
- Objects and arrays are recreated on every render. Memoize them with `useMemo` before placing them in a dependency array or they will cause infinite re-render loops.
- `useEffect` is for syncing with external systems only. Return a cleanup function for subscriptions, timers, and event listeners. Use `AbortController` for fetch cleanup to prevent state updates after unmount.
- Never call hooks inside conditions, loops, or nested functions.
- Do not use `useEffect` to sync derived state — compute it during render instead.
- Lazy-initialize expensive state: `useState(() => compute())`.
- `useMemo` and `useCallback`: measure before adding. Use `useCallback` to stabilize function references passed to memoized children; use `useMemo` for genuinely expensive computed values.
- `useRef` for mutable values that must not trigger re-renders (DOM nodes, timers, previous-value tracking).
- `useTransition` / `useDeferredValue` for non-blocking UI updates that should not block input.
- Stale closure in a long-lived subscription or event listener: store the latest callback in a ref (`useRef`) and read it inside the effect, so the effect dependency stays stable without capturing an outdated function.

## P0 — Component Basics

- Function components only. No class components.
- One component per file. Named exports. PascalCase names.
- Keep components under ~250 lines; split when larger.
- No nested component definitions — define at module scope.
- Use stable IDs as list keys; never use array index.
- Prefer ternary (`cond ? <A /> : <B />`) over `&&` for conditional rendering — `&&` renders `0` when the left side is falsy.
- Define event handlers before the return statement; avoid non-trivial inline arrow functions in JSX props.
- Do not drill props more than two levels — use Context API or a state manager.

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
- Prop drilling beyond two levels.
- Array index used as list key.
- `React.FC` type annotation.
- `any` in TypeScript.
- Nested component definitions.
- `dangerouslySetInnerHTML` without DOMPurify sanitization.
- Tokens or secrets in `localStorage`.
- Inline object literals as props on memoized children (`style={{}}`).
- `export *` barrel files — breaks tree-shaking.

## References

Load only what the current task requires:

- [component-patterns](refs/component-patterns.md) — designing reusable component APIs: composition, compound components, HOC, render props, controlled vs uncontrolled
- [state-management](refs/state-management.md) — choosing or implementing state: Context, Zustand, Redux Toolkit, React Query/SWR
- [performance](refs/performance.md) — eliminating data waterfalls, reducing bundle size, virtualization, web workers, `startTransition`
- [testing](refs/testing.md) — writing RTL tests, MSW mocking, form/context/router testing patterns
- [security](refs/security.md) — XSS/DOMPurify depth, auth flows, CSRF tokens, CSP headers, OAuth/JWT
- [tooling](refs/tooling.md) — Vite config, DevTools profiling, bundle analysis, `why-did-you-render`, ESLint setup
