---
name: css
description: Pragmatic, battle-tested CSS conventions. Use when authoring or reviewing styles — a small set of durable principles (keep specificity low, scope by default, tokenize, respect the user) plus a minimal accessibility/security floor. CSS is forgiving, so this favours judgment and consistency over rigid rules; depth (layout, theming, performance, Tailwind, tooling) lives in refs.
metadata:
  targets: "Baseline Widely Available (web-features, Oct 2026) · Tailwind CSS v4"
  last_reviewed: 2026-10-18
  triggers:
    files:
      - '**/*.css'
      - '**/*.scss'
      - '**/*.sass'
      - '**/*.less'
      - '**/*.pcss'
      - '**/*.postcss'
      - '**/*.module.css'
      - '**/*.module.scss'
    keywords:
      - stylesheet
      - cascade
      - specificity
      - '@layer'
      - cascade layer
      - flexbox
      - grid
      - container query
      - media query
      - custom property
      - css variable
      - design token
      - dark mode
      - clamp
      - logical property
      - z-index
      - keyframes
      - transition
      - focus-visible
      - prefers-reduced-motion
      - tailwind
      - '@apply'
      - utility class
      - sass
      - scss
      - postcss
---

# CSS

Target: Baseline Widely Available browsers; Tailwind CSS v4 for Tailwind projects.

Optimise for **consistency, low specificity, and not breaking the user**. This file is the whole standard for most work; pull a ref only for depth.

The biggest lever is **matching what the codebase already does**. Propose a methodology or tooling migration (BEM ↔ utilities, adding Tailwind, swapping Sass) as its own task, never inside a feature change.

## Principles

1. **Keep specificity low and flat.** Style with a single class, keep selectors shallow, and avoid IDs and `!important`. When cascade order matters, use `@layer`, not more selectors. → `refs/architecture.md`
2. **Scope by default.** Use CSS Modules, BEM/utilities, or `@scope`; keep bare element selectors to resets and base. → `refs/architecture.md`
3. **Tokenize; don't hardcode.** One source of truth for colour, spacing, and type. Use custom properties for anything themeable; derive values from a scale, not magic numbers. → `refs/theming.md`
4. **Lay out with Flexbox and Grid,** not floats, absolute positioning, or fixed heights. Prefer `gap`, intrinsic sizing, and container queries over media queries. → `refs/layout.md`
5. **Use the platform; don't over-tool.** Nesting, custom properties, `clamp()`, and `color-mix()` replace most preprocessor use. Add Sass/PostCSS/Tailwind only for real team leverage. Use newer-than-Baseline features only as progressive enhancement; `browserslist`: `baseline widely available`. → `refs/tooling.md`, `refs/tailwind.md`
6. **Prefer deleting and composing over overriding.** Every override is future debt. If a rule defeats another rule, fix the first one.

## Modern features — Baseline status (web-features, Oct 2026)

- **Widely Available — use freely:** `:has()`, native nesting, subgrid, container size queries, `@layer`.
- Newly Available and Limited features (popover, view transitions, anchor positioning, scroll-driven animations): use with a fallback, gate with `@supports` → `refs/layout.md`

## The floor (non-negotiable)

- **Don't break reflow or zoom.** Content must reflow with no horizontal scroll down to 320px and stay usable at 400% zoom. Size text in `rem`; never disable zoom.
- **Keep focus visible.** Never ship `outline: none` (or `0`) without a visible `:focus-visible` replacement.
- **Respect motion and colour.** Gate every non-essential animation behind `prefers-reduced-motion`; never convey meaning (error, status, required) by colour alone; keep body-text contrast ≥ 4.5:1. → `refs/accessibility.md`
- **Never put untrusted input into CSS** — `url()`, `content`, custom-property values, or an injected `<style>`. → `refs/security.md`

## Judgment, not dogma

Naming, declaration order, and units are team conventions. Enforce them with Stylelint/Prettier.

## Anti-Patterns

- `z-index: 9999` escalation instead of a small named scale.
- `transition: all`, or animating layout props (`width`/`top`/`margin`) instead of `transform`/`opacity`.

## References

Load a ref only when the task needs that depth.

- [architecture](refs/architecture.md) — methodology and scale: cascade layers (`@layer`), BEM/ITCSS/utility-first, `@scope` and CSS Modules, specificity strategy, file/folder organization; keywords: @layer, cascade layer, BEM, ITCSS, CSS Modules, @scope, specificity, methodology, naming
- [layout](refs/layout.md) — modern layout and responsive: Flexbox, Grid, subgrid, container queries, logical properties, intrinsic sizing, `aspect-ratio`, fluid type with `clamp()`, viewport units, breakpoint strategy; keywords: flexbox, grid, subgrid, container query, logical property, clamp, aspect-ratio, intrinsic, breakpoint, gap
- [theming](refs/theming.md) — custom properties, design-token layering, `color-scheme`/`light-dark()` dark mode, `oklch()` and modern colour, `@property`, relative colour syntax; keywords: custom property, design token, dark mode, color-scheme, light-dark, oklch, @property, theming, color-mix
- [performance](refs/performance.md) — selector cost, `contain`/`content-visibility`, compositor-only animation, `will-change` discipline, critical CSS, font loading (`font-display`, `size-adjust`), reducing paint/layout; keywords: performance, contain, content-visibility, will-change, critical css, font-display, reflow, repaint, compositor
- [accessibility](refs/accessibility.md) — `:focus-visible`, `prefers-reduced-motion`, `prefers-contrast`/`forced-colors`, colour contrast, target sizes, screen-reader-only utilities, motion safety; keywords: focus-visible, prefers-reduced-motion, forced-colors, contrast, sr-only, target size, accessibility, a11y
- [tailwind](refs/tailwind.md) — TailwindCSS (v4 CSS-first `@theme` + v3 config), utility-first discipline, `cn()`/`tailwind-merge`, component extraction, arbitrary values, dark mode, plugins, content detection; keywords: tailwind, tailwindcss, @apply, @theme, utility class, cn, tailwind-merge, cva, arbitrary value, tailwind.config
- [tooling](refs/tooling.md) — Stylelint, Prettier, PostCSS/Lightning CSS pipeline, autoprefixer, Sass/SCSS conventions (`@use`/`@forward`, nesting depth), native CSS nesting, `browserslist`; keywords: stylelint, postcss, autoprefixer, lightningcss, sass, scss, @use, @forward, nesting, browserslist
- [security](refs/security.md) — CSS injection, attribute-selector data exfiltration, third-party/`@import` risk, clickjacking overlays, user-generated-style sanitization; keywords: css injection, exfiltration, third-party css, @import, clickjacking, sanitize styles, expression
