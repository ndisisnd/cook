---
name: global
description: Universal coding principles for any implementation task across frontend and backend. Use when writing, refactoring, or reviewing code that needs shared rules for simplicity, design, safety, error handling, and performance.
metadata:
  triggers:
    files:
      - '**/*.ts'
      - '**/*.tsx'
      - '**/*.js'
      - '**/*.jsx'
      - '**/*.go'
      - '**/*.dart'
      - '**/*.java'
      - '**/*.kt'
      - '**/*.swift'
      - '**/*.py'
    keywords:
      - dry
      - kiss
      - solid
      - refactor
      - clean code
      - readability
      - naming
      - error handling
      - security
      - performance
---

# Global Standards

## Priority: P0 - Universal Rules

### Core Design Principles
- Apply `SOLID`, especially Single Responsibility: each function, component, class, or service should have one clear reason to change.
- Apply `KISS`: choose the simplest design that solves the current problem correctly.
- Apply `DRY`: remove repeated logic when the duplication is real and stable, not accidental similarity.
- Apply `YAGNI`: do not add abstraction, configurability, or extension points without a present need.

### Readability and Structure
- Prefer intention-revealing names. A reader should understand purpose without decoding abbreviations.
- Keep units focused and small enough to reason about quickly. Split code when one unit starts mixing unrelated responsibilities.
- Prefer guard clauses and early returns over deep nesting.
- Prefer explicit data flow over hidden side effects.
- Comments should explain why, constraints, or non-obvious tradeoffs, not restate what the code already says.

### Correctness and Safety
- Validate and sanitize untrusted input at every boundary.
- Handle errors explicitly. Never swallow exceptions or return failures that hide the cause.
- Add context when propagating errors so failures are diagnosable.
- Never hardcode secrets, tokens, or credentials.
- Never leak sensitive data or internal stack details to users, clients, or logs.

### State and Side Effects
- Avoid global mutable state. Prefer explicit ownership, dependency injection, or local state.
- Keep side effects at clear boundaries; separate pure logic from I/O where practical.
- Clean up owned resources such as subscriptions, listeners, timers, streams, or connections.

### Performance Discipline
- Measure before optimizing. Fix proven bottlenecks, not hypothetical ones.
- Avoid obviously expensive patterns in hot paths, especially repeated work inside loops, unnecessary re-renders, redundant fetches, and N+1-style access patterns.
- Prefer predictable, maintainable performance wins over clever micro-optimizations.

### Change Quality
- Remove dead code, temporary debugging code, and stale fallbacks before finishing a change.
- Cover changed logic and important edge cases with the appropriate verification for the codebase.
- Keep behavior, naming, and structure consistent with the existing project unless there is a clear reason to improve them.

## Anti-Patterns

- Clever code that obscures intent
- Large units that mix multiple responsibilities
- Deep nesting instead of guard clauses
- Duplicated business logic across files or layers
- Swallowed errors or context-free failures
- Hardcoded secrets or sensitive data in logs
- Hidden mutable shared state
- Premature optimization without measurement
- Leaving debug code or dead code in production paths
