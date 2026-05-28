---
description: Open redirect prevention — block user-controlled redirect targets that enable phishing
alwaysApply: false
---

# Open Redirects

## NEVER
- Use user input directly as a redirect target (`res.redirect(userInput)`)
- Allow wildcard domains (e.g. `*.example.com`) in any redirect allowlist
- Validate redirect URLs with simple substring checks instead of full URL parsing

## ALWAYS
- Restrict user-controlled redirects to local paths only (must start with `/`, no protocol prefix), OR
- Validate against a strict allowlist of trusted domains using a robust URL parsing library
- Add an explicit code comment at every redirect documenting which rule is enforced

## Checklist
- [ ] No redirect accepts raw user input without validation
- [ ] Local-path redirects enforced: starts with `/`, no `http:`/`https:` prefix
- [ ] Allowlist-based redirects use exact domain matching via URL parser
- [ ] No wildcard domains in allowlist
- [ ] All redirect sites have explanatory code comments
