---
name: Skill Routing
description: mapping from review target type to standards skills to load from this repo
type: reference
---

# Skill Routing

## Global Review Base

- Always load `standards/global/SKILL.md` first with the appropriate mode flag.
- If the request is review work, also load `standards/review/SKILL.md`.

## Review Mode Mapping

| Review mode | Mode flag | Additional skills to load |
| --- | --- | --- |
| Frontend | `--frontend` | `standards/typescript/SKILL.md` or matching language skill; React/Next.js skills when files match |
| Backend | `--backend` | `standards/typescript/SKILL.md` or matching language skill; database skills when files match |
| Full-stack | `--full-stack` | Union of frontend and backend skills that match the touched files |
| Security-sensitive | `--backend` or `--full-stack` + load `standards/global/refs/security.md` | Activate when change touches auth, access control, injection risk, uploads, redirects, or third-party inputs |

## Trigger Checks

- Frontend signals: `.tsx`, `.jsx`, `components/`, `pages/`, `app/`, `hooks/`, `styles/`
- Backend signals: `controllers/`, `routes/`, `handlers/`, `services/`, `repositories/`, `db/`
- Full-stack signals: both frontend and backend files in one review target
- Security-sensitive signals: auth, token, session, role, permission, owner scope, upload, redirect, webhook, external URL

## Worked Examples

- Reviewing a React checkout form with TypeScript: load `standards/global/SKILL.md --frontend`, `standards/review/SKILL.md`, `standards/typescript/SKILL.md`, plus matching React skills. Load `standards/global/refs/security.md` because the form handles payment input.
- Reviewing a new API endpoint with auth: load `standards/global/SKILL.md --backend`, `standards/review/SKILL.md`, `standards/global/refs/api-design.md`, `standards/global/refs/security.md`, plus the matching language and framework skills.
