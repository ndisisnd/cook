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

Cook turns a code task into one standards payload. It holds no rules itself. It detects what the task touches and compiles rules from `standards/`.

Run one command:

```
python3 scripts/cook_run.py --project <dir> --task "<task summary>"
```

Read the JSON envelope it prints:

- `needs_llm: true`: pick tags from the `llm_input.vocab` file, never invent one. Run `cook_run.py --resume <fingerprint> --tags a,b`. If `platform_ambiguous` is true, add `ios` or `macos` only when the task says which.
- Otherwise the run is done.

Return the envelope. Never inline the payload; the invoker reads the payload file.

`/cook` args or a telemetry flag (`--init`, `--status`...): read [`refs/protocol-cook.md`](refs/protocol-cook.md) first.
The step-by-step flow for a model that cannot run the script is [`refs/protocol-manual.md`](refs/protocol-manual.md).
