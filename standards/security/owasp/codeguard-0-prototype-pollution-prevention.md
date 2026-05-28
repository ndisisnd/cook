---
description: Prevent prototype pollution in JavaScript/TypeScript by using safe data structures and freezing built-in prototypes
alwaysApply: false
---

# Prototype Pollution Prevention

Attackers who can write to `__proto__` or `constructor.prototype` can escalate privileges or achieve RCE.

## NEVER
- Use plain `{}` object literals as key-value stores for untrusted data
- Merge/clone user input into objects without sanitizing `__proto__` and `constructor` keys
- Allow unchecked access to `__proto__`, `constructor`, or `prototype` from external data

## ALWAYS
- Prefer `new Map()` or `new Set()` over plain objects for dynamic key-value storage
- When objects are required, create with `Object.create(null)` to strip prototype chain
- Freeze built-in prototypes in high-risk contexts: `Object.freeze(Object.prototype)`
- Run Node.js with `--disable-proto=delete` as a defense-in-depth measure

## Safe Data Structures

```javascript
// Prefer Map/Set
const allowedTags = new Set(['b', 'i']);
const options = new Map([['spaces', 1]]);

// When object required — no prototype
const obj = Object.create(null);
// Last resort with literal
const obj2 = { __proto__: null };
```

## Checklist
- [ ] Dynamic key-value stores use `Map`/`Set`, not `{}`
- [ ] Objects built from external input created with `Object.create(null)`
- [ ] No merge/clone utility writes `__proto__` or `constructor` keys
- [ ] `Object.freeze(Object.prototype)` applied where appropriate
- [ ] Node.js deployed with `--disable-proto=delete`
- [ ] Dependencies audited for prototype pollution vulnerabilities
