# Accessibility

Use this ref for the CSS side of accessibility: focus indication, motion safety, contrast and high-contrast modes, target sizes, and hiding content correctly. CSS cannot fix bad markup — pair with the framework shelf for semantics/ARIA.

## Focus indication

Keyboard users must always see where focus is.

```css
/* Scope the ring to keyboard focus; pointer users don't see it */
:focus-visible {
  outline: 2px solid var(--color-focus);
  outline-offset: 2px;
}
/* Only remove the default outline when you provide :focus-visible */
:focus:not(:focus-visible) { outline: none; }
```

- **Never** ship `outline: none` (or `outline: 0`) without an equal-or-better replacement.
- `outline` (not `border`/`box-shadow` alone) respects `outline-offset` and doesn't shift layout; if you use `box-shadow` for the ring, keep an `outline` fallback for forced-colors mode (see below).
- Ensure the focus indicator meets **3:1 contrast** against adjacent colours (WCAG 1.4.11 Non-text Contrast, AA). A ≥2px-thick / minimum-area indicator is the stronger target (WCAG 2.4.13 Focus Appearance, AAA) — treat it as best practice, not an AA gate.

## Motion safety

Honour `prefers-reduced-motion` for anything non-essential (parallax, autoplay, large transitions, spinners that could trigger vestibular issues).

```css
/* Opt-in pattern: motion only when the user hasn't asked to reduce it */
@media (prefers-reduced-motion: no-preference) {
  .reveal { transition: transform 300ms ease, opacity 300ms ease; }
}

/* Or a global safety net */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

Reduce, don't necessarily remove — a subtle opacity fade is usually fine; a spinning/zooming/parallax motion is not. Keep functional feedback (focus, state change) perceivable.

## Contrast & high-contrast modes

- Body text ≥ **4.5:1**, large text (≥ 24px, or 18.7px bold) and UI/graphics ≥ **3:1** against their background.
- Don't rely on `opacity` for "muted" text without checking the resulting effective contrast.

### `forced-colors` (Windows High Contrast)

In forced-colors mode the OS replaces your palette with a user palette. Design for it rather than fighting it:

```css
@media (forced-colors: active) {
  .button { border: 1px solid ButtonText; }        /* use system colour keywords */
  .brand-swatch { forced-color-adjust: none; }     /* opt OUT only where colour is the content (a swatch) */
}
```

- Use **system colour keywords** (`ButtonText`, `Canvas`, `LinkText`, `Highlight`) inside `forced-colors`.
- `background-image`/`box-shadow`-based UI (e.g. icon-only buttons, custom checkboxes) can vanish in forced colors — provide a `border`/`outline` or an actual glyph so state stays visible.
- Only use `forced-color-adjust: none` when you *must* preserve specific colours (e.g. a colour picker swatch), and then restore visibility manually.

### `prefers-contrast`

```css
@media (prefers-contrast: more) { :root { --border: black; --text: black; } }
```

## Target size

Interactive controls should be at least **24×24px** (WCAG 2.5.8 AA); **44×44px** is the stronger AAA/mobile target.

```css
.icon-button { min-inline-size: 44px; min-block-size: 44px; }
/* Or expand the hit area without changing visual size */
.small-link { position: relative; }
.small-link::after { content: ''; position: absolute; inset: -8px; }
```

## Hiding content correctly

Different intents need different techniques:

```css
/* Visually hidden but read by screen readers (skip links, labels) */
.sr-only {
  position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
  overflow: hidden; clip-path: inset(50%); white-space: nowrap; border: 0;
}

/* Reveal an sr-only element on focus (skip-to-content link) */
.sr-only:focus-visible { position: static; width: auto; height: auto; clip-path: none; }
```

- `display: none` / `visibility: hidden` / `hidden` attribute → hidden from **everyone** (including AT). Use for genuinely inactive content.
- `.sr-only` (above) → hidden **visually only**, still announced. Use for labels, skip links, live-region text.
- `aria-hidden="true"` → hidden from **AT only**, still visible. Use for decorative icons; CSS can't set it, so coordinate with markup.

## Respecting user preferences

Also design around: `prefers-reduced-transparency`, `prefers-reduced-data`, and `inverted-colors`. Never override the user's root font-size or block zoom.

## Anti-Patterns

- `outline: none` with no `:focus-visible` replacement.
- Motion/animation with no `prefers-reduced-motion` handling.
- Icon-only buttons/custom form controls that disappear in `forced-colors` (image/shadow-only, no border/glyph).
- `display: none` used where an `.sr-only` label was intended (silences screen readers).
- Meaning conveyed by colour alone (status, error, required).
- Focus ring with insufficient contrast/thickness, or one that shifts layout (using `border` toggling instead of `outline`).
- Target smaller than 24px with no expanded hit area.
