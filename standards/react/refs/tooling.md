# React Tooling

## Vite Setup

Prefer Vite over Create React App for new projects — faster dev server, better tree-shaking, native ESM.

```ts
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: { vendor: ['react', 'react-dom'] },
      },
    },
  },
});
```

## StrictMode

Always wrap the app in `<React.StrictMode>` in development. It double-invokes render and effects to surface side-effect bugs early. Remove only if a specific third-party library is incompatible.

```tsx
// main.tsx
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

## Debugging Re-renders with `why-did-you-render`

Traces unexpected re-renders in development. Remove before production builds.

```tsx
// wdyr.ts — import this before React in main.tsx
import React from 'react';

if (process.env.NODE_ENV === 'development') {
  const whyDidYouRender = await import('@welldone-software/why-did-you-render');
  whyDidYouRender.default(React, { trackAllPureComponents: true });
}
```

Opt specific components into tracking:

```tsx
function ExpensiveList(props: Props) { /* ... */ }
ExpensiveList.whyDidYouRender = true;
```

## React DevTools Profiler

Use the Profiler API to measure actual render durations and find slow commits:

```tsx
import { Profiler } from 'react';

function onRender(id: string, phase: string, actualDuration: number) {
  if (actualDuration > 16) console.warn(`[Profiler] ${id} (${phase}): ${actualDuration.toFixed(1)}ms`);
}

<Profiler id="Feed" onRender={onRender}>
  <Feed />
</Profiler>
```

Open the Profiler tab in React DevTools browser extension and use "Highlight updates when components render" to spot unnecessary re-renders visually.

## Custom Hook Debug Label

```tsx
function useOnlineStatus() {
  const isOnline = useSyncExternalStore(subscribe, getSnapshot);
  useDebugValue(isOnline ? 'Online' : 'Offline'); // shown in DevTools
  return isOnline;
}
```

## Bundle Analysis

```bash
# Vite
npm install --save-dev rollup-plugin-visualizer
# add visualizer() to vite.config.ts plugins, then:
npm run build && open dist/stats.html

# webpack / CRA
npx source-map-explorer 'build/static/js/*.js'
```

Review the output for: large vendor chunks that could be split, libraries that appear multiple times (version conflicts), and modules that should be lazy-loaded.

## ESLint

Mandatory plugins for React projects:

```json
{
  "plugins": ["react-hooks", "react-refresh"],
  "rules": {
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn",
    "react-refresh/only-export-components": "warn"
  }
}
```

`exhaustive-deps` should be `warn`, not `error`, to allow intentional escape hatches when the engineer has verified the dependency is stable by other means (e.g. a ref). Never set it to `off`.

## Environment Variables

Use `.env` files with Vite's `VITE_` prefix for client-side variables. Never put secrets in client-side env vars — they are embedded in the bundle.

```bash
# .env.local
VITE_API_URL=https://api.example.com
# Secrets go server-side only — never VITE_ prefixed
```

```tsx
const apiUrl = import.meta.env.VITE_API_URL;
```
