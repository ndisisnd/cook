---
description: Prevent clickjacking via HTTP headers, cookie attributes, and frame-buster script
alwaysApply: false
---

# Clickjacking Defense

## NEVER
- Use `X-Frame-Options: ALLOW-FROM` — obsolete, unsupported by modern browsers
- Rely solely on JavaScript frame-busters — advanced attackers can defeat them
- Apply framing protections only to sensitive pages — protect all pages

## ALWAYS
- Set `Content-Security-Policy: frame-ancestors 'none'` (or `'self'`/allowlisted origins)
- Add `X-Frame-Options: DENY` as fallback for older browsers that lack CSP support
- Apply cookie `SameSite=Lax` (or `Strict`) + `Secure` + `HttpOnly` on session cookies
- Inject headers globally via web server/CDN config, not per-page manually
- Combine all three layers (CSP, X-Frame-Options, frame-buster) for defense in depth

## Headers

| Header | Value | Notes |
|--------|-------|-------|
| `Content-Security-Policy` | `frame-ancestors 'none'` | Preferred; overrides X-Frame-Options |
| `Content-Security-Policy` | `frame-ancestors 'self' https://trusted.com` | When embedding is required |
| `X-Frame-Options` | `DENY` or `SAMEORIGIN` | Fallback for older browsers |
| `Set-Cookie` | `SameSite=Lax; Secure; HttpOnly` | Prevents cross-origin cookie inclusion |

## Frame-Buster (legacy browsers)

```html
<style id="antiClickjack">body{display:none !important;}</style>
<script>
  if (self === top) { document.getElementById("antiClickjack").remove(); }
  else { top.location = self.location; }
</script>
```

## Checklist
- [ ] `frame-ancestors` CSP directive set on all responses
- [ ] `X-Frame-Options` fallback header present
- [ ] Session cookies have `SameSite`, `Secure`, `HttpOnly`
- [ ] Headers injected globally (server/CDN), not per-page
- [ ] Sensitive in-frame actions require additional confirmation when framing is intentional
- [ ] CSP violation reporting endpoint configured for monitoring
