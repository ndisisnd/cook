---
# Allowed values: planned, complete
status: planned
---

# Verification Run [11.1] - Fix Next.js Consolidation Audit Gaps

> Follow-up to verify-[11]. The Next.js domain was consolidated, but post-verification found
> source-coverage gaps, stale examples, and one guardrail violation. This plan authorizes only the
> narrow remediation needed to make the consolidation true to verify-[11].

---

## 1. Scope

Allowed paths:

- `standards/nextjs/SKILL.md`
- `standards/nextjs/_INDEX.md`
- `standards/nextjs/refs/*.md`
- `CHANGELOG.md`
- `verify/verify-[11.1].md`

Verify-only paths:

- `archive/nextjs/**`
- `verify/done/verify-[11].md`

Guardrails:

- Do not edit archived source folders; use them only as truth sources.
- Do not edit other domains.
- Do not silently drop any source rule; carry it or record a deliberate drop with reason.
- Prefer additive, narrow edits over rewrites.
- If reverting the root `SKILL.md` wording would conflict with later intended orchestrator work, stop and ask before changing it.

---

## 2. Findings To Fix

| ID | Severity | Finding | Required action |
|---|---|---|---|
| 11.1-A | High | Root `SKILL.md` was edited even though verify-[11] marked `cook/SKILL.md` verify-only. | Either revert the verify-[11] root `SKILL.md` edits or explicitly re-scope with user approval before keeping them. |
| 11.1-B | High | `refs/rendering-and-caching.md` contains a server-side example using `fetch('/api/posts', ...)`, conflicting with the no-own-API rule. | Rewrite the example to call a DAL/service function or direct database helper with cache tags. |
| 11.1-C | High | Next 15 async route API examples still access `params.id` synchronously in `rendering-and-caching.md` and `styling-and-optimization.md`. | Rewrite examples to type `params` as a Promise and `await params` before reading fields. |
| 11.1-D | Medium | Authentication library selection from `nextjs-authentication/SKILL.md` was dropped. | Add Auth.js/`next-auth` and Clerk selection guidance to `refs/security.md`, or document a deliberate drop. |
| 11.1-E | Medium | `dynamicParams` is advertised in `_INDEX.md` but has no guidance in `refs/rendering-and-caching.md`. | Add concise `dynamicParams` guidance near SSG/ISR/dynamic routes, or remove the keyword if deliberately unsupported. |
| 11.1-F | Medium | App Router route colocation rule was dropped. | Add route-folder colocation guidance to `refs/app-router.md`. |
| 11.1-G | Medium | Pages Router API response/status-code guidance was dropped. | Add API Routes response/status-code guidance to `refs/pages-router.md`. |
| 11.1-H | Medium | DAL standardized error handling is only implicit in an example. | Add explicit guidance for `NotFoundError`, `UnauthorizedError`, `error.tsx`, and `notFound()` to `refs/data-fetching.md`. |
| 11.1-I | Low | `X-XSS-Protection` was silently dropped from security headers. | Either add it as legacy/usually-unneeded guidance or record the deliberate drop because modern browsers ignore it. |

---

## 3. Execution Plan

1. Read each archived source cited by the findings:
   - `archive/nextjs/nextjs-authentication/SKILL.md`
   - `archive/nextjs/nextjs-data-access-layer/SKILL.md`
   - `archive/nextjs/nextjs-data-fetching/SKILL.md`
   - `archive/nextjs/nextjs-app-router/SKILL.md`
   - `archive/nextjs/nextjs-pages-router/SKILL.md`
   - `archive/nextjs/nextjs-rendering/SKILL.md`
   - `archive/nextjs/nextjs-security/SKILL.md`
2. Patch only the destination refs needed for 11.1-B through 11.1-I.
3. Resolve 11.1-A separately: revert the root `SKILL.md` edit unless user approval explicitly expands scope.
4. Update `CHANGELOG.md` with a newest-first pending entry for the verify-[11.1] follow-up fixes.
5. Update this file with audit results and mark completed criteria.

---

## 4. Success Criteria

### Coverage Fixes

- [ ] 11.1-B: No server/RSC example in active Next.js refs fetches the app's own `/api` route.
- [ ] 11.1-C: App Router examples that read `params`/`searchParams` use Next 15 async request API style.
- [ ] 11.1-D: Auth.js/`next-auth` and Clerk library-selection guidance is carried or deliberately dropped with reason.
- [ ] 11.1-E: `dynamicParams` has guidance in `refs/rendering-and-caching.md`, or `_INDEX.md` no longer advertises it.
- [ ] 11.1-F: App Router route-folder colocation guidance is present.
- [ ] 11.1-G: Pages Router API Routes include standardized response/status-code guidance.
- [ ] 11.1-H: DAL standardized error handling guidance is explicit.
- [ ] 11.1-I: `X-XSS-Protection` is either carried as legacy guidance or recorded as a deliberate drop.

### Guardrails

- [ ] 11.1-A is resolved by reverting root `SKILL.md` edits or by documented user approval to keep them.
- [ ] No archived source files are edited.
- [ ] No non-Next.js domain files are edited.
- [ ] `verify/done/verify-[11].md` remains unchanged after the move.

### Verification Commands

- [ ] `git diff --check`
- [ ] Grep active Next.js refs for own-API server examples: `fetch('/api`, `fetch("/api`, and localhost API calls.
- [ ] Grep active Next.js refs for synchronous App Router `params.id` / `params.slug` examples.
- [ ] Grep active Next.js refs for stale archived-path links.

---

## 5. Audit Result

- Status: pending
- Gaps fixed: pending
- Deliberate drops: pending
- Verification commands: pending
