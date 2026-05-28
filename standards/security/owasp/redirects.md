---
description: Prevent open redirect and forward vulnerabilities — validate destinations against strict allowlists, never accept raw user input as redirect target
alwaysApply: false
---

# Redirects and Forwards

## NEVER
- Use raw user input (query params, form fields) as a redirect or forward destination
- Forward server-side requests to a destination derived from user input without validation
- Use deny-list approaches to filter redirect destinations
- Trust `returnUrl` / `url` parameters without validating against an allow-list
- Allow wildcard domains (e.g. `*.example.com`) in any redirect allowlist
- Validate redirect URLs with simple substring checks instead of full URL parsing
- In PHP: omit `exit` after `header("Location: ...")` — execution continues otherwise

## ALWAYS
- Prefer hardcoded redirect URLs that cannot be manipulated
- Restrict user-controlled redirects to local paths only (must start with `/`, no protocol prefix), OR
- Map user-supplied tokens/IDs to full URLs server-side; never expose the target URL as input
- Validate any required user input against a strict allow-list of permitted destinations using a robust URL parsing library
- Verify the user is authorized for the redirect/forward target before acting
- Use interstitial warning pages for redirects to external domains
- Use large or cryptographically complex token spaces to prevent enumeration

## Prevention Strategies

| Strategy | Protection level | Notes |
|----------|-----------------|-------|
| Hardcoded URL | Highest | No user input involved |
| Server-side token→URL mapping | High | Prevents URL tampering; guard against ID enumeration |
| Allow-list validation + authz check | Medium | Use allow-list, not deny-list; verify user authorization |
| Interstitial warning page | Supplemental | Show destination; require user confirmation |

Safe (hardcoded) vs. unsafe (user-controlled) — Java:
```java
// Safe
response.sendRedirect("http://www.mysite.com");

// Unsafe — NEVER do this
response.sendRedirect(request.getParameter("url"));
```

## Checklist
- [ ] No redirect destination derived directly from untrusted request parameters
- [ ] Local-path redirects enforced: starts with `/`, no `http:`/`https:` prefix
- [ ] Server-side mapping used for any user-influenced redirect
- [ ] All destinations validated against an allow-list using a robust URL parser before redirect
- [ ] No wildcard domains in allowlist
- [ ] User authorization verified for redirect/forward target
- [ ] External redirects show an interstitial warning page
- [ ] Token spaces are large enough to prevent enumeration
- [ ] PHP redirects followed by `exit;` to halt further execution
