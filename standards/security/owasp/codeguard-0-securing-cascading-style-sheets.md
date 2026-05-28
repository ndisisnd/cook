---
description: Prevent CSS from disclosing application roles, features, and sensitive functionality to attackers
alwaysApply: false
---

# Securing Cascading Style Sheets

Global CSS files containing role-based selectors expose application structure and enable targeted attacks.

## NEVER
- Serve a single global CSS file containing selectors for all user roles
- Use descriptive selector names that reveal functionality (`.addUsers`, `.deleteUsers`, `.changePassword`, `.exportUserData`, `.addNewAdmin`)
- Allow authenticated users to access CSS files scoped to other roles
- Accept user-authored HTML/CSS content without sanitization

## ALWAYS
- Create separate CSS files per role (e.g., `StudentStyling.css`, `AdministratorStyling.css`)
- Enforce server-side access control before serving role-scoped CSS files
- Log and alert on unauthorized CSS file access attempts (forced browsing)
- Use build-time obfuscation to generate non-descriptive class names
- Sanitize and restrict styles in user-generated content
- Use structural/element-based selectors instead of feature-named classes

## Selector Obfuscation

```css
/* Revealing — avoid */
#UserPage .Toolbar .addUserButton { }

/* Structural — prefer */
#page_u header button:first-of-type { }
```

Build-time tools that auto-generate opaque names:
- JSS (CSS-in-JS) with `minify` → `.c001`, `.c002`
- CSS Modules with `localIdentName` option
- .NET Blazor CSS Isolation → `button.add[b-3xxtam6d07]`
- CSS frameworks (Bootstrap, Tailwind) reduce need for custom selectors

## Checklist
- [ ] CSS files segmented by role; no global file serving all roles
- [ ] Server-side access control validated before CSS delivery
- [ ] Unauthorized CSS access attempts logged and alerted
- [ ] Class names obfuscated at build time or use structural selectors
- [ ] User-generated HTML/CSS sanitized and restricted
- [ ] CSS access controls tested to confirm role isolation
