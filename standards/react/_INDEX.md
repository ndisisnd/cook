<!-- AUTO-GENERATED from SKILL.md frontmatter — do not edit manually -->
# react Skills Index

## File Match

| Skill | File pattern | Keywords |
| ----- | ------------ | -------- |
| **react** | `**/*.tsx`, `**/*.jsx` | component, props, children, JSX, hooks, useEffect, useEffectEvent, useState, useCallback, useMemo, useRef, useContext, useReducer, useSyncExternalStore, useId, useLayoutEffect, ReactNode |
| react → testing ref | `**/*.test.tsx`, `**/*.spec.tsx`, `**/*.test.jsx`, `**/*.spec.jsx` | render, screen, userEvent, MSW, mock service worker, waitFor, queryBy, fake timers, act |
| react → tooling ref | `package.json`, `vite.config.*`, `.eslintrc.*`, `eslint.config.*` | vite, webpack, bundle, StrictMode, profile, why-did-you-render, exhaustive-deps, React Compiler |
| react → state-management ref | `**/store/**`, `**/stores/**` | zustand, redux, RTK, RTK Query, react-query, TanStack Query, SWR, Jotai, store |
| react → performance ref | `**/*.tsx`, `**/*.jsx` | waterfall, lazy, Suspense, dynamic, virtualize, react-window, TanStack Virtual, bundle size, React Compiler |
| react → security ref | `**/*.tsx`, `**/*.jsx` | dangerouslySetInnerHTML, XSS, DOMPurify, Trusted Types, JWT, auth, CSP, CSRF, sanitize, SameSite |
| react → component-patterns ref | `**/*.tsx`, `**/*.jsx` | compound component, HOC, render prop, composition, controlled, uncontrolled, accessibility, ARIA, dialog, tabs, menu |
| react → hooks ref | `**/*.tsx`, `**/*.jsx` | useEffectEvent, useSyncExternalStore, useId, useLayoutEffect, useLocalStorage, useDebounce, useWindowSize, useOnClickOutside, useIntersectionObserver, usePrevious, useToggle, custom hook |

## Loading Instructions

> Load `<SKILLS>/react/SKILL.md` for any `.tsx` or `.jsx` file — covers hook correctness (P0), component basics (P0), boundary safety (P0), TypeScript conventions (P1), and style conventions (P1).
>
> Load `<SKILLS>/react/refs/testing.md` when touching test files or writing RTL/MSW tests, including async queries, absence checks, fake timers, or `userEvent`.
>
> Load `<SKILLS>/react/refs/tooling.md` when touching Vite/webpack config, ESLint config, React Compiler-compatible hooks linting, or bundle tooling.
>
> Load `<SKILLS>/react/refs/state-management.md` when choosing or implementing Context, Zustand, Redux Toolkit, Jotai, TanStack Query, SWR, or URL state.
>
> Load `<SKILLS>/react/refs/performance.md` when investigating re-renders, waterfalls, virtualization, React Compiler-era memoization, or bundle bloat.
>
> Load `<SKILLS>/react/refs/security.md` when touching auth, XSS, CSRF, CSP, Trusted Types, token storage, or serialized-state concerns.
>
> Load `<SKILLS>/react/refs/component-patterns.md` when designing reusable, composable component APIs or custom accessible compound widgets.
>
> Load `<SKILLS>/react/refs/hooks.md` when implementing or reviewing reusable custom hooks, external subscriptions, effect-local callbacks, layout measurement, or generated accessibility IDs.

## Archived

The following sub-skill folders have been merged into `SKILL.md` and `refs/`, then archived under `archive/react/` as non-loadable source trace:

- `archive/react/react-component-patterns/` → merged into `refs/component-patterns.md`
- `archive/react/react-hooks/` → merged into `SKILL.md` and `refs/hooks.md`
- `archive/react/react-performance/` → merged into `refs/performance.md`
- `archive/react/react-security/` → merged into `refs/security.md`
- `archive/react/react-state-management/` → merged into `refs/state-management.md`
- `archive/react/react-testing/` → merged into `refs/testing.md`
- `archive/react/react-tooling/` → merged into `refs/tooling.md`
- `archive/react/react-typescript/` → merged into `SKILL.md` and `refs/component-patterns.md`
