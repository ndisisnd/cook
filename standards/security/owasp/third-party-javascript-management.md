---
description: Prevent arbitrary code execution and data leakage from third-party JavaScript tags
alwaysApply: false
---

# Third-Party JavaScript Management

Third-party JS carries three critical risks: loss of change control, arbitrary code execution on clients, and data leakage to vendors.

## NEVER
- Allow third-party scripts direct DOM access or URL parameter access
- Load third-party scripts without integrity verification in high-risk contexts
- Grant tag manager configurations access beyond the controlled data layer
- Enable custom HTML/JavaScript tags in tag managers where avoidable
- Skip vendor agreements requiring secure coding and change-detection controls

## ALWAYS
- Populate the data layer exclusively with first-party, sanitized code
- Restrict third-party scripts to reading from the controlled data layer only
- Add `integrity` (SRI) hashes to all external `<script>` tags
- Update SRI hashes whenever vendor scripts change
- Validate `event.origin` before processing any `postMessage` data
- Sanitize dynamic DOM data before including it in tag payloads (DOMPurify / MentalJS)
- Keep all JavaScript libraries updated; scan with RetireJS
- Require 2FA for tag management system configuration access

## Containment Strategies

| Strategy | Protection | Trade-off |
|----------|-----------|-----------|
| Server-direct data layer | No DOM/URL access; only validated data sent | Most scalable for large sites |
| Subresource Integrity (SRI) | Only reviewed code executes | Vendor must enable CORS; requires hash maintenance |
| iframe sandbox | Isolates DOM and cookie access | Needs postMessage bridge; CSP recommended |

SRI example:
```html
<script src="https://analytics.vendor.com/v1.1/script.js"
  integrity="sha384-MBO5IDfYaE6c6Aao94oZrIOiC7CGiSNE64QUbHNPhzk8Xhm0djE6QqTpL0HzTUxk"
  crossorigin="anonymous"></script>
```

iframe sandbox (validate origin before processing messages):
```html
<iframe src="https://static.example.net/analytics.html"
  sandbox="allow-same-origin allow-scripts"></iframe>
```

## Checklist
- [ ] Data layer populated only by first-party code; vendor scripts cannot read URL params
- [ ] SRI `integrity` attribute present on all external scripts
- [ ] SRI hashes updated after any vendor script change
- [ ] iframe sandbox used for high-risk vendor scripts with origin-validated postMessage
- [ ] Dynamic data sanitized with DOMPurify or equivalent before tag payloads
- [ ] JavaScript libraries scanned with RetireJS; vulnerabilities remediated
- [ ] Vendor contracts include secure coding, code integrity monitoring, and breach penalties
