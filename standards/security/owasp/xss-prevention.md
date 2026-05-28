---
description: Prevent XSS via context-aware encoding, safe DOM APIs, DOMPurify sanitization, CSP/Trusted Types, DOM sink hardening, and filter bypass defense
alwaysApply: false
---

# XSS Prevention

No single technique solves XSS — apply the right combination for each context. Blacklists and input filters are bypassable via mixed encoding, whitespace manipulation, malformed tags, and obfuscation (`String.fromCharCode`, etc.); defense requires context-aware encoding and safe APIs.

## NEVER
- Trust any data source — internal APIs or databases can carry malicious data
- Use `innerHTML`, `outerHTML`, `dangerouslySetInnerHTML`, `[innerHTML]`, `v-html`, or `document.write()` without sanitizing first
- Inject user data into `onclick` or other event handler attributes
- Rely on client-side validation alone — always re-validate server-side
- Allow `javascript:` URLs — validate protocol before inserting URLs
- Inject user data into JavaScript context dynamically or use unescaped template literals to build HTML (`` `<div>${userInput}</div>` ``)
- Pass user input to `eval()`, `new Function()`, `setTimeout(string)`, or `setInterval(string)`
- Assign untrusted input to `location.href` or event handler properties without validation
- Handle `postMessage` events without origin validation
- Roll your own sanitization logic — use established libraries

## ALWAYS
- Apply context-aware output encoding at the point of output (HTML body, attribute, JS, CSS, URL)
- Sanitize HTML with DOMPurify using a strict allowlist before any `innerHTML`-equivalent insertion
- Use `element.textContent` for plain text; use safe DOM APIs (`setAttribute`) where rich HTML is not needed
- Validate all input server-side against strict allow-lists with length limits
- Implement CSP with `script-src 'nonce-{random}' 'strict-dynamic'` and `require-trusted-types-for 'script'`
- Set session cookies `HttpOnly; Secure; SameSite=Strict` to limit theft impact
- Validate URL inputs against an allowlist pattern before `location.href` assignment
- Validate `postMessage` origins against an explicit allowlist
- Use Trusted Types policy wrapping DOMPurify for all `innerHTML` assignments
- Keep frameworks and sanitization libraries updated

## Context-Aware Encoding

| Context | Safe approach | Encoding function |
| ------- | ------------- | ----------------- |
| HTML body/content | `element.textContent`; DOMPurify for rich content | `encodeForHTML` |
| HTML attribute | Quote all attributes; HTML-encode values | `encodeForHTMLAttribute` |
| JavaScript | Avoid dynamic JS generation; use data attributes + event listeners | `encodeForJavaScript` |
| CSS | Validate against strict allow-list before insertion | `encodeForCSS` |
| URL | Encode with `encodeURIComponent`; validate protocol (reject `javascript:`) | `encodeForURL` |
| ARIA / SVG | Allow-list values; sanitize SVG with DOMPurify SVG profile | — |

## Framework Escape Hatches
- **React** `dangerouslySetInnerHTML` → sanitize with DOMPurify first
- **Angular** `[innerHTML]` binding → sanitize with DOMPurify first
- **Vue** `v-html` directive → sanitize with DOMPurify first

## DOMPurify Configuration

```javascript
const cleanHtml = DOMPurify.sanitize(userHtml, {
  ALLOWED_TAGS: ['b', 'i', 'p', 'a', 'ul', 'li'],
  ALLOWED_ATTR: ['href', 'target', 'rel'],
  ALLOW_DATA_ATTR: false
});
```

## DOM Sinks

DOM-based XSS occurs when untrusted input flows to a dangerous sink client-side. Audit every sink on the list below.

### Sink Risk Reference

| Sink | Risk | Safe pattern |
| ---- | ---- | ------------ |
| `innerHTML` / `outerHTML` | High | `DOMPurify.sanitize()` or `textContent` |
| `document.write()` | High | Avoid entirely |
| `eval()` / `new Function()` | Critical | Remove; use data-only logic |
| `setTimeout(str)` / `setInterval(str)` | Critical | Pass a function reference, not a string |
| `location.href` | Medium | Validate against allowlist + `encodeURI` |
| `element.onclick = str` | Medium | `addEventListener` with function reference |

### postMessage Origin Validation

```javascript
window.addEventListener('message', (event) => {
  const ALLOWED_ORIGINS = ['https://trusted.example.com'];
  if (!ALLOWED_ORIGINS.includes(event.origin)) return;
  // safe to process event.data
});
```

## Trusted Types

```javascript
const policy = trustedTypes.createPolicy('dom-xss-prevention', {
  createHTML: (s) => DOMPurify.sanitize(s, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p', 'br'], ALLOWED_ATTR: []
  }),
  createScript: () => { throw new Error('Disallowed'); }
});
element.innerHTML = policy.createHTML(userInput);
```

## Safe API Substitutes

```javascript
// NEVER                             // ALWAYS
eval(input)                       // JSON.parse(input)
element.innerHTML = input         // element.textContent = input
document.write(input)             // DOM construction via createElement
setTimeout(input, 100)            // setTimeout(fn, 100) — fn is not a string
```

## Sanitization Libraries

| Platform | Library |
| -------- | ------- |
| JavaScript/DOM | DOMPurify (configure `ALLOWED_TAGS`, `ALLOWED_ATTR`) |
| Java | OWASP Java Encoder (`Encode.forHtml`, `Encode.forJavaScript`, …) |
| PHP | HTMLPurifier |

## Checklist
- [ ] All output context-encoded at point of insertion (HTML body, attribute, JS, URL, CSS)
- [ ] `innerHTML`, `outerHTML`, and framework HTML bindings (React, Vue, Angular) only used with DOMPurify sanitization
- [ ] No `eval()`, `new Function()`, or string-form `setTimeout`/`setInterval` with user input
- [ ] No inline event handlers (`onclick`) carrying server-rendered user data
- [ ] `location.href` set only after allowlist URL validation; no `javascript:` URLs permitted
- [ ] `postMessage` handlers validate `event.origin` against explicit allowlist
- [ ] Server-side input validation (allow-lists, length limits) in place
- [ ] CSP with nonce-based `script-src` and `require-trusted-types-for 'script'` deployed
- [ ] Session cookies have `HttpOnly; Secure; SameSite=Strict`
- [ ] Established sanitization library used (DOMPurify, Java Encoder, HTMLPurifier); no custom filter logic
- [ ] Frameworks and sanitization libraries kept up to date
