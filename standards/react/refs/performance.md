---
last_reviewed: 2026-10-23
---
# React Performance

Verified 2026-10: React 19.x, React Compiler 1.0 (`babel-plugin-react-compiler`), https://react.dev/learn/react-compiler/introduction

## Eliminate Data Waterfalls (P0)

- Fetch independent data in parallel: `await Promise.all([getUser(), getProducts()])`. Sequential `await` is the top cause of slow loads.
- Start fetches before render: route loaders or event handlers, not effects after mount.
- Prefer framework data APIs, route loaders, TanStack Query, or SWR over fetch effects. If an effect is unavoidable, use `AbortController` or a stale-response guard.
- Wrap slow subtrees in `<Suspense fallback={...}>` so the rest of the page renders first.

## Reduce Bundle Size (P0)

- Lazy-load heavy, non-initial components: `const Chart = lazy(() => import('./Chart'))` inside `<Suspense>`.
- Off-screen images: `loading="lazy" decoding="async"`. Next.js projects use `next/image` (see the nextjs shelf).
- Avoid `export *` barrels over large folders. Curated or type-only barrels are fine if bundle analysis shows tree-shaking works.
- Replace heavy libraries before shipping (`moment` → `dayjs`, `lodash` → native).
- Analyse the bundle before each significant release (`vite-bundle-visualizer`, `webpack-bundle-analyzer`).

## Memoization and Re-renders (P1)

- Move state down to its consumer. An update re-renders the owner and all descendants.
- With React Compiler enabled: write no manual `useMemo`, `useCallback`, or `memo` in new code; the compiler memoizes by analysis. Leave existing memoization in place (removing it can change output) unless tests cover the change.
- Keep manual `useMemo`/`useCallback` when a value is an effect dependency and must not re-fire the effect, or when you need exact control. Keep `memo` when profiling proves a win the compiler does not give.
- Without the Compiler: do not memoize by default. Remove needless effects, hoist constants, and measure first. Then memoize expensive items or stable callbacks passed to `memo` children.
- The Compiler skips components that break the Rules of React (mutating props or state, reading `ref.current` in render). Fix the violation instead of adding memoization. Check with `eslint-plugin-react-hooks` compiler rules.
- Virtualize lists of roughly 500+ rows (`@tanstack/react-virtual`).
- `startTransition` marks non-urgent state updates (results) so urgent input stays responsive. `useDeferredValue(query)` lets an expensive child lag behind input.
- CSS `content-visibility: auto` with `contain-intrinsic-size` skips layout and paint for large off-screen sections.

## Heavy Computation (P1)

Move encryption, image processing, and large sorts into a Web Worker (`new Worker(new URL('./worker.ts', import.meta.url), { type: 'module' })`). Terminate it in the effect cleanup.

## React Server Components (P1)

Applies when the framework supports RSC. Next.js-specific caching lives in the nextjs shelf.

- Keep server-only data fetching and heavy dependencies in Server Components.
- Pass minimal serializable props to Client Components: IDs, primitives, small DTOs.
- Dedupe repeated reads in one request with `cache(fn)` from `react`.

## Profiling

Use the React DevTools Profiler before optimising. `<Profiler id onRender>` suits programmatic thresholds only.
