---
description: Prevent DOM clobbering attacks where HTML id/name attributes override JS variables and APIs
alwaysApply: false
---

# DOM Clobbering Prevention

## NEVER
- Allow `id` or `name` attributes in user-generated HTML content
- Use `innerHTML` with unsanitized user input
- Disable `SANITIZE_NAMED_PROPS` in DOMPurify configuration
- Store sensitive data on `window` or `document` objects
- Use implicit global variables without `const`/`let`/`var` declaration
- Set `id` or `name` attributes dynamically from user input
- Use dynamic attribute assignment without validation

## ALWAYS
- Sanitize user HTML with DOMPurify using `SANITIZE_DOM: true`, `SANITIZE_NAMED_PROPS: true`, and `FORBID_ATTR: ['id', 'name']`
- Enable `"use strict"` in all JavaScript files
- Declare all variables explicitly with `const` or `let`
- Validate object types before accessing properties that could be clobbered
- Verify built-in APIs are functions before calling (`typeof document.getElementById === 'function'`)
- Implement strict CSP: `script-src 'self' 'nonce-{random}'; object-src 'none'; require-trusted-types-for 'script'`
- Use Trusted Types wrapping DOMPurify for all `innerHTML` assignments

## Sanitizer Configuration
```javascript
const clean = DOMPurify.sanitize(userInput, {
  SANITIZE_DOM: true,
  SANITIZE_NAMED_PROPS: true,
  FORBID_ATTR: ['id', 'name']
});
// OR: Sanitizer API
const sanitizer = new Sanitizer({
  blockAttributes: [{'name': 'id', elements: '*'}, {'name': 'name', elements: '*'}]
});
element.setHTML(userInput, {sanitizer});
```

## Dynamic Attribute Guard
```javascript
const FORBIDDEN_ATTRS = ['id', 'name', 'onclick', 'onload', 'onerror'];
if (FORBIDDEN_ATTRS.includes(name.toLowerCase())) throw new Error('Prohibited attribute');
```

## Checklist
- [ ] DOMPurify configured with `SANITIZE_NAMED_PROPS: true` and `FORBID_ATTR: ['id', 'name']`
- [ ] No direct `innerHTML` without sanitization
- [ ] `"use strict"` in all JS files; all variables explicitly declared
- [ ] No sensitive data stored on `window`/`document`
- [ ] Dynamic attribute setting validates against forbidden list
- [ ] CSP headers with `require-trusted-types-for 'script'` deployed
- [ ] Type validation performed before accessing potentially clobbered properties
