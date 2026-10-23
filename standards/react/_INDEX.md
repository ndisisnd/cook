<!-- Hand-maintained routing index. Keep in sync with SKILL.md frontmatter. -->
# react Skills Index

## File Match (auto-check against the file you are editing)

| Skill | File pattern | Keywords |
| ----- | ------------ | -------- |
| **react** | `**/*.tsx`, `**/*.jsx` | component, props, children, JSX, hooks, useEffect, useEffectEvent, useState, useCallback, useMemo, useRef, useContext, useReducer, useSyncExternalStore, useId, useLayoutEffect, ReactNode |
| react → testing ref | `**/*.test.tsx`, `**/*.spec.tsx` | render, screen, userEvent, MSW, mock service worker, waitFor, queryBy, fake timers, act |
| react → tooling ref | — | vite, webpack, StrictMode, exhaustive-deps, React Compiler, eslint |
| react → state-management ref | — | zustand, redux, RTK, RTK Query, react-query, TanStack Query, SWR, Jotai, store |
| react → performance ref | — | waterfall, lazy, Suspense, virtualize, react-window, TanStack Virtual, bundle size, profile, React Compiler |
| react → security ref | — | dangerouslySetInnerHTML, XSS, DOMPurify, Trusted Types, JWT, CSRF, sanitize, SameSite |
| react → component-patterns ref | — | compound component, HOC, render prop, composition, controlled, uncontrolled, accessibility, ARIA, dialog, tabs, menu |
| react → hooks ref | — | useEffectEvent, useSyncExternalStore, useLayoutEffect, useLocalStorage, useDebounce, useOnClickOutside, useIntersectionObserver, usePrevious, custom hook |

> Load `<SKILLS>/react/SKILL.md` for any `.tsx` or `.jsx` file — covers hook correctness, component basics, React 19 APIs, boundary safety (P0), TypeScript and conventions (P1).
>
> Refs route by keyword only (rows marked `—`), except testing, which also matches test files.
>
> Load `<SKILLS>/react/refs/testing.md` when touching test files or writing RTL/MSW tests, async queries, absence checks, fake timers, or `userEvent`.
>
> Load `<SKILLS>/react/refs/tooling.md` when touching Vite/webpack config, ESLint config, or React Compiler setup.
>
> Load `<SKILLS>/react/refs/state-management.md` when choosing or implementing Context, Zustand, Redux Toolkit, Jotai, TanStack Query, SWR, or URL state.
>
> Load `<SKILLS>/react/refs/performance.md` when investigating re-renders, waterfalls, virtualization, React Compiler-era memoization, profiling, or bundle bloat.
>
> Load `<SKILLS>/react/refs/security.md` when touching XSS, DOMPurify, URL sinks, CSRF, Trusted Types, token storage, or serialized-state concerns.
>
> Load `<SKILLS>/react/refs/component-patterns.md` when designing reusable, composable component APIs or custom accessible compound widgets.
>
> Load `<SKILLS>/react/refs/hooks.md` when implementing or reviewing reusable custom hooks, external subscriptions, effect-local callbacks, or layout measurement.
