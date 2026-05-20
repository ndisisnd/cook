---
name: Skill Routing
description: mapping from review target type to standards skills to load from this repo
type: reference
---

# Skill Routing

## Global Review Base

- Always load `standards/global/SKILL.md` first — its P0 universal rules apply to every review. There are no mode flags.
- If the request is review work, also load `standards/review/SKILL.md`.
- Match the review target's keywords and touched-file patterns against the **Concern Match** table in `standards/global/_INDEX.md`, and load every concern ref that matches (`refs/architecture.md`, `refs/api-design.md`, `refs/error-handling.md`, `refs/security.md`, `refs/performance.md`, `refs/debug.md`).

## Surface-to-Skills Mapping

A review target can touch more than one surface; load the union of everything that matches.

| Review surface | Concern refs to load | Domain skills to load |
| --- | --- | --- |
| Frontend | `refs/architecture.md`, `refs/performance.md` | `standards/typescript/SKILL.md` or matching language skill; React/Next.js skills when files match |
| Backend | `refs/api-design.md`, `refs/error-handling.md` | `standards/typescript/SKILL.md` or matching language skill; database/GraphQL skills when files match |
| Full-stack | union of the frontend and backend rows | union of frontend and backend skills that match the touched files |
| Security-sensitive | `refs/security.md` (in addition to the above) | matching domain skills; activate when the change touches auth, access control, injection risk, uploads, redirects, or third-party inputs |

## Trigger Checks

- Frontend signals: `.tsx`, `.jsx`, `components/`, `pages/`, `app/`, `hooks/`, `styles/`
- Backend signals: `controllers/`, `routes/`, `handlers/`, `services/`, `repositories/`, `db/`
- Full-stack signals: both frontend and backend files in one review target
- Security-sensitive signals: auth, token, session, role, permission, owner scope, upload, redirect, webhook, external URL

## Worked Examples

- Reviewing a React checkout form with TypeScript: load `standards/global/SKILL.md`, `standards/review/SKILL.md`, `standards/global/refs/architecture.md` and `refs/performance.md`, `standards/typescript/SKILL.md`, plus matching React skills. Add `standards/global/refs/security.md` because the form handles payment input.
- Reviewing a new API endpoint with auth: load `standards/global/SKILL.md`, `standards/review/SKILL.md`, `standards/global/refs/api-design.md`, `refs/error-handling.md`, and `refs/security.md`, plus the matching language and framework skills.
