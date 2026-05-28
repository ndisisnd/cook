---
description: Prevent XSS via context-aware output encoding, input validation, and defense-in-depth controls
alwaysApply: false
---

# Cross-Site Scripting (XSS) Prevention

No single technique solves XSS — apply the right combination for each context.

## NEVER
- Trust any data source — internal APIs or databases can carry malicious data
- Use `innerHTML`, `dangerouslySetInnerHTML`, `[innerHTML]`, or `v-html` without sanitizing first
- Inject user data into `onclick` or other event handler attributes
- Rely on client-side validation alone — always re-validate server-side
- Allow `javascript:` URLs — validate protocol before inserting URLs
- Inject user data into JavaScript context dynamically

## ALWAYS
- Apply context-aware output encoding at the point of output (HTML body, attribute, JS, CSS, URL)
- Sanitize HTML with DOMPurify using a strict allowlist before any `innerHTML`-equivalent insertion
- Validate all input server-side against strict allow-lists with length limits
- Use safe DOM APIs (`textContent`, `setAttribute`) instead of `innerHTML` where rich HTML is not needed
- Implement CSP with `script-src 'nonce-{random}' 'strict-dynamic'` as defense-in-depth
- Set session cookies `HttpOnly; Secure; SameSite=Strict` to limit theft impact
- Keep frameworks and sanitization libraries updated

## Context-Specific Encoding

| Context | Safe Approach |
|---------|---------------|
| HTML body | `element.textContent`; DOMPurify for rich content |
| HTML attribute | Quote all attributes; HTML-encode values |
| JavaScript | Avoid dynamic JS generation; use data attributes + event listeners |
| CSS | Validate against strict allow-list before insertion |
| URL | Encode URL; validate protocol (reject `javascript:`) |
| ARIA / SVG | Allow-list values; sanitize SVG with DOMPurify SVG profile |

## Framework Escape Hatches
- **React** `dangerouslySetInnerHTML` → sanitize with DOMPurify first
- **Angular** `[innerHTML]` binding → sanitize with DOMPurify first
- **Vue** `v-html` directive → sanitize with DOMPurify first

## Sanitization

```javascript
const cleanHtml = DOMPurify.sanitize(userHtml, {
  ALLOWED_TAGS: ['b', 'i', 'p', 'a', 'ul', 'li'],
  ALLOWED_ATTR: ['href', 'target', 'rel'],
  ALLOW_DATA_ATTR: false
});
```

## Trusted Types (DOM XSS)

```javascript
const policy = trustedTypes.createPolicy('myPolicy', {
  createHTML: (s) => DOMPurify.sanitize(s),
  createScript: () => { throw new Error('Disallowed'); }
});
element.innerHTML = policy.createHTML(userInput);
```

## Checklist
- [ ] All output HTML-encoded or context-encoded at point of insertion
- [ ] `innerHTML` / framework equivalents sanitized with DOMPurify + allowlist
- [ ] Server-side input validation in place (allow-lists, length limits)
- [ ] CSP header with nonce-based `script-src` deployed
- [ ] Session cookies have `HttpOnly; Secure; SameSite=Strict`
- [ ] No `javascript:` URLs permitted
- [ ] Dependencies and sanitization libraries kept up to date
