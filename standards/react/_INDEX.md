<!-- Hand-maintained routing index. Keep in sync with SKILL.md frontmatter. -->
# react Skills Index

## File Match (auto-check against the file you are editing)

| Skill | File pattern | Keywords |
| ----- | ------------ | -------- |
| **react** | `**/*.tsx`, `**/*.jsx` | react component, function component, props, children prop, JSX, react hooks, useEffect, useEffectEvent, useState, useCallback, useMemo, useRef, useContext, useReducer, useSyncExternalStore, useId, useLayoutEffect, ReactNode |
| react → testing ref | `**/*.test.tsx`, `**/*.spec.tsx`, `**/*.test.jsx`, `**/*.spec.jsx`, `**/__tests__/**`, `content:@testing-library`, `content:msw`, `content:vitest`, `content:jest`, `content:describe(`, `content:renderHook` | renderHook, getByRole, getByTestId, getByText, findByRole, userEvent, MSW, mock service worker, waitFor, queryBy, fake timers, act() |
| react → tooling ref | `vite.config.*`, `eslint.config.*`, `.eslintrc*`, `webpack.config.*`, `babel.config.*`, `.babelrc*` | vite, webpack, StrictMode, exhaustive-deps, React Compiler, eslint |
| react → state-management ref | — | zustand, redux, RTK, RTK Query, react-query, TanStack Query, SWR, Jotai |
| react → performance ref | — | waterfall, lazy, Suspense, virtualize, react-window, TanStack Virtual, bundle size, profiler, profiling, React Compiler |
| react → security ref | — | dangerouslySetInnerHTML, XSS, DOMPurify, Trusted Types, JWT, CSRF, sanitize, SameSite |
| react → component-patterns ref | — | compound component, HOC, render prop, composition, controlled, uncontrolled, accessibility, ARIA, dialog component, tabs component, menu component |
| react → hooks ref | — | useEffectEvent, useSyncExternalStore, useLayoutEffect, useLocalStorage, useDebounce, useOnClickOutside, useIntersectionObserver, usePrevious, custom hook |

Core refs (auto mode): hooks, performance, security

> Load `<SKILLS>/react/SKILL.md` for any `.tsx` or `.jsx` file — covers hook correctness, component basics, React 19 APIs, boundary safety (P0), TypeScript and conventions (P1).
>
> Concept refs (hooks, performance, security, state, component patterns) have no file pattern: they always load under a bare `--react`. In auto mode they route by keyword, except the core refs on the `Core refs` line above (hooks, performance, security), which load whenever react routes. Structural refs carry a file pattern, and testing also carries `content:` signals (test-library imports in a touched source file, so an inline test in a normal file still loads it).
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
