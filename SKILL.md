---
name: cook
description: Top-level router for coding and review standards in this repository. Use to choose the correct standards skill from `standards/` based on task intent, touched files, and framework.
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

# Cook Router

## Intent Routing

- If the request intent is code review, load `standards/review/SKILL.md`.
- If the request intent is implementation or refactor, load `standards/global/SKILL.md` first.
- If the request is ambiguous, inspect the task summary and touched files before loading more skills.

## Review Triggers

Load `standards/review/SKILL.md` for prompts such as:

- `review this`
- `review this PR`
- `review this diff`
- `audit this code`
- `look for bugs`
- `check for regressions`

## Coding Triggers

After `standards/global/SKILL.md`, load the matching standards family:

- `standards/global/_INDEX.md` for cross-cutting coding rules plus frontend, backend, or full-stack mode routing
- `standards/dart/_INDEX.md` for `.dart`
- `standards/typescript/SKILL.md` for `.ts` and `.tsx`
- `standards/react/` for React-specific files and patterns
- `standards/nextjs/` for Next.js app or routing work
- `standards/flutter/` for Flutter code
- `standards/database/` for SQL, schema, or database work
- `standards/graphql/SKILL.md` for GraphQL schema or resolver work

## Notes

- The review skill loads other standards after it classifies the code surface.
- The global skill is the coding baseline, not the review persona.
