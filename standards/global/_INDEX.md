<!-- Concern index for the global skill. cook matches task keywords/patterns against this table. -->
# global Skills Index

## Load Order

1. Always load `<SKILLS>/global/SKILL.md` — P0 universal rules apply to every code task.
2. Match the task's keywords and touched-file patterns against the Concern Match table below.
3. Load each concern ref whose patterns or keywords match at least one signal.

Layer selection (frontend vs backend vs full-stack) is no longer decided here — `cook/SKILL.md` extracts keywords and matches concerns directly. There are no mode flags.

## Concern Match (match against task keywords and touched files)

| Ref | File pattern | Keywords |
| --- | ------------ | -------- |
| `refs/architecture.md` | `**/components/**`, `**/services/**`, `**/hooks/**`, `**/widgets/**` | architecture, component, state, hook, lift state, business logic, logic leak, layer, monolith, god class, refactor, structure, duplication |
| `refs/api-design.md` | `**/controllers/**`, `**/routes/**`, `**/handlers/**`, `**/api/**`, `**/*.controller.*` | api, endpoint, rest, http, GET, POST, status code, pagination, paginate, versioning, version bump, contract, openapi |
| `refs/error-handling.md` | `**/*.controller.*`, `**/*.service.*`, `**/domain/**`, `**/infrastructure/**` | error, exception, throw, catch, failure, error code, envelope, error boundary, domain error |
| `refs/security.md` | `**/auth/**`, `**/middleware.*`, `**/*.controller.*` | security, secret, owasp, sanitize, validate, validation, xss, sql injection, dangerouslySetInnerHTML, localStorage, tenant, owner, guard, cors, ssrf, pii |
| `refs/auth.md` | `**/auth/**`, `**/middleware.*`, `**/login/**`, `**/*.guard.*` | auth, login, oauth, pkce, token, jwt, session, cookie, rbac, role, scope, csrf, password hash |
| `refs/performance.md` | `**/components/**`, `**/*.entity.ts`, `**/migrations/*.sql` | performance, slow, n+1, index, re-render, memo, virtualize, waterfall, parallel fetch, cache, latency, throughput, bottleneck, profile |
| `refs/debug.md` | n/a | debug, crash, trace, stack trace, reproduce, repro, bug report, regression |

## Notes

- Concern refs hold the prescriptive layer rules (frontend component/UI-security/render-performance and backend API/error/auth/query rules) folded in by topic — there is no separate frontend/backend/full-stack file.
- For findings-first code review, load `<SKILLS>/review/SKILL.md` instead of this skill.
