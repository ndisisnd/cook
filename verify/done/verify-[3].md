---
status: complete
---

# Verification Run [3] — Global Standards Collapse + Refs Extraction

## 1. What Was Changed

### Global standards — full restructure

**Before:** 9 separate sub-skill directories under `standards/global/`, each with their own `SKILL.md` and `refs/`:
```
standards/global/
├── api-design/          (HTTP semantics, status codes, URL design, OpenAPI)
├── architecture/        (structural audit, logic leakage, monolith detection)
├── coding-principles/   (SOLID, KISS, DRY, YAGNI, naming)
├── debug/               (scientific method, bug report template)
├── error-handling/      (error layers, response envelope)
├── owasp/               (OWASP Web Top 10, API Top 10 checklists)
├── performance/         (profiling workflow, memoization, batching)
├── security-audit/      (SAST scan commands, CVE scanning)
├── security-standards/  (parameterized queries, secret management, PII)
├── _INDEX.md            (stale routing table pointing to deleted sub-skills)
└── SKILL.md             (thin — only universal principles, no mode support)
```

**After:** Single skill with a lean `SKILL.md` and consolidated `refs/` following the dart exemplar:
```
standards/global/
├── SKILL.md             (P0 universal rules + P1 mode rules: --frontend, --backend, --full-stack)
├── _INDEX.md            (updated — mode routing + ref loading table, stale refs removed)
└── refs/
    ├── api-design.md    (HTTP verbs, status codes, URL design, versioning, pagination, OpenAPI)
    ├── architecture.md  (logic leakage detection, monolith thresholds, remediation table)
    ├── debug.md         (scientific method, bug report template)
    ├── error-handling.md (3-layer architecture, response envelope, classification table)
    ├── performance.md   (profile-first workflow, memoization, batching, UI/network patterns)
    └── security.md      (OWASP Web + API Top 10, SAST scan commands, secure coding patterns)
```

### `standards/global/SKILL.md` — rewritten

Following the dart exemplar (inline content, priority levels, conditional refs):

- **P0 — Universal Rules**: Core design (SOLID/KISS/DRY/YAGNI), readability (guard clauses, naming), safety (input validation, error handling, secrets, resource cleanup), security baseline (no raw SQL, no wildcard CORS, no full entity return), change quality.
- **P1 — Mode-Specific Rules**:
  - `--frontend`: component structure, UI security (no `dangerouslySetInnerHTML`, no `localStorage` for auth tokens), rendering performance
  - `--backend`: API semantics, error architecture (3-layer model), auth/ownership (owner scoping, role guards), DB performance (no N+1)
  - `--full-stack`: union of both + cross-layer contract rules
- **Anti-Patterns**: 13-item consolidated list, no duplicates with refs
- **References**: conditional loading — 6 refs with explicit task-based conditions

### `standards/global/_INDEX.md` — rewritten

Removed routing to 9 deleted sub-skills. Now describes:
- File match triggers for each mode flag
- Inline mode routing (all content is in SKILL.md — no extra files to load)
- Ref loading table with per-ref conditions

### `standards/review/refs/skill-routing.md` — updated

Replaced all references to deleted sub-skill paths (`global/api-design/SKILL.md`, `global/security-standards/SKILL.md`, etc.) with:
- Mode flag invocation on `global/SKILL.md`
- Direct refs paths (`global/refs/security.md`, `global/refs/api-design.md`) for security-sensitive supplement

---

## 2. Expected Output When Running the Skill

When a coding agent loads `standards/global/SKILL.md` correctly:

### Scenario A — Writing any code (no mode)
- Loads: `global/SKILL.md` only
- Applies: SOLID/KISS/DRY, guard clauses, safety rules, 3-rule security baseline
- Does NOT load any ref

### Scenario B — Frontend feature (React component, hook, page)
- Loads: `global/SKILL.md --frontend`
- Applies: all P0 rules + component structure, UI security, rendering performance
- Loads `refs/security.md` only if the task is security-sensitive (auth forms, token handling)

