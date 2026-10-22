---
last_reviewed: 2026-10-18
---

# TypeScript Tooling

## tsconfig

TypeScript 6.0 defaults: `strict` is `true`, `types` is `[]`, `rootDir` is the `tsconfig.json` folder, `esModuleInterop` cannot be `false`. `strict` omits the checks below — add them explicitly.

Node.js service or CLI (Node 24, emitted by `tsc`):

```json
{
  "compilerOptions": {
    "target": "es2024", "lib": ["es2024"],
    "module": "nodenext", "types": ["node"],
    "rootDir": "./src", "outDir": "./dist",
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

- Bundled app (Vite, Next.js, esbuild): `"module": "esnext"`, `"moduleResolution": "bundler"`, `"noEmit": true`, `"types"` for the target runtime (e.g. `["vite/client"]`). Keep the strictness flags.
- Library: add `"declaration": true`, `"isolatedDeclarations": true`.

**Non-obvious traps:**

- `nodenext` for code Node.js loads directly; `bundler` for bundled code. `moduleResolution: node10` is deprecated; `classic` is removed in 6.0.
- Without `"types": ["node"]`, `process`, `Buffer`, and `node:` imports error. Add test globals only where used (`"vitest/globals"`).
- Without `"rootDir": "./src"`, output lands in `dist/src/`.
- `erasableSyntaxOnly` rejects `enum`, runtime `namespace`, parameter properties, `import =`. Enable for code run by Node.js type stripping.
- Relative imports carry the real extension: write `./user.ts`; `rewriteRelativeImportExtensions` emits `./user.js`. For `noEmit` projects use `allowImportingTsExtensions`.
- `verbatimModuleSyntax`: a type imported without `import type` is a compile error.
- Removed or deprecated in 6.0 (hard errors in 7.0): `baseUrl`, `outFile`, `target: es5`, `downlevelIteration`, `module: amd|umd|system|none`, `esModuleInterop: false`. Delete them; do not hide them with `ignoreDeprecations`.
- `paths` does not affect emitted output. Prefer `package.json` `"imports"` (`#/…`), which Node.js and `tsc` both resolve.

### TypeScript 7

TypeScript 7.0 (native compiler) has no stable programmatic API. `typescript-eslint`, `ts-jest`, and other tools importing `typescript` still need 6.x. Use 7 for `tsc`, keep 6 under the `typescript` name, and check `npx tsc --version` reports 7.x:

```json
"devDependencies": {
  "@typescript/native": "npm:typescript@^7.0.0",
  "typescript": "npm:@typescript/typescript6@^6.0.0"
}
```

## ESLint

Flat config only (`eslint.config.*`); no `.eslintrc.*`. `tseslint.config()` is deprecated — use `defineConfig` from `eslint/config`. `strictTypeChecked` already includes `recommended`, `recommendedTypeChecked`, and `strict`, and needs `projectService`:

Compose with `defineConfig(js.configs.recommended, tseslint.configs.strictTypeChecked, {...})`:

- `languageOptions.parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname }`.
- Add `@typescript-eslint/switch-exhaustiveness-check: 'error'` (in no preset) and `no-unused-vars` with `argsIgnorePattern: '^_'`.
- Add a `files: ['**/*.{js,mjs,cjs}']` block with `extends: [tseslint.configs.disableTypeChecked]`.

With `strict` off, `no-unsafe-*` is noisy — suppress per line with a reason, never globally.

## Build And Run Tools

- `node file.ts` for dev and scripts: native type stripping (stable in Node 24.12+), erasable syntax only, no type check. Use `tsx` for `paths` aliases or non-erasable syntax in legacy code.
- Library bundling: `tsdown` (tsup is unmaintained; `npx tsdown-migrate` converts configs).
- Transpile-only tools (esbuild, swc, type stripping): no type check — pair with `tsc --noEmit` in CI and enable `isolatedModules`.

## Vitest (default for new projects)

- Use a dedicated `vitest.config.ts`; it takes priority over `vite.config.ts`.
- When sharing a Vite config, use `mergeConfig(viteConfig, defineConfig({ test: {...} }))` from `vitest/config`; omitting it silently drops all Vite plugins.
- Coverage `provider: 'v8'`. With `globals: true`, add `"vitest/globals"` to tsconfig `types`; otherwise import test APIs from `vitest`.

## Jest (existing projects)

- Keep Jest where the repo uses it. Prefer `ts-jest` over Babel (Babel does not type-check).
- Import test APIs from `@jest/globals`. With `@types/jest`, match its major to Jest (`@types/jest@30` for Jest 30).

## CI

- Order cheapest first: `eslint . --max-warnings 0`, `tsc --noEmit`, test with coverage, build. Pin Node with `actions/setup-node@v4` `node-version-file: '.nvmrc'`.
