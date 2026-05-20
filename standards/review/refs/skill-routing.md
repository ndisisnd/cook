---
name: Skill Routing
description: mapping from review target type to standards skills to load from this repo
type: reference
---

# Skill Routing

## Global Review Base

- Always load `standards/global/SKILL.md` first.
- If the request is review work, also load `standards/review/SKILL.md`.
- Load `standards/global/security-standards/SKILL.md` for both frontend and backend review.

## Review Mode Mapping

| Review mode | Load these standards |
| --- | --- |
| Frontend | `standards/global/error-handling/SKILL.md`, `standards/react/*`, `standards/nextjs/*` when file matches, plus language skill such as `standards/typescript/SKILL.md` |
| Backend | `standards/global/api-design/SKILL.md`, `standards/global/error-handling/SKILL.md`, `standards/typescript/SKILL.md` or other language skill, plus framework or database skills when file matches |
| Full-stack | Union of frontend and backend standards that match the touched files |
| Security-sensitive | Add `standards/global/owasp/SKILL.md` and `standards/global/security-audit/SKILL.md` when the change touches auth, access control, injection risk, uploads, redirects, or third-party inputs |

## Trigger Checks

- Frontend signals: `.tsx`, `.jsx`, `components/`, `pages/`, `app/`, `hooks/`, `styles/`
- Backend signals: `controllers/`, `routes/`, `handlers/`, `services/`, `repositories/`, `db/`
- Full-stack signals: both frontend plus backend files in one review target
- Security-sensitive signals: auth, token, session, role, permission, owner scope, upload, redirect, webhook, external URL

## Worked Example

- Reviewing a React checkout form with TypeScript loads `standards/global/SKILL.md`, `standards/review/SKILL.md`, `standards/global/security-standards/SKILL.md`, `standards/typescript/SKILL.md`, plus the matching React skills.
- Reviewing a new API endpoint with auth loads `standards/global/SKILL.md`, `standards/review/SKILL.md`, `standards/global/api-design/SKILL.md`, `standards/global/error-handling/SKILL.md`, `standards/global/security-standards/SKILL.md`, `standards/global/owasp/SKILL.md`, plus the matching language and framework skills.