### Scenario C — Backend feature (API endpoint, service, DB access)
- Loads: `global/SKILL.md --backend`
- Applies: all P0 rules + API semantics, error architecture, auth/ownership, DB performance
- Loads `refs/api-design.md` for endpoint design work; `refs/error-handling.md` for error hierarchy work; `refs/security.md` for OWASP checklist

### Scenario D — Full-stack task
- Loads: `global/SKILL.md --full-stack`
- Applies: union of --frontend and --backend rules + cross-layer contract rules
- Loads refs as needed

### Scenario E — Security audit
- Loads: `global/SKILL.md` + `refs/security.md`
- Applies: OWASP Web + API checklists, SAST scan commands, CVE scanning steps

---

## 3. Success Criteria

### Structure
- [x] `standards/global/SKILL.md` exists and is non-empty
- [x] `standards/global/refs/api-design.md` exists
- [x] `standards/global/refs/architecture.md` exists
- [x] `standards/global/refs/debug.md` exists
- [x] `standards/global/refs/error-handling.md` exists
- [x] `standards/global/refs/performance.md` exists
- [x] `standards/global/refs/security.md` exists
- [x] The 9 old sub-skill directories do NOT exist: `api-design/`, `architecture/`, `coding-principles/`, `debug/`, `error-handling/`, `owasp/`, `performance/`, `security-audit/`, `security-standards/`
- [x] `standards/global/_INDEX.md` contains no references to deleted sub-skill paths
- [x] `standards/review/refs/skill-routing.md` contains no references to deleted sub-skill paths

### Content — SKILL.md
- [x] Contains P0 section with: SOLID/KISS/DRY/YAGNI, guard clauses, safety (input validation + error handling + secrets + resource cleanup), 3-rule security baseline (no raw SQL, no wildcard CORS, no full ORM entity), change quality
- [x] Contains P1 `--frontend` section with: component-per-file rule, state locality, no `dangerouslySetInnerHTML`, no `localStorage` for auth tokens, no unbounded list renders
- [x] Contains P1 `--backend` section with: GET is idempotent, correct status codes, pagination defaults, 3-layer error model, owner/tenant scoping, role guard requirement, no N+1
- [x] Contains P1 `--full-stack` section with: no business logic leak, validate once at server, API contract versioning
- [x] References section uses conditional loading language ("Load only what the current task requires")

### Content — Refs
- [x] `refs/api-design.md` contains: HTTP verb table, status code table, URL design rules, versioning rules, pagination envelope, OpenAPI requirements, worked URL examples
- [x] `refs/error-handling.md` contains: 3-layer table, error mechanics (wrap/replace), standard JSON envelope, error classification table
- [x] `refs/security.md` contains: parameterized query example, OWASP Web Top 10 table, OWASP API Top 10 table, SAST grep commands, CVE scan commands
- [x] `refs/architecture.md` contains: structural duplication detection, logic leakage detection scripts (web/mobile/backend), monolith thresholds table, remediation table
- [x] `refs/performance.md` contains: baseline/identify/fix/verify workflow, memoization code example, batching code example, UI virtualization rule
- [x] `refs/debug.md` contains: 5-step scientific method, best practices, bug report template

### No duplication
- [x] SKILL.md anti-patterns do not repeat ref anti-patterns (spot-check: raw SQL, wildcard CORS, N+1, swallowed errors)
- [x] `refs/security.md` OWASP content does not duplicate `refs/api-design.md` status code content
- [x] `refs/error-handling.md` envelope does not duplicate `refs/api-design.md` error body example

### Routing correctness
- [x] `review/refs/skill-routing.md` references `global/SKILL.md --frontend` (not `global/security-standards/SKILL.md`)
- [x] `review/refs/skill-routing.md` references `global/refs/security.md` for security-sensitive supplement
- [x] `global/_INDEX.md` mode routing section does not mention any deleted sub-skill path
