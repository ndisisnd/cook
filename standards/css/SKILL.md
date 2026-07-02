---
name: css
description: Pragmatic, battle-tested CSS conventions. Use when authoring or reviewing styles — a small set of durable principles (keep specificity low, scope by default, tokenize, respect the user) plus a minimal accessibility/security floor. CSS is forgiving, so this favours judgment and consistency over rigid rules; depth (layout, theming, performance, Tailwind, tooling) lives in refs.
metadata:
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

CSS is forgiving and subjective — there is rarely one "correct" stylesheet. Optimise for **consistency, low specificity, and not breaking the user**, not for rule-compliance. This file is the whole standard for most styling work; pull a ref only when you need depth.

The single biggest lever is **matching what the codebase already does**. A convention you'd not have picked, applied consistently, beats a "better" one applied unevenly. Propose a methodology or tooling migration (BEM ↔ utilities, adding Tailwind, swapping Sass) as its own explicit task — never as a drive-by inside a feature change.

## Principles (battle-tested)

1. **Keep specificity low and flat.** Style with a single class, keep selectors shallow, and avoid IDs and `!important`. Low, even specificity is what keeps styles overridable — most CSS pain is a specificity war that someone started and everyone else inherited. When cascade order genuinely matters, control it with `@layer`, not by piling on selectors. → `refs/architecture.md`
2. **Scope by default.** Leaking styles is the root cause of most "why did *that* change?" bugs. Reach for CSS Modules, a naming convention (BEM/utilities), or `@scope`; keep bare element selectors to resets and base. → `refs/architecture.md`
3. **Tokenize; don't hardcode.** Keep one source of truth for colour, spacing, and type. Use custom properties for anything themeable, and derive values from a scale instead of scattering magic numbers. → `refs/theming.md`
4. **Lay out with Flexbox and Grid.** They solve cleanly what floats, absolute positioning, and fixed heights only ever hacked around. Reach for `gap`, intrinsic sizing, and container queries before adding media queries. → `refs/layout.md`
5. **Use the platform; don't over-tool.** Modern CSS (nesting, custom properties, `clamp()`, `color-mix()`) covers most of what preprocessors were for. Add Sass/PostCSS/Tailwind because the team gets real leverage from it, not by reflex — and don't ship a shiny new feature to production without checking your browser support. → `refs/tooling.md`, `refs/tailwind.md`
6. **Prefer deleting and composing over overriding.** CSS only ever grows, and every override is future debt. If you're writing a rule to defeat another rule, fix the first one instead.

## The floor (non-negotiable)

The few rules that don't bend to taste, because they protect users:

- **Don't break reflow or zoom.** Content must reflow with no horizontal scroll down to a 320px viewport and stay usable at 400% zoom. Size text in `rem`; never disable zoom.
- **Keep focus visible.** Never ship `outline: none` (or `outline: 0`) without a visible `:focus-visible` replacement.
- **Respect motion and colour.** Gate non-essential motion behind `prefers-reduced-motion`; never convey meaning (error, status, required) by colour alone; keep body-text contrast ≥ 4.5:1. → `refs/accessibility.md`
- **Never put untrusted input into CSS** — `url()`, `content`, custom-property values, or an injected `<style>`. → `refs/security.md`

## Judgment, not dogma

Naming style, declaration order, unit choices, and which nice modern feature to use are **team conventions**. Pick one, enforce it with Stylelint/Prettier so it never becomes a review conversation, and move on. Don't bikeshed anything a linter can settle. The principles and floor above exist to keep CSS overridable, scoped, and usable — everything else is preference, and reasonable engineers differ.

## Anti-Patterns (the ones that actually hurt)

- `!important`, ID selectors, or deep descendant chains used to win a specificity war you created.
- Global element selectors (outside a reset) that leak across the app.
- `z-index: 9999` escalation instead of a small named scale.
- `float` / absolute positioning / fixed heights used for structural layout.
- Magic-number values where a token or scale belongs.
- `outline: none` with no focus replacement; motion with no reduced-motion guard; meaning carried by colour alone.
- `transition: all`, or animating layout props (`width`/`top`/`margin`) instead of `transform`/`opacity`.
- Untrusted input interpolated into `url()`, `content`, or custom properties.
- Rewriting a file's whole convention mid-feature instead of matching what's already there.

## References

Load a ref only when the task needs that depth — the principles above are the standard for most work.

- [architecture](refs/architecture.md) — methodology and scale: cascade layers (`@layer`), BEM/ITCSS/utility-first, `@scope` and CSS Modules, specificity strategy, file/folder organization; keywords: @layer, cascade layer, BEM, ITCSS, CSS Modules, @scope, specificity, methodology, naming
- [layout](refs/layout.md) — modern layout and responsive: Flexbox, Grid, subgrid, container queries, logical properties, intrinsic sizing, `aspect-ratio`, fluid type with `clamp()`, viewport units, breakpoint strategy; keywords: flexbox, grid, subgrid, container query, logical property, clamp, aspect-ratio, intrinsic, breakpoint, gap
- [theming](refs/theming.md) — custom properties, design-token layering, `color-scheme`/`light-dark()` dark mode, `oklch()` and modern colour, `@property`, relative colour syntax; keywords: custom property, design token, dark mode, color-scheme, light-dark, oklch, @property, theming, color-mix
- [performance](refs/performance.md) — selector cost, `contain`/`content-visibility`, compositor-only animation, `will-change` discipline, critical CSS, font loading (`font-display`, `size-adjust`), reducing paint/layout; keywords: performance, contain, content-visibility, will-change, critical css, font-display, reflow, repaint, compositor
- [accessibility](refs/accessibility.md) — `:focus-visible`, `prefers-reduced-motion`, `prefers-contrast`/`forced-colors`, colour contrast, target sizes, screen-reader-only utilities, motion safety; keywords: focus-visible, prefers-reduced-motion, forced-colors, contrast, sr-only, target size, accessibility, a11y
- [tailwind](refs/tailwind.md) — TailwindCSS (v4 CSS-first `@theme` + v3 config), utility-first discipline, `cn()`/`tailwind-merge`, component extraction, arbitrary values, dark mode, plugins, content detection; keywords: tailwind, tailwindcss, @apply, @theme, utility class, cn, tailwind-merge, cva, arbitrary value, tailwind.config
- [tooling](refs/tooling.md) — Stylelint, Prettier, PostCSS/Lightning CSS pipeline, autoprefixer, Sass/SCSS conventions (`@use`/`@forward`, nesting depth), native CSS nesting, `browserslist`; keywords: stylelint, postcss, autoprefixer, lightningcss, sass, scss, @use, @forward, nesting, browserslist
- [security](refs/security.md) — CSS injection, attribute-selector data exfiltration, third-party/`@import` risk, clickjacking overlays, user-generated-style sanitization; keywords: css injection, exfiltration, third-party css, @import, clickjacking, sanitize styles, expression
