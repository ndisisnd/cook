# Theming

Use this ref when defining design tokens, building light/dark themes, choosing a colour model, or working with custom properties (`--var`), `@property`, or modern colour functions.

## Custom properties vs preprocessor variables

| | Custom property (`--x`) | Sass/Less variable (`$x`) |
|---|---|---|
| Resolved | **Runtime**, cascades, inheritable | Compile-time, static |
| Themeable / re-scopable | Yes (per selector, media query, JS) | No |
| Use for | Anything that varies by theme, state, breakpoint, JS | Build-time constants, loop inputs, math |

Default to custom properties for theming. Reach for preprocessor variables only for compile-time values (Sass maps, loop bounds).

## Token layering

Three tiers. Components consume **semantic** tokens, never raw primitives — so a rebrand touches one layer.

```css
:root {
  /* 1. Primitives — the raw scale, no meaning */
  --blue-500: oklch(0.55 0.2 255);
  --gray-100: oklch(0.97 0 0);
  --gray-900: oklch(0.2 0 0);
  --space-4: 1rem;

  /* 2. Semantic — meaning, maps to primitives */
  --color-accent: var(--blue-500);
  --surface: var(--gray-100);
  --text: var(--gray-900);

  /* 3. Component — optional, maps to semantic */
  --button-bg: var(--color-accent);
}
```

Rules: primitives have no meaning in their name; components never reference a primitive directly; one source of truth per token.

## Dark mode

### `color-scheme` + `light-dark()`

The modern path. Declare which schemes an element supports, then let `light-dark()` pick per scheme — no media query, no duplicated selectors.

```css
:root {
  color-scheme: light dark;               /* also styles form controls/scrollbars */
  --surface: light-dark(oklch(0.98 0 0), oklch(0.2 0 0));
  --text:    light-dark(oklch(0.2 0 0),  oklch(0.95 0 0));
}
```

### Media-query fallback / manual toggle

For a user-selectable theme (not just OS preference), scope tokens by attribute and honour the system default:

```css
:root { --surface: oklch(0.98 0 0); }
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) { --surface: oklch(0.2 0 0); }
}
:root[data-theme="dark"] { --surface: oklch(0.2 0 0); }
```

- Set `color-scheme` to match so native UI (inputs, scrollbars) follows the theme.
- Redefine **semantic tokens** for dark mode, not every component — the token layer does the work.
- Avoid a flash of wrong theme: set the theme attribute before first paint (inline script / SSR), don't wait for hydration.

## Modern colour

- Prefer **`oklch()`** (perceptually uniform: equal lightness steps look equal; predictable for generating scales and accessible contrast). `hsl()` is fine but non-uniform.
- **`color-mix()`** for tints/shades/state variants without new tokens:

```css
--button-bg-hover: color-mix(in oklch, var(--button-bg), black 12%);
--overlay: color-mix(in oklch, var(--surface) 60%, transparent);
```

- **Relative colour syntax** to derive from an existing colour:

```css
--accent-muted: oklch(from var(--color-accent) l c h / 0.5);
```

- Use modern space-separated / slash-alpha syntax: `rgb(0 0 0 / 0.5)`, not legacy `rgba(0,0,0,0.5)`.

## `@property` — typed custom properties

Register a custom property so it can **animate**, has a type, and has a guaranteed fallback. Un-registered custom properties are treated as strings and cannot be transitioned.

```css
@property --gradient-angle {
  syntax: '<angle>';
  inherits: false;
  initial-value: 0deg;
}
@keyframes spin { to { --gradient-angle: 360deg; } }
.ring {
  background: conic-gradient(from var(--gradient-angle), var(--color-accent), transparent);
  animation: spin 1s linear infinite;   /* animates smoothly ONLY because --gradient-angle is registered */
}
```

## Fallbacks & guards

- Provide a fallback in `var()` for properties that may be undefined: `color: var(--text, black)`.
- Feature-gate with `@supports` when using newer functions on a broad browser matrix:

```css
@supports (color: light-dark(white, black)) { /* modern path */ }
```

## Anti-Patterns

- Components referencing primitive tokens (`--blue-500`) directly instead of semantic ones — every rebrand becomes a find-and-replace.
- Duplicating a full dark-mode stylesheet instead of redefining semantic tokens.
- `prefers-color-scheme` handled without also setting `color-scheme` — native controls stay light-on-dark.
- Legacy `rgba()`/`hsla()` in new code; hard-coded hex scattered outside the token layer.
- Animating an unregistered custom property (silently does nothing — needs `@property`).
- Theme applied after hydration, causing a flash of the wrong theme.
