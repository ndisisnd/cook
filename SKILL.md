---
name: cook
description: React, Next.js, Flutter, Swift, iOS, macOS, TypeScript, Node.js, SQL, PostgreSQL, Supabase, GraphQL and CSS coding standards for refactor, audit, bug fix, feature and code review work — this keyword-driven orchestrator receives a code-task summary from the invoking agent, extracts keywords, matches them against the global concern index and the relevant domain indexes, loads only the matched rules, and returns a single compiled standards payload.
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

**Before doing anything, read [`refs/protocol-cook.md`](refs/protocol-cook.md) and follow it exactly.** In short: run `scripts/cook_run.py` once, branch on `needs_llm` (if true, canonicalise tags and run it again with `--resume`), and return the envelope. Never inline the payload. When the invocation carries flags or prose, the protocol directs you to [`refs/protocol-explicit.md`](refs/protocol-explicit.md) to parse them. Codex and humans can follow the step-by-step flow in [`refs/protocol-manual.md`](refs/protocol-manual.md). The protocol is mandatory, not a reference aside.
