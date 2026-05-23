# Architecture

## Overview

Cook is a keyword-driven standards orchestrator. A calling agent passes a task summary; cook classifies the intent, extracts signals, and compiles a single standards payload from the matching rule libraries under `standards/`.

```
SKILL.md (cook)
└── standards/
    ├── global/          universal rules + concern refs
    ├── review/          adversarial review skill
    ├── flutter/         Flutter/Dart UI
    ├── dart/            Dart 3 language
    ├── nextjs/          Next.js App Router
    ├── react/           React (non-Next)
    ├── typescript/      TypeScript 5 language
    ├── database/        PostgreSQL + Redis
    └── graphql/         GraphQL schema + resolvers
```

---

## Skills

| Skill | Description |
|---|---|
| cook | Entry-point orchestrator: classifies intent (review vs inform), extracts keywords, and composes a standards payload from matched domain skills and global refs. |
| global | Universal P0 rules that apply to every task regardless of stack; concern refs are loaded on top by cook. |
| review | Adversarial review that detects bugs, design gaps, and security risks by loading matching coding standards; offers auto-fix or eval-report output. |
| flutter | Flutter/Dart UI standards covering widgets, state management, navigation, architecture, performance, and testing. |
| dart | Dart 3.x language standards: null safety, patterns, sealed classes, records, class modifiers, naming, immutability, collections, async, and import organisation. |
| nextjs | Next.js App Router standards: RSC boundaries, server data access, async route APIs, Server Actions, rendering/cache strategy, and Pages Router awareness. |
| react | React + TypeScript standards: hook rules, component structure, prop typing, and boundary safety for non-Next.js projects. |
| typescript | TypeScript 5.x language standards: type safety, narrowing, generics, modules, and async code. |
| database | Database standards for PostgreSQL schema/migration/query design and Redis caching and cache invalidation. |
| graphql | GraphQL schema design and resolver conventions: naming, nullability, types, input objects, mutations, queries, and operation structure. |

---

## Refs

### global

- `refs/architecture.md`: Component and state structure rules across layers.
- `refs/api-design.md`: HTTP verb semantics, status codes, request/response shape.
- `refs/error-handling.md`: Error architecture, propagation, and user-facing error design.
- `refs/security.md`: UI, API, and auth security rules.
- `refs/performance.md`: Performance workflow and profiling discipline.
- `refs/debug.md`: Scientific debugging method and instrumentation rules.

### review

- `refs/report-format.md`: Output format, vibecoder field guidance, and severity reference for review reports.
- `refs/review-lenses.md`: Correctness, Security, and Reliability lenses applied during review.

### flutter

- `refs/architecture.md`: Layer separation and feature-first folder structure.
- `refs/cicd.md`: CI/CD pipeline and release configuration.
- `refs/concurrency.md`: Isolates, async, and stream concurrency rules.
- `refs/dependency-injection.md`: DI patterns and service locator conventions.
- `refs/design-system.md`: Design tokens, theming, and widget composition.
- `refs/error-handling.md`: Error propagation and user-facing error handling in Flutter.
- `refs/localization.md`: i18n and l10n setup and ARB file conventions.
- `refs/navigation.md`: GoRouter / AutoRoute patterns and deep-link handling.
- `refs/networking.md`: HTTP client setup, interceptors, and retry strategy.
- `refs/notifications.md`: Push notification setup and permission handling.
- `refs/security.md`: Secure storage, certificate pinning, and obfuscation.
- `refs/state-management.md`: Bloc/Cubit, Riverpod, and GetX conventions.
- `refs/testing.md`: Unit, widget, and integration test conventions.

### dart

- `refs/testing.md`: Dart test conventions and coverage rules.
- `refs/tooling.md`: Dart toolchain, linter, and formatter configuration.

### nextjs

- `refs/app-router.md`: App Router file conventions, layouts, and route handlers.
- `refs/architecture.md`: Project structure and layer boundaries for Next.js apps.
- `refs/data-fetching.md`: Data fetching patterns: fetch, cache, revalidation.
- `refs/i18n.md`: Internationalisation setup for App Router.
- `refs/pages-router.md`: Legacy Pages Router patterns and migration notes.
- `refs/rendering-and-caching.md`: Static, dynamic, and streaming rendering; cache semantics.
- `refs/security.md`: Next.js-specific security: headers, CSRF, server boundary leaks.
- `refs/server-actions.md`: Server Action conventions, validation, and error handling.
- `refs/server-components.md`: RSC rules: data access, serialisation, and client boundary placement.
- `refs/state-management.md`: Client-side state patterns compatible with RSC.
- `refs/styling-and-optimization.md`: CSS Modules, Tailwind, fonts, images, and bundle optimisation.
- `refs/testing.md`: Next.js testing: unit, component, and E2E conventions.
- `refs/tooling.md`: Next.js toolchain: ESLint, TypeScript, and build configuration.

### react

- `refs/component-patterns.md`: Component composition, slot patterns, and API design.
- `refs/hooks.md`: Custom hook rules, dependency arrays, and effect discipline.
- `refs/performance.md`: Memoisation, code splitting, and render optimisation.
- `refs/security.md`: XSS prevention and safe DOM interaction in React.
- `refs/state-management.md`: Local, context, and external store patterns.
- `refs/testing.md`: React Testing Library conventions and coverage rules.
- `refs/tooling.md`: Vite, ESLint, and React toolchain configuration.

### typescript

- `refs/security.md`: Type-safe input validation and injection prevention.
- `refs/testing.md`: TypeScript test patterns and type-level testing.
- `refs/tooling.md`: tsconfig, strict mode, and compiler flag conventions.

### database

- `refs/postgresql-best-practices.md`: Schema design, constraints, and indexing best practices.
- `refs/postgresql-anti-patterns.md`: Common PostgreSQL mistakes and how to avoid them.
- `refs/postgresql-checklist.md`: Pre-migration and pre-deploy checklist for schema changes.
- `refs/postgresql-implementation.md`: Concrete implementation patterns: transactions, CTEs, batch writes.
- `refs/redis-best-practices.md`: Key design, TTL strategy, and data structure selection.
- `refs/redis-checklist.md`: Pre-deploy checklist for Redis usage.
- `refs/sql-gotchas.md`: SQL edge cases: NULL semantics, type coercion, lock behaviour.

### graphql

- `refs/schema-design.md`: Type naming, nullability defaults, and field design rules.
- `refs/performance.md`: DataLoader usage, query complexity limits, and N+1 prevention.
- `refs/security.md`: Depth limits, introspection policy, and auth on resolvers.
- `refs/testing.md`: Schema and resolver testing conventions.
- `refs/tooling.md`: Code generation, linting, and GraphQL toolchain setup.
