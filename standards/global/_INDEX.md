<!-- Top-level routing for the compressed global skill. -->
# global Skills Index

## Load Order

1. Always load `<SKILLS>/global/SKILL.md` first.
2. If no mode is passed explicitly, infer it from the task summary, mentioned files, and expected change surface.
3. Load the topic skills mapped to that mode.
4. Load extra topic skills only when the task explicitly needs them.

## File Match

| Skill | File pattern | Keywords |
| ----- | ------------ | -------- |
| **global** | `**/*.{ts,tsx,js,jsx,go,dart,java,kt,swift,py}` | dry, kiss, solid, refactor, clean code, readability, naming, error handling, security, performance |
| global -> frontend mode | `**/*.{tsx,jsx,css,scss,less}`, `**/components/**`, `**/pages/**`, `**/app/**`, `**/views/**`, `**/hooks/**` | frontend, ui, form, state, rendering, accessibility, client, browser |
| global -> backend mode | `**/controllers/**`, `**/routes/**`, `**/handlers/**`, `**/services/**`, `**/repositories/**`, `**/api/**`, `**/db/**`, `**/*.controller.*`, `**/*.service.*`, `**/*.router.*`, `**/*.handler.*` | backend, api, endpoint, auth, authorization, database, query, persistence, queue, cron |
| global -> full-stack mode | n/a | full-stack, full stack, end-to-end, e2e, wire up, connect ui to api, frontend and backend |

## Mode Routing

### Frontend Mode

Load these topic skills after `global/SKILL.md`:

- `<SKILLS>/global/security-standards/SKILL.md`
- `<SKILLS>/global/error-handling/SKILL.md`
- `<SKILLS>/global/performance/SKILL.md`

`security-standards` is part of the default frontend load because secret hygiene, unsafe rendering, token leakage, and input handling are cross-cutting concerns.

### Backend Mode

Load these topic skills after `global/SKILL.md`:

- `<SKILLS>/global/api-design/SKILL.md`
- `<SKILLS>/global/security-standards/SKILL.md`
- `<SKILLS>/global/error-handling/SKILL.md`
- `<SKILLS>/global/performance/SKILL.md`

`security-standards` is part of the default backend load because boundary validation, auth, secret management, and data protection are always relevant.

### Full-Stack Mode

Load the union of frontend and backend topic skills:

- `<SKILLS>/global/api-design/SKILL.md`
- `<SKILLS>/global/security-standards/SKILL.md`
- `<SKILLS>/global/error-handling/SKILL.md`
- `<SKILLS>/global/performance/SKILL.md`

Use `full-stack` only when the task genuinely spans UI and server concerns.

## Security-Sensitive Supplement

Load `<SKILLS>/global/owasp/SKILL.md` only when the task is security-sensitive or explicitly requests security review.

Common triggers:

- auth, authorization, roles, sessions, tokens, or permissions
- exposed endpoints, resource ownership, tenant scoping, or access control
- untrusted HTML, injection risk, uploads, redirects, or external URLs
- third-party API consumption or webhook handling
- explicit requests for security review, audit, or OWASP checks

## Intent-Driven Supplements

Load these only when the task explicitly calls for them:

- `debug/SKILL.md` for debugging and root-cause analysis
- `architecture/SKILL.md` for structural refactors and architecture reviews
- `security-audit/SKILL.md` for security audits and vulnerability scans
- `code-review/SKILL.md` only until a separate top-level `review` skill replaces it

## Notes

- `coding-principles/SKILL.md` is superseded by `global/SKILL.md` for normal coding tasks.
- Topic folders remain separate and are loaded by mode; they are not merged into synthetic mode refs.
