<!-- AUTO-GENERATED from SKILL.md frontmatters — do not edit manually -->
# css Skills Index

## File Match (auto-check against the file you are editing)

| Skill | File pattern | Keywords |
| ----- | ------------ | -------- |
| **css** | `**/*.css`, `**/*.scss`, `**/*.sass`, `**/*.less`, `**/*.pcss`, `**/*.postcss` | stylesheet, cascade, specificity, @layer, flexbox, grid, container query, media query, custom property, css variable, design token, dark mode, clamp, logical property, z-index, keyframes, transition, focus-visible, prefers-reduced-motion, tailwind, @apply, utility class, sass, scss, postcss |
| css → architecture ref | — | @layer, cascade layer, BEM, ITCSS, CSS Modules, @scope, specificity, methodology, naming |
| css → layout ref | `**/*.css`, `**/*.scss` | flexbox, grid, subgrid, container query, logical property, clamp, aspect-ratio, intrinsic, breakpoint, gap |
| css → theming ref | `**/tokens/**`, `**/theme.css`, `**/*.tokens.css` | custom property, design token, dark mode, color-scheme, light-dark, oklch, @property, theming, color-mix |
| css → performance ref | — | performance, contain, content-visibility, will-change, critical css, font-display, reflow, repaint, compositor |
| css → accessibility ref | — | focus-visible, prefers-reduced-motion, forced-colors, contrast, sr-only, target size, accessibility, a11y |
| css → tailwind ref | `tailwind.config.*`, `**/*.tsx`, `**/*.jsx`, `**/*.html`, `**/*.vue`, `**/*.svelte` | tailwind, tailwindcss, @apply, @theme, utility class, cn, tailwind-merge, cva, arbitrary value, tailwind.config |
| css → tooling ref | `.stylelintrc.*`, `postcss.config.*`, `**/*.scss`, `browserslist` | stylelint, postcss, autoprefixer, lightningcss, sass, scss, @use, @forward, nesting, browserslist |
| css → security ref | — | css injection, exfiltration, third-party css, @import, clickjacking, sanitize styles, expression |

> Load `<SKILLS>/css/SKILL.md` for any `.css`, `.scss`, `.sass`, `.less`, or PostCSS file — a small set of battle-tested principles (keep specificity low, scope by default, tokenize, lay out with Flexbox/Grid, use the platform, compose over override) plus a minimal accessibility/security floor. It's the whole standard for most styling work; pull a ref only for depth.
>
> Load `<SKILLS>/css/refs/architecture.md` when choosing a methodology, setting up `@layer`, scoping with CSS Modules/`@scope`, or managing specificity at scale.
>
> Load `<SKILLS>/css/refs/layout.md` when building layout with Flexbox/Grid/subgrid, container queries, logical properties, intrinsic sizing, or fluid `clamp()` type.
>
> Load `<SKILLS>/css/refs/theming.md` when defining design tokens, building light/dark themes (`color-scheme`/`light-dark()`), or using `oklch()`/`color-mix()`/`@property`.
>
> Load `<SKILLS>/css/refs/performance.md` when diagnosing jank/reflow, adding animation, using `contain`/`content-visibility`, splitting critical CSS, or loading web fonts.
>
> Load `<SKILLS>/css/refs/accessibility.md` when handling focus (`:focus-visible`), motion safety, contrast/`forced-colors`, target sizes, or screen-reader-only content.
>
> Load `<SKILLS>/css/refs/tailwind.md` when authoring or reviewing Tailwind — utility discipline, `@theme`/config, `cn()`/`tailwind-merge`, `cva` component variants, arbitrary values, and dark mode.
>
> Load `<SKILLS>/css/refs/tooling.md` when configuring Stylelint, Prettier, PostCSS/Lightning CSS, `browserslist`, or Sass `@use`/`@forward` and native nesting.
>
> Load `<SKILLS>/css/refs/security.md` when CSS crosses a trust boundary — user-generated styles, third-party/`@import` CSS, values from input, or selector-based data exfiltration.

## Notes

- CSS is presentation-layer only. Component/markup structure lives in the framework shelves (`<SKILLS>/react/`, `<SKILLS>/nextjs/`, `<SKILLS>/flutter/`); universal architecture and the full security library live in `<SKILLS>/global/` and `<SKILLS>/security/`.
- Framework-level styling integration (RSC compatibility, `next/font`, image/bundle optimization) lives in `<SKILLS>/nextjs/refs/styling-and-optimization.md`; the Tailwind *CSS-authoring* rules live here in `refs/tailwind.md`.
