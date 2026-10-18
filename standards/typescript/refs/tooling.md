---
last_reviewed: 2026-10-18
---

# TypeScript Tooling

## tsconfig

TypeScript 6.0 changed several defaults: `strict` is `true`, `types` is `[]`, `rootDir` is the folder that holds `tsconfig.json`, and `esModuleInterop` can no longer be `false`. `strict` still omits the checks listed after it below — add them explicitly.

Node.js service or CLI (Node 24, emitted by `tsc`):

```json
{
  "compilerOptions": {
    "target": "es2024",
    "lib": ["es2024"],
    "module": "nodenext",
    "types": ["node"],
    "rootDir": "./src",
    "outDir": "./dist",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noImplicitOverride": true,
    "noFallthroughCasesInSwitch": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "verbatimModuleSyntax": true,
    "isolatedModules": true,
    "erasableSyntaxOnly": true,
    "rewriteRelativeImportExtensions": true,
    "resolveJsonModule": true,
    "skipLibCheck": true
  },
  "include": ["src"]
}
```

Bundled app (Vite, Next.js, esbuild): use `"module": "esnext"`, `"moduleResolution": "bundler"`, `"noEmit": true`, and `"types"` for the runtime you target (for example `["vite/client"]`). Keep the strictness flags above.

Library: add `"declaration": true` and `"isolatedDeclarations": true` so declaration files can be generated per file without the type checker.

**Non-obvious traps:**

- **Pick `module` by runtime.** `nodenext` for code that Node.js loads directly; `bundler` resolution for code a bundler consumes. `moduleResolution: node10` is deprecated and `classic` is removed in 6.0.
- **`types` is `[]` by default in 6.0.** Without `"types": ["node"]` you get errors for `process`, `Buffer`, and `node:` imports. Add test-runner globals only where you use them (`"vitest/globals"`).
- **`rootDir` is no longer inferred from sources.** Without `"rootDir": "./src"`, `src/index.ts` emits to `dist/src/index.js`.
- **`erasableSyntaxOnly`** rejects `enum`, runtime `namespace`, parameter properties, and `import =`. Turn it on for any code that Node.js type stripping runs.
- **Relative imports carry the real extension.** Write `./user.ts`; `rewriteRelativeImportExtensions` rewrites it to `./user.js` on emit. For `noEmit` projects use `allowImportingTsExtensions` instead.
- **`verbatimModuleSyntax`**: imports without `type` are kept as written. A type imported without `import type` is a compile error, not a silent runtime import.
- **`exactOptionalPropertyTypes`**: without it, optional properties accept explicit `undefined` — `settings.theme = undefined` compiles even when `theme` is `"dark" | "light"`.
- **`noUncheckedIndexedAccess`**: `arr[0]` becomes `T | undefined`, forcing a narrow before use.
- **Removed or deprecated in 6.0** (hard errors in 7.0): `baseUrl`, `outFile`, `target: es5`, `downlevelIteration`, `module: amd|umd|system|none`, `esModuleInterop: false`. Delete them; do not hide them with `ignoreDeprecations`.
- **`paths` does not affect emitted output.** Prefer `package.json` `"imports"` (`#/…`) subpath imports, which Node.js and `tsc` both resolve.
- **`exclude` does not prevent compilation of imported files.**

### TypeScript 7

TypeScript 7.0 (native compiler) has no stable programmatic API. `typescript-eslint`, `ts-jest`, and other tools that import `typescript` still need 6.x. Use 7 for `tsc` and keep 6 installed under the `typescript` name:

```json
"devDependencies": {
  "@typescript/native": "npm:typescript@^7.0.0",
  "typescript": "npm:@typescript/typescript6@^6.0.0"
}
```

Check that `npx tsc --version` reports 7.x after install.

## ESLint

Flat config only (`eslint.config.*`). `tseslint.config()` is deprecated — use `defineConfig` from `eslint/config`. `strictTypeChecked` already includes `recommended`, `recommendedTypeChecked`, and `strict`, and it needs type information through `projectService`:

