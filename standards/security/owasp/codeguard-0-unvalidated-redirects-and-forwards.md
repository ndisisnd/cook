---
description: Prevent open redirect and forward vulnerabilities by validating all user-controlled redirect destinations
alwaysApply: false
---

# Unvalidated Redirects and Forwards

## NEVER
- Use raw user input (query params, form fields) as a redirect or forward destination
- Forward server-side requests to a destination derived from user input without validation
- Use deny-list approaches to filter redirect destinations
- Trust `returnUrl` / `url` parameters without validating against an allow-list
- In PHP: omit `exit` after `header("Location: ...")` — execution continues otherwise

## ALWAYS
- Prefer hardcoded redirect URLs that cannot be manipulated
- Map user-supplied tokens/IDs to full URLs server-side; never expose the target URL as input
- Validate any required user input against a strict allow-list of permitted destinations
- Verify the user is authorized for the redirect/forward target before acting
- Use interstitial warning pages for redirects to external domains
- Use large or cryptographically complex token spaces to prevent enumeration
- Keep frameworks updated (ASP.NET MVC 1/2 are particularly vulnerable; use MVC 3+)

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
- [ ] Server-side mapping used for any user-influenced redirect
- [ ] All destinations validated against an allow-list before redirect
- [ ] User authorization verified for redirect/forward target
- [ ] External redirects show an interstitial warning page
- [ ] Token spaces are large enough to prevent enumeration
- [ ] PHP redirects followed by `exit;` to halt further execution
