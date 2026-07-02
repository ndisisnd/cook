# Tooling

Use this ref when configuring the CSS toolchain: Stylelint, Prettier, PostCSS/Lightning CSS, autoprefixer/browser targets, or Sass/SCSS conventions and native nesting.

## Stylelint

Lint CSS/SCSS for correctness and consistency. Start from the standard config and add ordering.

```jsonc
// .stylelintrc.json
{
  "extends": ["stylelint-config-standard", "stylelint-config-standard-scss"],
  "plugins": ["stylelint-order"],
  "rules": {
    "no-descending-specificity": true,
    "declaration-no-important": [true, { "severity": "warning" }],
    "selector-max-specificity": "0,4,1",
    "selector-max-id": 0,
    "color-function-notation": "modern",
    "order/properties-order": [ /* positioning → box → typography → visual */ ]
  },
  "overrides": [
    {
      "files": ["**/reset.css", "**/base.css"],
      "rules": { "selector-max-specificity": null }
    }
  ]
}
```

- `selector-max-specificity` / `selector-max-id` mechanically enforce the flat-specificity rule from the SKILL. The `,1` type allowance is deliberate: the SKILL permits element selectors in reset/base (`body {}`, `a {}`), which have specificity `0,0,1` and would fail a `0,x,0` cap. Reset/base files are further exempted via `overrides`, since element-targeted resets legitimately combine a few type selectors.
- Run Stylelint in CI and pre-commit; `--fix` handles ordering and notation automatically.

## Formatting

- **Prettier** owns whitespace/formatting; Stylelint owns rules. Disable Stylelint's stylistic rules that overlap Prettier (`stylelint-config-standard` already defers formatting).
- One declaration per line; consistent quote and colour-notation style (enforced, not debated).

## Build pipeline — PostCSS / Lightning CSS

- **PostCSS** with `autoprefixer` + `postcss-preset-env` transforms modern CSS for the target browser matrix, or
- **Lightning CSS** (Rust, used by Vite/Parcel) — faster, does prefixing + minification + syntax lowering in one pass. Prefer it in new Vite/Bun setups.
- Drive both from a single **`browserslist`** — never hand-write vendor prefixes:

```jsonc
// package.json
"browserslist": ["> 0.5%", "last 2 versions", "not dead"]
```

`browserslist` is the single source of truth for autoprefixer, `postcss-preset-env`, and Lightning CSS. Tightening it drops dead prefixes and shrinks output.

## Native nesting vs Sass

CSS now nests natively — you may not need Sass at all.

```css
.card {
  padding: var(--space-4);
  & > .card__title { font-weight: 600; }
  &:hover { background: var(--surface-hover); }
  @media (min-width: 48rem) { padding: var(--space-6); }
}
```

Caveats: native nesting has some selector-matching differences from Sass; keep nesting **≤ 3 levels** (deep nesting produces high-specificity, brittle selectors regardless of preprocessor).

### Sass/SCSS conventions (when you do use it)

- Use the **module system**: `@use` / `@forward`, never the deprecated `@import`.

```scss
@use 'tokens' as *;
@use 'mixins';
.card { padding: mixins.pad(4); }
```

- Reach for Sass only for what native CSS lacks: `@each`/`@for` loops, maps, complex mixins, math. Use **custom properties**, not `$variables`, for anything themeable/runtime → `refs/theming.md`.
- Keep nesting shallow; avoid the `&__element` BEM-via-nesting trap that hides real specificity.
- Prefer `math.div()` over the deprecated `/` division; run the Sass migrator for legacy `@import` codebases.

## Anti-Patterns

- Hand-written vendor prefixes instead of a `browserslist`-driven autoprefixer/Lightning CSS.
- Stylelint and Prettier fighting over formatting (overlapping stylistic rules enabled).
- No CI/pre-commit lint — specificity and `!important` creep go unnoticed.
- Sass `@import` (deprecated, global namespace) in new code instead of `@use`/`@forward`.
- Deep nesting (native or Sass) that silently inflates specificity.
- Using Sass variables where a runtime-themeable custom property is required.
