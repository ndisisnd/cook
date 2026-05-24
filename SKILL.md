---
name: cook
description: Keyword-driven orchestrator for this repository's coding and review standards. Receives a code-task summary from the invoking agent, extracts keywords, matches them against the global concern index and the relevant domain indexes, loads only the matched rules, and returns a single compiled standards payload.
metadata:
  triggers:
    files:
      - '**/*.ts'
      - '**/*.tsx'
      - '**/*.js'
      - '**/*.jsx'
      - '**/*.dart'
      - '**/*.sql'
      - '**/*.graphql'
    keywords:
      - review
      - audit
      - refactor
      - bug
      - feature
      - frontend
      - backend
      - full-stack
      - critique
      - regression
      - diff
      - react
      - nextjs
      - next.js
      - flutter
      - graphql
      - typescript
      - dart
      - prisma
      - apollo
      - migration
      - schema
      - auth
      - api
      - endpoint
      - component
      - hook
      - resolver
---

# Cook Orchestrator

Cook is the single entry point for standards. It does not hold rules of its own — it detects what a task touches and composes a payload from the rule libraries under `standards/`. There are no mode flags (`--frontend` / `--backend` / `--full-stack`); layer concerns are matched by keyword, so a task that touches both UI and server simply matches concerns and domains from both sides.

## Protocol

### Step 1 — Receive summary

Accept the code-task summary passed by the invoking agent. It describes what is being built, changed, or reviewed, and usually names files, frameworks, and intent.

### Step 2 — Detect mode

Classify the invoking agent's intent into one of two modes before proceeding:

**Review mode** — the agent wants to evaluate existing artifacts for correctness, bugs, or design gaps.
Signals: `review`, `audit`, `check for bugs`, `look for regressions`, `review this PR`, `review this diff`, `critique`, `adversarial review`.
Action: skip Steps 3–7, detect the review surface, pass it as `code_surface`, load `standards/review/SKILL.md`, and stop.

Surface detection for Review mode:

- Frontend signals: `.tsx`, `.jsx`, `components/`, `pages/`, `app/`, `hooks/`, `styles/`
- Backend signals: `controllers/`, `routes/`, `handlers/`, `services/`, `repositories/`, `db/`
- Full-stack signals: both frontend and backend files in one review target
- Security-sensitive signals: auth, token, session, role, permission, owner scope, upload, redirect, webhook, external URL

Tag the detected surface as `frontend`, `backend`, or `full-stack`. If security-sensitive signals appear, add `security-sensitive` to `code_surface` alongside the base surface, for example `full-stack, security-sensitive`.

**Inform mode** — the agent is about to create or change code/plans and needs compiled standards to guide that work.
Signals: everything else — feature requests, bug fixes, refactors, new plans, migrations, or any task that will produce new or modified artifacts.
Action: continue to Steps 3–7 to compile and return a standards payload.

### Step 3 — Extract keywords

Parse the summary into signals:

- **File paths and extensions** — `.ts`, `.tsx`, `.dart`, `.graphql`, `app/`, `pages/`, `components/`, `migrations/`, etc.
- **Framework and library names** — Next.js, React, Flutter, Riverpod, Prisma, Apollo, etc.
- **Domain terms** — `endpoint`, `auth`, `BlocProvider`, `resolver`, `migration`, etc.
- **Concern terms** — `pagination`, `re-render`, `N+1`, `error`, `validate`, `state`, `navigation`, etc.

### Step 4 — Load global P0 (always)

Load `standards/global/SKILL.md`. Its P0 universal rules apply to every code task regardless of stack.

### Step 5 — Match global concerns

Read `standards/global/_INDEX.md` and match the extracted keywords and file patterns against its **Concern Match** table. Load every concern ref (`refs/architecture.md`, `refs/api-design.md`, `refs/error-handling.md`, `refs/security.md`, `refs/performance.md`, `refs/debug.md`) whose patterns or keywords match at least one signal. These refs hold the prescriptive layer rules — UI/component, API, auth, error, and performance — folded in by topic.

### Step 6 — Detect domains and match skills/refs

Map the extracted keywords and file patterns to one or more domains. **Multiple domains may match** — e.g. a feature spanning a Next.js UI and a Postgres schema matches both `nextjs` and `database`.

| Domain | Index | Match when |
| --- | --- | --- |
| Flutter | `standards/flutter/_INDEX.md` | `**/*.dart` and Flutter terms (Widget, Bloc, Cubit, GetX, Riverpod, GoRouter, AutoRoute) |
| Next.js | `standards/nextjs/_INDEX.md` | `app/**`, `pages/**`, Next.js terms (App Router, Server Action, Server Component, middleware) |
| React | `standards/react/_INDEX.md` | `**/*.tsx`, `**/*.jsx`, React terms (component, hook, useState, useEffect) and no Next.js signal |
| Database | `standards/database/_INDEX.md` | sql, schema, migration, postgres, prisma, redis, cache, `**/*.entity.ts`, `**/migrations/*.sql` |
| GraphQL | `standards/graphql/_INDEX.md` | graphql, gql, resolver, mutation, subscription, Apollo, DataLoader, `**/*.graphql` |
| TypeScript | `standards/typescript/SKILL.md` | `**/*.ts` and no framework signal (cook bypasses the auto-generated `_INDEX.md` and loads the SKILL directly; `**/*.tsx` is excluded by design — covered by React or Next.js domains) |
| Dart | `standards/dart/_INDEX.md` | `**/*.dart` with non-Flutter Dart terms (sealed, record, pattern, extension) |

For each matched domain index, match the extracted keywords and file patterns against its rows and load the matched domain `SKILL.md` plus any matched `refs/*.md` entries. For `typescript`, load `standards/typescript/SKILL.md` directly.

### Step 7 — Compile and return

Invoke the compilation script with the path list assembled by Steps 4–6 (or from `routing.skills` on a cache hit). Single Bash call — no LLM involvement:

```
python3 scripts/cook_compile.py \
  --skills <comma-separated paths relative to cook root>
```

The script deduplicates paths, buckets them (Universal → Domain → Concern), reads each file, strips YAML frontmatter, and concatenates with terse section headers (`## Universal`, `## React`, `## Security`, etc.). Output is JSON:

```json
{
  "content": "<assembled markdown>",
  "degraded": [],
  "metadata": {"resolutions_applied": [], "dropped_for_budget": []}
}
```

Return the JSON envelope to the invoking agent. If `degraded` is non-empty, log the failed paths — the next invocation re-attempts them automatically.

**Path list construction:**
- **Cache hit:** use `routing.skills` from the resolver output directly.
- **Miss path:** collect paths from Steps 4–6: `standards/global/SKILL.md`, matched `standards/global/refs/<name>.md`, matched domain `SKILL.md` + `refs/*.md`.

## Notes

- Cook owns detection and composition only. The rules live in `global/` (universal + concern refs) and the domain folders.
- Global is one rule library among peers, not a privileged baseline that decides layers.
- When in doubt about the change surface, inspect the touched files before widening the match.
