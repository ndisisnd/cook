# Architecture

Use this ref when structuring a stylesheet system: choosing a methodology, setting up cascade layers, scoping styles, controlling specificity at scale, or organizing files.

## Cascade Layers (`@layer`)

Declare layer order **once**, up front. Later layers beat earlier layers **regardless of specificity** — this is how you tame the cascade by intent instead of by selector weight.

```css
@layer reset, base, tokens, components, utilities;

@layer reset      { *, *::before, *::after { box-sizing: border-box; margin: 0; } }
@layer base       { body { font: 1rem/1.5 system-ui; } a { color: var(--color-link); } }
@layer components { .card { padding: var(--space-4); background: var(--card-bg); } }
@layer utilities  { .mt-0 { margin-block-start: 0; } }
```

- A single-class `.card` in `components` still loses to a `.mt-0` utility because `utilities` is declared last. No `!important` needed.
- **Unlayered styles beat all layered styles.** Keep almost everything layered; leave only deliberate overrides unlayered.
- Isolate **third-party CSS in its own early layer** so your own styles win without `!important`:

```css
@layer reset, third-party, base, components, utilities;
@import "vendor-widget.css" layer(third-party);
```

## Methodology — pick one

| Approach | When | Cost |
|---|---|---|
| **Utility-first (Tailwind)** | Product UI, design-system-driven, fast iteration | Verbose markup; needs `cn()` discipline → `refs/tailwind.md` |
| **CSS Modules** | Component frameworks (React/Next/Vue); automatic scoping | Build step; `composes` for sharing |
| **BEM** | Plain CSS, server-rendered, no build scoping | Naming discipline; verbose class names |
| **ITCSS layering** | Large hand-authored codebases | Organizational overhead; pairs well with `@layer` |

Do not mix ad-hoc. A codebase may use CSS Modules *and* Tailwind deliberately, but every author must know which owns what.

### BEM

```css
.card {}                 /* block */
.card__title {}          /* element */
.card--featured {}       /* modifier */
.card__title--muted {}   /* element modifier */
```

Keeps specificity flat (every selector is one class) and communicates structure in the name.

### ITCSS (inverted-triangle layering)

Order stylesheets from generic/low-specificity to explicit/high-specificity — **settings → tools → generic → elements → objects → components → utilities**. Maps cleanly onto `@layer`.

## Scoping

- **CSS Modules** — `styles.module.css`; the bundler rewrites `.card` to a hashed local name (`.card_a1b2c`). Zero leakage, zero naming ceremony. Use `composes: base from './base.module.css'` to share.
- **`@scope`** — native scoping without a build step; styles apply only within the subtree and stop at the lower bound:

```css
@scope (.card) to (.card__body) {
  :scope { border: 1px solid var(--border); }
  img    { aspect-ratio: 16 / 9; }   /* scoped; won't leak below .card__body */
}
```

- **`:where()` for zero-specificity resets** — wrap base/reset selectors so authors can always override:

```css
:where(ul, ol) { margin: 0; padding: 0; }   /* specificity 0,0,0 — trivially overridable */
```

## Specificity strategy

- Target **classes**; avoid IDs and element+class over-qualification (`div.card` → `.card`).
- Keep selector depth **≤ 3**. Deep descendant chains (`.a .b .c .d`) are brittle and hard to override.
- Use `:is()` / `:where()` to flatten grouped selectors. Remember: `:is()` takes the **highest** specificity of its arguments; `:where()` is always **zero**.
- Reach for specificity control (layers, `:where()`) before reaching for `!important`.

## File & folder organization

```
styles/
├── reset.css            # or a vendored reset (layer: reset)
├── tokens/
│   ├── primitives.css   # raw scale: --color-blue-500, --space-4
│   └── semantic.css     # --color-danger, --surface-raised
├── base.css             # element defaults (layer: base)
├── components/          # one file per component (or colocated modules)
└── utilities.css        # generated or hand-authored (layer: utilities)
```

- Define the `@layer` order in a single entry file that `@import`s the rest in layer order.
- Colocate component styles with components in framework projects (`Button.module.css` next to `Button.tsx`).
- One token source of truth; never redefine `--space-4` in two places.

## Anti-Patterns

- Relying on **source order** across files instead of explicit `@layer` order.
- Mixing methodologies ad-hoc so no one knows what owns a given element.
- Deep descendant chains and over-qualified selectors that force `!important` later.
- Third-party CSS imported unlayered, then fought with `!important`.
- Redefining the same token in multiple files.
- Reset/base rules authored at normal specificity so component authors must out-specify them.
