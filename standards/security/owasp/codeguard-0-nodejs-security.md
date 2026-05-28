---
description: Node.js application security — injection, error handling, headers, and platform hardening
alwaysApply: false
---

# Node.js Security

## NEVER
- Use `eval()` with any user-supplied input (RCE risk)
- Pass user input to `child_process.exec` without validation (command injection)
- Use `fs` module with unsanitized paths (directory traversal)
- Return more fields than required from API endpoints
- Leave uncaught exceptions or unhandled EventEmitter errors without explicit handlers

## ALWAYS
- Limit request body size (e.g. `express.json({ limit: "1kb" })`)
- Validate all input with allowlists; sanitize for the target context
- Escape HTML/JS output using a library (e.g. `escape-html`, `node-esapi`)
- Set secure cookie flags: `secure: true, httpOnly: true, sameSite: true`
- Use `helmet` for security headers (HSTS, frameguard, CSP, noSniff, hidePoweredBy)
- Protect against CSRF on state-changing endpoints
- Use `hpp` middleware to prevent HTTP parameter pollution
- Enable strict mode (`"use strict"`)
- Use flat Promise chains or async/await — no callback nesting
- Run `npm audit` regularly; use Retire.js or OWASP Dependency-Check
- Apply security linters (ESLint security plugin, JSHint) in CI
- Test regexes for ReDoS with vuln-regex-detector

## Error Handling

```javascript
process.on("uncaughtException", function(err) {
  // log, clean up resources
  process.exit(); // avoid unknown state
});
emitter.on('error', function(err) { /* handle */ });
```

## Server Overload Protection

```javascript
const toobusy = require('toobusy-js');
app.use((req, res, next) => {
  if (toobusy()) res.status(503).send("Server Too Busy");
  else next();
});
```

## Brute-Force / Rate Limiting
- Apply rate limiting with delays on authentication endpoints (e.g. `express-bouncer`)
- Return HTTP 429 with retry-after information when threshold exceeded

## Checklist
- [ ] Request body size limits set for all body-parsing middleware
- [ ] All inputs validated with allowlist; outputs escaped
- [ ] `helmet` applied; CSP and HSTS configured
- [ ] Cookies use `secure`, `httpOnly`, `sameSite`
- [ ] CSRF protection on all state-changing routes
- [ ] `eval()` and raw `child_process.exec` absent from codebase
- [ ] `npm audit` clean; dependency scanner in CI
