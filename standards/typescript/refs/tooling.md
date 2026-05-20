# TypeScript Tooling

## tsconfig

`strict: true` enables 9 flags but silently omits 4 meaningful checks. Always add them explicitly:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "node16",
    "moduleResolution": "node16",
    "lib": ["ES2022"],
    "rootDir": "src",
    "outDir": "dist",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "exactOptionalPropertyTypes": true,
    "noUncheckedIndexedAccess": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "isolatedModules": true
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

**Non-obvious traps:**

- **`moduleResolution` defaults are wrong for ESM.** `module: "esnext"` defaults to `classic`. Always set it explicitly: `node16` for Node.js, `bundler` for Vite/esbuild.
- **`rootDir` inference produces unexpected nesting.** Without it, `src/utils/math.ts` may emit to `dist/src/utils/math.js`. Set it explicitly.
- **`exactOptionalPropertyTypes`**: without this flag, optional properties silently accept explicit `undefined` — `settings.theme = undefined` compiles even when `theme` is typed as `"dark" | "light"`.
- **`noUncheckedIndexedAccess`**: `arr[0]` becomes `T | undefined`, forcing explicit narrowing before use. Off by default; worth enabling.
- **`paths` does not affect emitted output.** It only helps TypeScript resolve types. Your bundler must also be configured to remap paths at runtime, or runtime lookups fail.
- **`exclude` does not prevent compilation of imported files.** A file excluded from globs is still compiled if another included file imports it.

## ESLint

`@typescript-eslint/recommended` is the baseline. Add **strict** tier rules that catch real bugs:

```javascript
// eslint.config.js (flat config)
import tseslint from 'typescript-eslint';

export default tseslint.config(
  ...tseslint.configs.recommended,
  ...tseslint.configs.strict,
  {
    rules: {
      // Catch unhandled async — recommended doesn't include these
      '@typescript-eslint/no-floating-promises': 'error',
      '@typescript-eslint/no-misused-promises':  'error',
      '@typescript-eslint/await-thenable':        'error',
      // Exhaustiveness and dead code
      '@typescript-eslint/switch-exhaustiveness-check': 'error',
      '@typescript-eslint/no-unnecessary-condition':    'warn',
      // Replace core ESLint rules with TS-aware equivalents
      'no-unused-vars': 'off',
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    },
  }
);
```

> When `strict: false` in tsconfig, `no-unsafe-*` rules produce excessive noise — suppress selectively with `@ts-expect-error` rather than disabling rules globally.

## Build Tools

| Use case | Tool | Notes |
|----------|------|-------|
| CI type check | `tsc --noEmit` | Catches project-wide errors; LSP may miss cross-file issues |
| Development iteration | `ts-node` / `tsx` | No build step needed |
| Library bundling | `tsup` | Generates CJS + ESM + `.d.ts` in one command |
| Web applications | `Vite` | Use `@vitejs/plugin-react` or equivalent |
| Transpile-only | `esbuild` / `swc` | No type checking — pair with a separate `tsc --noEmit` in CI |

Enable `isolatedModules: true` when using a transpile-only tool. It catches cross-file emit issues (const enum, namespace re-exports) that esbuild/swc cannot handle.

## Jest

Prefer `ts-jest` over Babel for TypeScript projects. Babel only transpiles — it does not type-check during test runs, so type errors pass silently.

```typescript
// jest.config.ts
import type { Config } from 'jest';

const config: Config = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src'],
  testMatch: ['**/__tests__/**/*.ts', '**/?(*.)+(spec|test).ts'],
  collectCoverageFrom: ['src/**/*.ts', '!src/**/*.d.ts'],
  coverageThreshold: {
    global: { branches: 80, functions: 80, lines: 80, statements: 80 },
  },
};

export default config;
```

Use `@jest/globals` for test imports — it is maintained by the Jest team and always in sync with the runtime:

```typescript
import { describe, expect, test, jest } from '@jest/globals';
```

If you use `@types/jest` instead, pin its major version to match your Jest version (`@types/jest@29.x` for Jest 29). A version mismatch causes subtle type errors and incorrect autocomplete.

## Vitest

Create a dedicated `vitest.config.ts` — it takes priority over `vite.config.ts`. If you share a Vite config, merge explicitly with `mergeConfig`; omitting it silently drops all Vite plugins:

```typescript
// vitest.config.ts
import { defineConfig, mergeConfig } from 'vitest/config';
import viteConfig from './vite.config';

export default mergeConfig(viteConfig, defineConfig({
  test: {
    globals: true,
    environment: 'node',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['**/*.d.ts'],
      thresholds: { lines: 80, functions: 80, branches: 80 },
    },
  },
}));
```

## CI Pipeline

```yaml
# .github/workflows/ci.yml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npx tsc --noEmit
      - run: npx eslint . --max-warnings 0
      - run: npm test -- --coverage
      - run: npm run build
```

## Pre-commit (lint-staged + Husky)

```json
// package.json
{
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --fix", "prettier --write"],
    "*.{js,json,md}": "prettier --write"
  }
}
```

```bash
# .husky/pre-commit
npx lint-staged
npx tsc --noEmit
```

## Anti-Patterns

- Babel-only test setup — Babel transpiles but does not type-check; real type errors pass silently
- `@types/jest` version mismatch with Jest runtime — pin major versions or use `@jest/globals`
- `vitest.config.ts` without `mergeConfig` — silently drops all Vite plugins
- `strict: true` without companion flags — `noUnusedLocals`, `noImplicitReturns`, and others are not included
- Running `tsc` / build steps before `eslint` and type check — fail fast on the cheapest checks first
