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
      - '**/*.go'
      - '**/*.java'
      - '**/*.kt'
      - '**/*.swift'
      - '**/*.py'
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
---

# Cook Orchestrator

Cook is the single entry point for standards. It does not hold rules of its own — it detects what a task touches and composes a payload from the rule libraries under `standards/`. There are no mode flags (`--frontend` / `--backend` / `--full-stack`); layer concerns are matched by keyword, so a task that touches both UI and server simply matches concerns and domains from both sides.

## Protocol

### Step 1 — Receive summary

Accept the code-task summary passed by the invoking agent. It describes what is being built, changed, or reviewed, and usually names files, frameworks, and intent.

### Step 2 — Detect review intent

If the summary signals review — keywords `review`, `audit`, `check for bugs`, `look for regressions`, `review this PR`, `review this diff` — skip Steps 3–7 and load `standards/review/SKILL.md`. The review skill classifies the code surface itself. Stop here.

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

### Step 6 — Detect domains and match sub-skills

Map the extracted keywords and file patterns to one or more domains. **Multiple domains may match** — e.g. a feature spanning a Next.js UI and a Postgres schema matches both `nextjs` and `database`.

| Domain | Index | Match when |
| --- | --- | --- |
| Flutter | `standards/flutter/_INDEX.md` | `**/*.dart` and Flutter terms (Widget, Bloc, Cubit, GetX, Riverpod, GoRouter, AutoRoute) |
| Next.js | `standards/nextjs/_INDEX.md` | `app/**`, `pages/**`, Next.js terms (App Router, Server Action, Server Component, middleware) |
| React | `standards/react/_INDEX.md` | `**/*.tsx`, `**/*.jsx`, React terms (component, hook, useState, useEffect) and no Next.js signal |
| Database | `standards/database/_INDEX.md` | sql, schema, migration, postgres, prisma, redis, cache, `**/*.entity.ts`, `**/migrations/*.sql` |
| GraphQL | `standards/graphql/_INDEX.md` | graphql, gql, resolver, mutation, subscription, Apollo, DataLoader, `**/*.graphql` |
| TypeScript | `standards/typescript/SKILL.md` | `**/*.ts` and no framework signal (load the SKILL directly — no index) |
| Dart | `standards/dart/_INDEX.md` | `**/*.dart` with non-Flutter Dart terms (sealed, record, pattern, extension) |

For each matched domain index, match the extracted keywords and file patterns against its rows and load every matched sub-skill `SKILL.md`. For `typescript`, load `standards/typescript/SKILL.md` directly.

### Step 7 — Compile and return

Assemble everything loaded — global P0 + matched global concern refs + matched domain sub-skills — into a single standards payload and return it to the invoking agent.

## Notes

- Cook owns detection and composition only. The rules live in `global/` (universal + concern refs) and the domain folders.
- Global is one rule library among peers, not a privileged baseline that decides layers.
- When in doubt about the change surface, inspect the touched files before widening the match.
