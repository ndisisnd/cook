---
last_reviewed: 2026-10-23
---

# React Tooling

Profiling and bundle analysis live in `refs/performance.md`.

## Vite

Use Vite (or a framework) for new projects. Create React App is deprecated.

```ts
// vite.config.ts — Vite 8, @vitejs/plugin-react 6+ (Rolldown-based)
import { defineConfig } from 'vite';
import react, { reactCompilerPreset } from '@vitejs/plugin-react';
import babel from '@rolldown/plugin-babel';

export default defineConfig({
  plugins: [react(), babel({ presets: [reactCompilerPreset()] })],
});
```

- Install `@rolldown/plugin-babel`, `@babel/core`, and `babel-plugin-react-compiler` as dev dependencies for the compiler preset.
- `@vitejs/plugin-react` below 6 takes the compiler inline: `react({ babel: { plugins: ['babel-plugin-react-compiler'] } })`. It must run first in the Babel pipeline.
- Vite exposes only `VITE_`-prefixed vars via `import.meta.env`. Everything in the client bundle is public; keep secrets server-side.

## React Compiler

- React Compiler 1.0 is stable. Install `babel-plugin-react-compiler@latest`; it must run first in the Babel pipeline.
- Next.js: set `reactCompiler: true` in `next.config.ts` (off by default).
- The compiler skips components that break the Rules of React and keeps compiling the rest. Fix lint-reported violations over time; do not suppress them.
- In compiled code, do not add new `useMemo` / `useCallback` / `React.memo` by default.

## StrictMode

Wrap the app in `<StrictMode>` in development. It double-invokes render and effects to expose impure code and missing cleanup. Do not remove it to silence a double-effect; fix the missing cleanup.

## ESLint (Flat Config)

`eslint-plugin-react-hooks` (7.x) ships `rules-of-hooks`, `exhaustive-deps`, and the Compiler rules (`purity`, `refs`, `immutability`, `set-state-in-effect`, `set-state-in-render`, `static-components`, `preserve-manual-memoization`, and others) in its `recommended` preset.

```js
// eslint.config.js
import { defineConfig } from 'eslint/config';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';

export default defineConfig([
  reactHooks.configs.flat.recommended,
  {
    plugins: { 'react-refresh': reactRefresh },
    rules: { 'react-refresh/only-export-components': 'warn' },
  },
]);
```

- Use `reactHooks.configs.flat['recommended-latest']` only to opt into experimental compiler rules.
- In Next.js, `eslint-config-next` already includes `eslint-plugin-react-hooks`; do not register it twice.
- Never disable `exhaustive-deps`. Move object creation into the effect, split effects, or use `useEffectEvent`.
