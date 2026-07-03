---
name: cook
description: Keyword-driven orchestrator for this repository's coding standards. Receives a code-task summary from the invoking agent, extracts keywords, matches them against the global concern index and the relevant domain indexes, loads only the matched rules, and returns a single compiled standards payload.
metadata:
  triggers:
    files:
      - '**/*.ts'
      - '**/*.tsx'
      - '**/*.js'
      - '**/*.jsx'
      - '**/*.cjs'
      - 'server.{ts,js,mjs,cjs}'
      - 'app.{ts,js,mjs,cjs}'
      - '**/*.server.{ts,js,mjs,cjs}'
      - '**/*.dart'
      - '**/*.sql'
      - '**/*.graphql'
      - 'supabase/**'
    keywords:
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
      - node
      - nodejs
      - node.js
      - dart
      - supabase
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

**Before doing anything, read [`refs/protocol-cook.md`](refs/protocol-cook.md) and follow it exactly.** It holds the mode branch table and Steps 0–6 — the complete operational protocol. Do not act on this skill without it; the protocol is mandatory, not a reference aside.
