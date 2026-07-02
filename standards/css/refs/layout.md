# Layout

Use this ref when building layout: choosing Flexbox vs Grid, using container queries, sizing intrinsically, applying logical properties, or building fluid/responsive behaviour.

## Flexbox vs Grid

| Use | For |
|---|---|
| **Flexbox** | One-dimensional flow — a row of buttons, a nav bar, content that wraps; distribution along a single axis |
| **Grid** | Two-dimensional layout — page templates, card galleries, anything where rows *and* columns align |

Default to Grid for structure, Flexbox for content flow. Neither replaces the other; most pages use both.

```css
/* Intrinsic responsive grid — no media queries needed */
.gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(16rem, 100%), 1fr));
  gap: var(--space-4);
}
```

`min(16rem, 100%)` prevents the track from overflowing its container on very narrow screens — a common `minmax` bug.

## The flex-child overflow trap

A flex/grid item's default `min-width: auto` refuses to shrink below its content's intrinsic size — long text or a `<pre>` blows the layout out horizontally.

```css
.flex-child { min-width: 0; }   /* allow shrinking; pair with overflow handling on the content */
```

Use `min-height: 0` for the same problem on the block axis (e.g. a scrollable panel inside a column flex container).

## `gap` over margins

Use `gap` for spacing between flex/grid children — no first/last-child margin hacks, no collapsing-margin surprises.

```css
.stack { display: flex; flex-direction: column; gap: var(--space-3); }
```

## Container Queries

Prefer container queries for **component** responsiveness — a card should respond to the space it's in, not the viewport. This makes components portable across sidebars, modals, and main content.

```css
.card-wrapper { container-type: inline-size; container-name: card; }

@container card (min-width: 24rem) {
  .card { grid-template-columns: 8rem 1fr; }
}
```

- `container-type: inline-size` queries width; `size` queries both axes (needs a definite size).
- Use **container query units** (`cqi`, `cqw`, `cqb`) to size relative to the container.
- Reserve viewport media queries for genuinely viewport-level concerns (page shell, global type scale).

## Logical Properties

Author with logical properties so layouts internationalize (RTL, vertical writing modes) with zero extra work.

| Physical | Logical |
|---|---|
| `margin-left` / `margin-right` | `margin-inline-start` / `margin-inline-end` |
| `margin-top` / `margin-bottom` | `margin-block-start` / `margin-block-end` |
| `width` / `height` | `inline-size` / `block-size` |
| `left`/`top` (inset) | `inset-inline-start` / `inset-block-start` |
| `text-align: left` | `text-align: start` |
| `border-top-left-radius` | `border-start-start-radius` |

Shorthands: `margin-inline: auto`, `padding-block: var(--space-2)`, `inset: 0`.

## Fluid Sizing — `min()` / `max()` / `clamp()`

Replace breakpoint-stepped values with continuous fluid values.

```css
/* Fluid type: min 1rem, scales with viewport, capped at 1.5rem */
h1 { font-size: clamp(1.5rem, 1rem + 2vw, 2.5rem); }

/* Fluid gutter with a floor and ceiling */
.section { padding-inline: clamp(1rem, 5vw, 4rem); }

/* Responsive width without a media query */
.panel { width: min(40rem, 100%); }
```

Always include a viewport-relative term in a `clamp()` middle argument (e.g. `1rem + 2vw`) so it actually scales; and keep a non-`vw`-only floor so it never collapses below a readable size at small viewports (WCAG zoom).

## Viewport units — prefer the dynamic/small variants

`vh`/`vw` predate mobile browser chrome (the address bar that grows and shrinks). On mobile, `100vh` is the *largest* viewport, so a `height: 100vh` element gets clipped behind the toolbar. Reach for the newer units:

- **`svh`/`svw`** (small): the viewport with browser UI *shown* — the safe default for "fill the screen without clipping".
- **`lvh`** (large): UI hidden. **`dvh`** (dynamic): resizes live as the chrome shows/hides — smoothest, but it reflows on scroll, so avoid it on hot paths.

```css
.hero { min-height: 100svh; }   /* never clipped behind mobile chrome */
```

Default to `svh` for full-height sections; use `dvh` only where the live resize is worth the reflow.

## `aspect-ratio`

Reserve space and avoid layout shift without padding-hack wrappers.

```css
.thumb { aspect-ratio: 16 / 9; width: 100%; object-fit: cover; }
.avatar { aspect-ratio: 1; }
```

## Subgrid

Align nested content to a parent grid's tracks — e.g. card titles and footers lining up across a gallery regardless of content length.

```css
.gallery { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-4); }
.card    { display: grid; grid-row: span 3; grid-template-rows: subgrid; }
```

## Breakpoint strategy

- **Mobile-first**: base styles are the smallest layout; add complexity with `min-width` queries.
- Choose breakpoints where **the content breaks**, not at device widths (`375px`, `768px` are guesses; test the actual layout).
- Prefer `rem`-based breakpoints (`@media (min-width: 48rem)`) so they respond to user font-size.
- Fewer breakpoints is better — fluid sizing (`clamp`) and intrinsic grids (`auto-fill`/`minmax`) eliminate most of them.

## Anti-Patterns

- `float` / absolute positioning / table hacks for structural layout.
- `minmax(16rem, 1fr)` without `min(…, 100%)` — overflows on narrow screens.
- Missing `min-width: 0` on flex children holding long content.
- First/last-child margin hacks instead of `gap`.
- Viewport media queries for component-level responsiveness that a container query fits better.
- Physical properties in new code where logical ones internationalize for free.
- `clamp()` with no viewport term (never scales) or no readable floor (breaks zoom).
- Fixed pixel heights on containers that hold variable content.
