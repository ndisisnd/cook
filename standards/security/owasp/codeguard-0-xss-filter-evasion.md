---
description: Defeat XSS filter-evasion by applying context-aware output encoding and avoiding dangerous DOM APIs
alwaysApply: false
---

# XSS Filter Evasion Prevention

Blacklists and input filters are bypassable via mixed encoding, whitespace manipulation, malformed tags, and obfuscation (`String.fromCharCode`, etc.). Defense requires context-aware encoding and safe APIs.

## NEVER
- Use `innerHTML`, `document.write`, `eval`, `new Function`, `setTimeout(string)`, or `setInterval(string)` with user input
- Inline event handlers (`onclick="…"`) with server-rendered user data
- Roll your own sanitization logic — use established libraries
- Trust any input encoding scheme; always encode for the output context

## ALWAYS
- Encode output for the specific context where it is rendered
- Use `textContent` instead of `innerHTML` for plain text
- Validate input format before processing (allow-list regex)
- Use an established sanitization library (DOMPurify, OWASP Java Encoder, HTMLPurifier)
- Set a strict CSP: `default-src 'self'; script-src 'self'; object-src 'none'`
- Set `HttpOnly; Secure; SameSite=Strict` on session cookies

## Context-Aware Encoding

| Output context | Required encoding |
|---------------|-------------------|
| HTML content (between tags) | `encodeForHTML` |
| HTML attribute value | `encodeForHTMLAttribute` |
| JavaScript string | `encodeForJavaScript` |
| URL parameter | `encodeForURL` + validate redirect allow-list |
| CSS value | `encodeForCSS` |

## Safe API Substitutes

```javascript
// NEVER                          // ALWAYS
eval(input)                    // JSON.parse(input)
element.innerHTML = input      // element.textContent = input
document.write(input)          // DOM construction via createElement
setTimeout(input, 100)         // setTimeout(fn, 100) — fn is not a string
```

## Sanitization Libraries

| Platform | Library |
|----------|---------|
| JavaScript/DOM | DOMPurify (configure `ALLOWED_TAGS`, `ALLOWED_ATTR`) |
| Java | OWASP Java Encoder (`Encode.forHtml`, `Encode.forJavaScript`, …) |
| PHP | HTMLPurifier |

## Checklist
- [ ] All output encoded for its render context (HTML / attribute / JS / URL / CSS)
- [ ] No `innerHTML`, `eval`, `document.write`, `new Function` with user input
- [ ] No inline event handlers carrying server-rendered user data
- [ ] Established sanitization library used; no custom filter logic
- [ ] Strict CSP header deployed (`script-src 'self'`, `object-src 'none'`)
- [ ] Session cookies set with `HttpOnly; Secure; SameSite=Strict`
- [ ] Input allow-list validation applied before processing
