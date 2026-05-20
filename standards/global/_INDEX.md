<!-- Top-level routing for the global skill. -->
# global Skills Index

## Load Order

1. Load `<SKILLS>/global/SKILL.md`.
2. If no mode is passed explicitly, infer it from the task summary, mentioned files, and expected change surface.
3. Pass the appropriate mode flag (`--frontend`, `--backend`, or `--full-stack`) so the mode-specific rules in SKILL.md apply.
4. Load refs only when the task explicitly needs them.

## File Match

| Skill | File pattern | Keywords |
| ----- | ------------ | -------- |
| **global** | `**/*.{ts,tsx,js,jsx,go,dart,java,kt,swift,py}` | dry, kiss, solid, refactor, clean code, readability, naming, error handling, security, performance |
| global `--frontend` | `**/*.{tsx,jsx,css,scss}`, `**/components/**`, `**/pages/**`, `**/app/**`, `**/hooks/**` | frontend, ui, form, state, rendering, client, browser |
| global `--backend` | `**/controllers/**`, `**/routes/**`, `**/handlers/**`, `**/services/**`, `**/repositories/**`, `**/api/**`, `**/*.controller.*`, `**/*.service.*` | backend, api, endpoint, auth, database, query, persistence |
| global `--full-stack` | n/a | full-stack, full stack, end-to-end, connect ui to api |

## Mode Routing

All mode-specific rules are inline in `global/SKILL.md`. No additional skill files to load.

- `--frontend` — component structure, UI security, rendering performance
- `--backend` — API semantics, error architecture, auth/ownership, DB performance
- `--full-stack` — union of both, plus cross-layer contract rules

Use `--full-stack` only when the task genuinely spans UI and server concerns.

## Ref Loading

Load refs from `global/refs/` only when the task explicitly requires them:

| Ref | Load when |
| --- | --- |
| `refs/api-design.md` | designing endpoints, choosing status codes, writing OpenAPI |
| `refs/error-handling.md` | defining error hierarchies or response envelopes |
| `refs/security.md` | implementing auth, OWASP checklist, or running a SAST scan |
| `refs/architecture.md` | auditing structural debt or detecting logic leakage |
| `refs/performance.md` | profiling or fixing a proven bottleneck |
| `refs/debug.md` | troubleshooting crashes or filing a bug report |

## Notes

- For findings-first code review, load `<SKILLS>/review/SKILL.md` instead of this skill.
