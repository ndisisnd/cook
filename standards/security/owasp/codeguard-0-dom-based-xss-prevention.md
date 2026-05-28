---
description: Prevent DOM-based XSS by securing sinks, encoding by context, and enforcing CSP/Trusted Types
alwaysApply: false
---

# DOM-Based XSS Prevention

## NEVER
- Assign untrusted input to `innerHTML`, `outerHTML`, `document.write()`
- Pass user input to `eval()`, `new Function()`, `setTimeout(string)`, `setInterval(string)`
- Assign untrusted input to `location.href` or event handler properties without validation
- Use unescaped template literals to build HTML: `` `<div>${userInput}</div>` ``
- Handle `postMessage` events without origin validation

## ALWAYS
- Use `element.textContent` for plain text; sanitize with DOMPurify before any `innerHTML` assignment
- Apply context-aware encoding: HTML-encode for HTML context, `encodeURIComponent` for URLs, JS-encode for JS context
- Validate URL inputs against an allowlist pattern before `location.href` assignment
- Validate `postMessage` origins against an explicit allowlist
- Implement strict CSP: `script-src 'self' 'nonce-{random}'; object-src 'none'; base-uri 'self'; require-trusted-types-for 'script'`
- Use Trusted Types policy wrapping DOMPurify for all `innerHTML` assignments
- Validate all user input server-side before it reaches the DOM

## Sink Risk Reference

| Sink | Risk | Safe pattern |
|------|------|-------------|
| `innerHTML` / `outerHTML` | High | `DOMPurify.sanitize()` or `textContent` |
| `document.write()` | High | Avoid entirely |
| `eval()` / `new Function()` | Critical | Remove; use data-only logic |
| `setTimeout(str)` | Critical | `setTimeout(() => fn(data), ms)` |
| `location.href` | Medium | Validate against allowlist + `encodeURI` |
| `element.onclick = str` | Medium | `addEventListener` with function ref |

## Trusted Types Setup
```javascript
const policy = trustedTypes.createPolicy('dom-xss-prevention', {
  createHTML: (s) => DOMPurify.sanitize(s, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p', 'br'], ALLOWED_ATTR: []
  })
});
element.innerHTML = policy.createHTML(userInput);
```

## Checklist
- [ ] No `innerHTML`/`outerHTML` assignment without DOMPurify sanitization
- [ ] No `eval()`, `new Function()`, or string-form `setTimeout`/`setInterval`
- [ ] `location.href` only set after allowlist URL validation
- [ ] `postMessage` handlers validate `event.origin` against explicit allowlist
- [ ] Strict CSP with nonce deployed; `require-trusted-types-for 'script'` enabled
- [ ] Context-aware encoding applied (HTML, JS, URL contexts)
- [ ] Framework HTML rendering (React `dangerouslySetInnerHTML`, Vue `v-html`) uses DOMPurify