```javascript
// eslint.config.js
import { defineConfig } from 'eslint/config';
import js from '@eslint/js';
import tseslint from 'typescript-eslint';

export default defineConfig(
  js.configs.recommended,
  tseslint.configs.strictTypeChecked,
  {
    languageOptions: {
      parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname },
    },
    rules: {
      // Not in any preset
      '@typescript-eslint/switch-exhaustiveness-check': 'error',
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    },
  },
  {
    files: ['**/*.{js,mjs,cjs}'],
    extends: [tseslint.configs.disableTypeChecked],
  },
);
```

> When `strict` is off in tsconfig, `no-unsafe-*` rules produce excessive noise — suppress per line with a reason rather than disabling rules globally.

## Build And Run Tools

| Use case | Tool | Notes |
|----------|------|-------|
| CI type check | `tsc --noEmit` | Catches project-wide errors; LSP may miss cross-file issues |
| Run TS on Node (dev, scripts) | `node file.ts` | Native type stripping (stable in Node 24.12+); erasable syntax only, no type check |
| Run TS needing transforms | `tsx` | For `paths` aliases or non-erasable syntax in legacy code |
| Library bundling | `tsdown` | tsup is no longer maintained; `npx tsdown-migrate` converts configs |
| Web applications | Vite | Use the framework plugin |
| Transpile-only | esbuild / swc | No type checking — pair with `tsc --noEmit` in CI |

Enable `isolatedModules` with any transpile-only tool or type stripping.

## Vitest (default for new projects)

Use Vitest for new projects. Create a dedicated `vitest.config.ts` — it takes priority over `vite.config.ts`. If you share a Vite config, merge explicitly with `mergeConfig`; omitting it silently drops all Vite plugins:

```typescript
// vitest.config.ts
import { defineConfig, mergeConfig } from 'vitest/config';
import viteConfig from './vite.config';

export default mergeConfig(viteConfig, defineConfig({
  test: {
    include: ['src/**/*.test.ts'],
    environment: 'node',
    coverage: {
      provider: 'v8',
      include: ['src/**/*.ts'],
      thresholds: { lines: 80, functions: 80, branches: 80 },
    },
  },
}));
```

Import test APIs explicitly (`import { describe, expect, it, vi } from 'vitest'`). If you enable `globals: true`, add `"vitest/globals"` to tsconfig `types`.

## Jest (existing projects)

Keep Jest where the repo already uses it. Prefer `ts-jest` over Babel — Babel only transpiles, so type errors pass silently.

```typescript
// jest.config.ts
import type { Config } from 'jest';

const config: Config = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src'],
  testMatch: ['**/*.test.ts'],
  collectCoverageFrom: ['src/**/*.ts', '!src/**/*.d.ts'],
  coverageThreshold: {
    global: { branches: 80, functions: 80, lines: 80, statements: 80 },
  },
};

export default config;
```

Import test APIs from `@jest/globals` — the Jest team ships it in sync with the runtime. If you use `@types/jest` instead, match its major to Jest (`@types/jest@30` for Jest 30).

## CI Pipeline

Run the cheapest checks first: lint, typecheck, test, build.

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
          node-version-file: '.nvmrc'   # pins Node 24 LTS in one place
          cache: 'npm'
      - run: npm ci
      - run: npx eslint . --max-warnings 0
      - run: npx tsc --noEmit
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
- `@types/jest` major that differs from the Jest major — or use `@jest/globals`
- `vitest.config.ts` without `mergeConfig` when a `vite.config.ts` exists — silently drops all Vite plugins
- Relying on `strict` alone — `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noImplicitReturns`, and the unused checks are not included
- Missing `"types"` after upgrading to 6.0, or `"types": ["*"]` kept as a permanent fix
- Deprecated options silenced with `ignoreDeprecations` — TypeScript 7 rejects them
- `tseslint.config()` or `.eslintrc.*` in new config
- Type-aware lint presets without `projectService`
- Running tests or the build before lint and typecheck — fail fast on the cheapest checks
