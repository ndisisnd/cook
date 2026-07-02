# Tailwind CSS

Use this ref when authoring or reviewing Tailwind: utility-first discipline, theme/token configuration (v4 `@theme` or v3 `tailwind.config`), the `cn()` merge pattern, component extraction, arbitrary values, dark mode, and plugins.

Tailwind is a **delivery mechanism for the same cascade** — the CSS `SKILL.md` still applies (specificity, responsive, accessibility, logical thinking). Tailwind's job is to make design-token-constrained styling fast and consistent. In a Next.js/React project, framework-integration concerns (RSC compatibility, `next/font`, bundle) live in `standards/nextjs/refs/styling-and-optimization.md`; **this ref owns the Tailwind CSS-authoring rules**.

## v4 vs v3 — know which you're in

| | v4 (current) | v3 |
|---|---|---|
| Config | **CSS-first** — `@theme` in CSS | `tailwind.config.js` (JS) |
| Import | `@import "tailwindcss";` | `@tailwind base/components/utilities;` |
| Engine | Oxide (Rust), Lightning CSS built in | PostCSS + JS |
| Content detection | Automatic | `content: [...]` globs required |
| Prefixing/nesting | Built in | Needs PostCSS plugins |

Default new projects to **v4**. Match the existing version in an existing project — don't mix paradigms.

### v4 setup (CSS-first)

```css
/* app.css */
@import "tailwindcss";

@theme {
  --color-brand: oklch(0.55 0.2 255);
  --font-display: "Inter", sans-serif;
  --spacing-18: 4.5rem;          /* extends the spacing scale → utilities like p-18 */
  --breakpoint-3xl: 120rem;
}
```

Theme values in `@theme` become both CSS custom properties **and** utility classes (`bg-brand`, `font-display`, `p-18`). One source of truth.

### v3 setup

```js
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{ts,tsx,html}'],   // MUST cover every file using classes
  theme: { extend: { colors: { brand: 'oklch(0.55 0.2 255)' } } },
};
```

In v3, an incomplete `content` glob is the #1 bug — classes get purged and silently disappear in production.

## Utility-first discipline

- **Style with utilities in markup by default.** The verbosity is the tradeoff for locality, no naming, and dead-CSS-free output.
- **Never construct class names by string concatenation** — Tailwind's scanner sees source text literally, so `` `text-${color}-500` `` won't be generated. Map to complete class strings:

```tsx
// BAD — purged, class never generated
<div className={`text-${color}-500`} />

// GOOD — full class names present in source
const TONE = { danger: 'text-red-500', ok: 'text-green-500' } as const;
<div className={TONE[tone]} />
```

- Read utility order as **layout → box → typography → visual → state/responsive**; use `prettier-plugin-tailwindcss` to sort automatically and end the debate.
- Prefer Tailwind's **scale tokens** (`p-4`, `text-lg`, `gap-6`) over arbitrary values — the scale *is* the design system.

## `cn()` — conditional & merged classes

Combine `clsx` (conditional) with `tailwind-merge` (dedupe conflicting utilities so the last wins). This is the standard pattern; use it wherever classes are dynamic or overridable.

```ts
// lib/utils.ts
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
export const cn = (...inputs: ClassValue[]) => twMerge(clsx(inputs));
```

```tsx
<button
  className={cn(
    'inline-flex items-center rounded-md px-4 py-2 font-medium',
    variant === 'primary' && 'bg-brand text-white',
    disabled && 'opacity-50 pointer-events-none',
    className,                         // caller override wins via twMerge
  )}
/>
```

Without `tailwind-merge`, a caller's `px-6` and the base `px-4` both land and specificity/order decides unpredictably. `cn()` resolves the conflict deterministically.

## Component extraction — components over `@apply`

When a utility cluster repeats, extract a **component** (React/Vue/etc.), not a CSS class.

- **Prefer** a real component with a typed variant API. Use **`cva`** (class-variance-authority) or `tailwind-variants` for multi-variant components:

```ts
import { cva } from 'class-variance-authority';
const button = cva('inline-flex rounded-md font-medium', {
  variants: {
    intent: { primary: 'bg-brand text-white', ghost: 'bg-transparent' },
    size:   { sm: 'px-3 py-1 text-sm', md: 'px-4 py-2' },
  },
  defaultVariants: { intent: 'primary', size: 'md' },
});
```

- **`@apply` sparingly.** It recreates the abstraction problems Tailwind avoids (indirection, specificity, dead CSS) and is easy to overuse. Reasonable uses: styling markup you don't control (third-party HTML, prose/`@tailwind` typography), or a tiny base primitive. Not a substitute for components.

## Arbitrary values — escape hatch, not habit

`w-[347px]`, `bg-[#1da1f2]`, `grid-cols-[1fr_2fr]` bypass the design system. Use them for genuine one-offs; if a value repeats, **add it to `@theme`/config** instead so it becomes a token.

## Dark mode

```css
/* v4: selector strategy (class/attribute toggle) */
@custom-variant dark (&:where(.dark, .dark *));
```

```html
<div class="bg-white text-black dark:bg-neutral-900 dark:text-white">
```

- Prefer driving colours through **semantic theme tokens** so `dark:` variants stay few — define light/dark token values once (→ `refs/theming.md`) rather than sprinkling `dark:` on every element.
- Toggle the `dark` class before first paint to avoid a flash (SSR/inline script).

## Responsive & state

- Mobile-first: unprefixed = base, `md:`/`lg:` add up. `md:flex` means "flex at ≥ md", matching the SKILL's mobile-first rule.
- **Container queries** are first-class: `@container` + `@md:` variants (`@container/sidebar`) for component-level responsiveness → `refs/layout.md`.
- Group/peer state: `group-hover:`, `peer-checked:`, `has-[...]:`, `data-[state=open]:` — prefer these declarative variants over JS class toggling.
- Use `focus-visible:` (not bare `focus:`) for rings, and gate motion with `motion-safe:` / `motion-reduce:` → `refs/accessibility.md`.

## Plugins & prose

- `@tailwindcss/typography` (`prose`) for rendered markdown/CMS HTML you can't put utilities on.
- `@tailwindcss/forms` for sane form-control base styles.
- Author custom utilities with `@utility` (v4) or a plugin (v3) rather than random global CSS.

## Anti-Patterns

- Dynamic class names built by string interpolation (`` `bg-${c}-500` ``) → purged, missing in prod.
- Incomplete v3 `content` globs → classes silently dropped.
- `@apply` used to rebuild component abstractions Tailwind exists to avoid.
- Dynamic/overridable classes merged without `tailwind-merge` → nondeterministic conflicts.
- Arbitrary values (`w-[347px]`) for values that recur and should be tokens.
- `dark:` sprinkled per-element instead of semantic light/dark tokens.
- Bare `focus:` rings (show for mouse users) instead of `focus-visible:`.
- Fighting a design decision with `!` important utilities (`!bg-red-500`) instead of fixing token/order.
- Mixing v3 JS-config and v4 CSS-config paradigms in one project.
