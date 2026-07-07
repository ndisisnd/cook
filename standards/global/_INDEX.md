<!-- Concern index for the global skill. Routing lives in vocab/tag-vocabulary.json — single source. -->
# global Skills Index

## Load Order

1. Always load `<SKILLS>/global/SKILL.md` — P0 universal rules apply to every code task.
2. Concern routing is owned by `vocab/tag-vocabulary.json`: each tag whose
   `routes_to` is `concern:<name>` loads `refs/<name>.md`. Run
   `python3 scripts/cook_cache.py classify` (or match the vocab aliases) —
   there is no keyword table here to scan.

The concern shelf is exactly: `refs/architecture.md`, `refs/api-design.md`,
`refs/error-handling.md`, `refs/security.md`, `refs/auth.md`,
`refs/performance.md`, `refs/debug.md`, `refs/cicd.md`.

## Notes

- Concern refs hold the prescriptive layer rules (frontend component/UI-security/render-performance and backend API/error/auth/query rules) folded in by topic — there is no separate frontend/backend/full-stack file.
- This file used to duplicate the vocab's keyword column; that copy (and its parity-drift risk) was removed. Edit routing in the vocab only.
