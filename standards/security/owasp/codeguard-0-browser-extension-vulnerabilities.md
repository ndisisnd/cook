---
description: Browser extension security — manifest hardening, XSS prevention, storage, and supply chain
alwaysApply: false
---

# Browser Extension Security

## NEVER
- Request broad host permissions (`<all_urls>`, `http://*/*`) when specific origins suffice
- Use `eval()`, `new Function()`, `setTimeout(str)`, or dynamic `import()` of remote URLs
- Assign untrusted input to `.innerHTML` without a sanitization library (e.g., DOMPurify)
- Store sensitive data in `localStorage` — it is accessible to any script on the same origin
- Inject sensitive information directly into a web page's DOM
- Use the DOM as a communication channel between content and background scripts
- Fetch and execute remote code — all logic must be bundled in the initial package
- Ship third-party libraries without auditing them (run `npm audit` regularly)

## ALWAYS
- Request only the minimum permissions needed; list explicit origins instead of wildcards
- Define a strict CSP in `manifest.json`: `script-src 'self'; object-src 'self'`
- Use `.textContent` for plain text; sanitize fully before any `.innerHTML` assignment
- Store sensitive data in `chrome.storage` (isolated to the extension)
- Encrypt sensitive data before storing it
- Use HTTPS (`wss://` for WebSockets) for all network communication; monitor for unauthorized exfiltration
- Display sensitive information in extension-owned UI (popup, sidebar, options page) — not injected into page DOM
- Use `chrome.runtime.sendMessage` / `chrome.tabs.sendMessage` for content↔background communication

## Manifest security baseline
```json
"content_security_policy": {
  "extension_pages": "script-src 'self'; object-src 'self'"
}
```

## Checklist
- [ ] Manifest requests minimal, explicit permissions — no wildcard host patterns
- [ ] Strict CSP set; inline scripts and `eval()` blocked
- [ ] No dynamic code execution (`eval`, `new Function`, string timers, remote `import()`)
- [ ] `.innerHTML` never receives unsanitized data; DOMPurify used where HTML is required
- [ ] Sensitive data stored in `chrome.storage`, encrypted; not in `localStorage`
- [ ] All network calls use HTTPS/WSS
- [ ] Message passing via `chrome.runtime` APIs only; no DOM-based IPC
- [ ] Dependencies audited with `npm audit`; no remote code loaded at runtime
