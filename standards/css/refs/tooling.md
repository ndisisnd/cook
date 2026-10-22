---
last_reviewed: 2026-10-18
---

# Tooling

Use this ref when configuring the CSS toolchain: Stylelint, Prettier, PostCSS/Lightning CSS, autoprefixer/browser targets, or Sass/SCSS conventions and native nesting.

## Stylelint

Extend `stylelint-config-standard` (+ `-scss`), add `stylelint-order`. Run in CI and pre-commit; `--fix` handles ordering and notation.

```jsonc
{
  "rules": {
    "no-descending-specificity": true,
    "declaration-no-important": [true, { "severity": "warning" }],
    "selector-max-specificity": "0,4,1",
    "selector-max-id": 0,
    "color-function-notation": "modern"
  },
  "overrides": [{ "files": ["**/reset.css", "**/base.css"], "rules": { "selector-max-specificity": null } }]
}
```

- The `,1` type allowance is deliberate: element selectors in reset/base (`0,0,1`) would fail a `0,x,0` cap. Reset/base files are also exempted via `overrides`.
- Prettier owns formatting; Stylelint owns rules. Do not enable Stylelint stylistic rules that overlap Prettier.

## Build pipeline

- **PostCSS** (`autoprefixer` + `postcss-preset-env`) or **Lightning CSS** (Rust, used by Vite/Parcel; prefixing, minification, lowering in one pass). Prefer Lightning CSS in new Vite/Bun setups.
- Drive both from a single `browserslist` — never hand-write vendor prefixes: `"browserslist": ["baseline widely available"]`. Widen it (for example `baseline widely available with downstream`) only for a known audience need.

## Native nesting vs Sass

- CSS nests natively (`&`, nested `@media`); you may not need Sass.
- Native nesting differs slightly from Sass in selector matching. Keep nesting ≤ 3 levels; deep nesting inflates specificity.

### Sass/SCSS (when used)

- Use `@use` / `@forward`, never the deprecated `@import`.
- Use Sass only for what native CSS lacks: `@each`/`@for`, maps, complex mixins, math. Use custom properties, not `$variables`, for anything themeable → `refs/theming.md`.
- Avoid the `&__element` BEM-via-nesting trap; it hides real specificity.
- Prefer `math.div()` over the deprecated `/` division; run the Sass migrator for legacy `@import` codebases.
