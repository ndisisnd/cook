# Performance

Use this ref when CSS is causing jank, slow paints, layout thrash, or a heavy bundle — or when adding animation, large lists, or web fonts.

## Animate on the compositor only

The browser can animate **`transform`** and **`opacity`** on the compositor thread — no layout, no paint, 60fps. Everything else is expensive.

```css
/* GOOD — compositor-only, cheap */
.slide { transition: transform 200ms ease; }
.slide:hover { transform: translateX(8px); }

/* BAD — triggers layout every frame */
.slide { transition: left 200ms ease; }
.slide:hover { left: 8px; }
```

Never animate `width`, `height`, `top`/`left`/`right`/`bottom`, `margin`, `padding` — each frame reflows the page. Reach for `transform: scale()` / `translate()` instead.

- Never `transition: all` — it animates every changed property (including expensive/unexpected ones) and defeats the point. Name the properties.

## `will-change` — sparingly

`will-change` promotes an element to its own layer *ahead* of an animation. It is a scalpel, not a default.

- Apply it just before the animation (e.g. on `:hover`/via JS) and remove it after — a permanently-promoted element wastes GPU memory.
- Never blanket `will-change: transform` on many elements; too many layers is slower than none.

## Containment — `contain` & `content-visibility`

Tell the browser a subtree's layout/paint is independent so it can skip work.

```css
.card { contain: layout paint; }              /* card internals can't affect outside layout */

.below-fold-section {
  content-visibility: auto;                    /* skip rendering off-screen content entirely */
  contain-intrinsic-size: auto 500px;          /* reserve space so the scrollbar is stable */
}
```

`content-visibility: auto` is one of the highest-leverage wins for long pages — off-screen sections aren't styled/laid out/painted until they approach the viewport. Always pair with `contain-intrinsic-size` to avoid scrollbar jumps.

## Selector cost

Modern engines are fast; selector performance rarely dominates. But at scale:

- Avoid the **universal selector in expensive contexts** and huge descendant/`*` combinations.
- Avoid deep descendant chains re-evaluated on every DOM change.
- The real selector cost is usually **quantity** (tens of thousands of rules) and unused CSS, not individual selector shape. Ship less CSS.

## Critical CSS & delivery

- **Inline critical (above-the-fold) CSS** in `<head>`; load the rest asynchronously so first paint isn't blocked by the full stylesheet.
- CSS is **render-blocking** by default — keep the critical path small.
- Scope non-critical stylesheets with `media` (`media="print"`, `media="(min-width: 60rem)"`) so the browser deprioritizes them.
- Split by route/component (CSS Modules, code splitting) so a page ships only what it uses. Purge unused utility CSS → `refs/tailwind.md`, `refs/tooling.md`.

## Web fonts

Fonts are a top cause of CLS and slow text render.

```css
/* 1. The real web font — no size-adjust here (100% would be a no-op). */
@font-face {
  font-family: 'Inter';
  src: url('/fonts/inter.woff2') format('woff2');
  font-display: swap;          /* show fallback immediately, swap when ready */
}

/* 2. A fallback face built from a local system font, with metrics tuned to
      match Inter — THIS is what kills the swap shift. */
@font-face {
  font-family: 'Inter Fallback';
  src: local('Arial');
  size-adjust: 107%;           /* per-font: make the fallback occupy the same space */
  ascent-override: 90%;
  descent-override: 22%;
}

/* 3. Order the stack so the tuned fallback renders until Inter loads. */
:root { --font-sans: 'Inter', 'Inter Fallback', sans-serif; }
```

- `font-display: swap` (or `optional` for the least layout shift) — never let text be invisible during load.
- **Preload** the critical font (`<link rel="preload" as="font" crossorigin>`) and self-host `woff2`.
- The swap-shift fix is a **separate fallback `@font-face`** whose `size-adjust`/`ascent-override`/`descent-override` are tuned to the web font — not `size-adjust` on the web font itself. This is exactly what `next/font` and Fontaine generate automatically (→ `standards/nextjs/refs/styling-and-optimization.md`).
- Subset fonts to the glyphs you use.

## Avoiding layout thrash

- Reserve space for async content with `aspect-ratio` / `min-height` so images and embeds don't shift layout (CLS).
- Batch DOM reads/writes in JS; reading `offsetWidth` after a style write forces synchronous layout (this is JS-side but CSS-adjacent).
- Prefer `transform`-based reveal animations over height/margin animations for accordions (or animate to `height: auto` via modern `interpolate-size: allow-keywords` / `calc-size()` where supported, with a reduced-motion guard).

## Anti-Patterns

- Animating `width`/`height`/`top`/`left`/`margin`; `transition: all`.
- Permanent / blanket `will-change`.
- No `content-visibility`/`contain` on long, independent sections.
- Shipping one giant stylesheet with no critical-path split; unused CSS not purged.
- Web fonts without `font-display`, unpreloaded, unsubset — invisible text and CLS.
- Async content (images/ads/embeds) with no reserved space → cumulative layout shift.
