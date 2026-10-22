---
name: swift
description: Swift 6.x language standards and code quality conventions. Use when writing or reviewing any Swift code — optionals, error handling, concurrency (actors, Sendable, @MainActor), value types, protocols and generics, memory management, naming, and access control.
metadata:
  triggers:
    files:
      - '**/*.swift'
    keywords:
      - Sendable
      - MainActor
      - actor isolation
      - Swift concurrency
      - async let
      - TaskGroup
      - structured concurrency
      - continuation
      - guard let
      - force unwrap
      - opaque type
      - existential
      - typed throws
      - Codable
      - weak self
      - unowned
      - retain cycle
      - Swift Testing
      - SwiftLint
  targets: "Swift 6.2+ · Swift 6 language mode · Xcode 27 (Swift 6.4 notes)"
  last_reviewed: 2026-10-18
---

# Swift Standards

Target: Swift 6.2+ in Swift 6 language mode, built with Xcode 27 (Swift 6.4 features flagged where used). Default load: this file only.

Swift owns language-level correctness only: optionals, errors, concurrency, value/reference types, protocols, generics, ARC, naming, access control. Scenes, SwiftUI architecture, sandboxing, distribution, persistence, localization → `standards/ios/` or `standards/macos/`; universal rules → `standards/global/`.

**Scope:** full force for new targets. In existing code, match conventions; propose migrations (language mode, `ObservableObject` → `@Observable`, deployment targets, dependency swaps) as separate tasks.

## Priority: P0 — Language Correctness

### Language Mode, Isolation & Concurrency

- New targets: Swift 6 language mode. Apps default to `MainActor` isolation; library/domain packages stay `nonisolated`. Check the module's default before reasoning about a bare declaration.
- Structured concurrency first. Every unstructured `Task {}` has a cancelling owner; `Task.detached` almost never.
- CPU-heavy work is `@concurrent`; under Approachable Concurrency `nonisolated async` runs on the caller's actor.
- Re-validate actor state after every `await`. Small sync critical sections use `Mutex` or `OSAllocatedUnfairLock`, not an actor.
- `@unchecked Sendable` / `nonisolated(unsafe)` only with a lock and a justification comment. Continuations resume exactly once.
- No GCD or Combine as architecture — the only allowed uses are the exception list in `refs/concurrency.md`.

Full rules, Swift 6.4 additions → `refs/concurrency.md`.

### Availability
- Gate every API newer than the deployment target with `if #available` / `@available` and a real fallback. Never raise the target to dodge a check.

### Optionals
- Never force-unwrap (`!`) or force-cast (`as!`) in production paths. For a true non-nil invariant, use `guard let x else { preconditionFailure("why") }`.
- No implicitly unwrapped optionals (`T!`) in new pure-Swift code; only `@IBOutlet` and Obj-C bridging.
- `guard let` for early exit; `if let` for genuine branching; use shorthand (`if let user`).
- Prefer `??` and optional chaining over `if x != nil` then `x!`.
- Return empty collections, not optionals, unless nil is meaningful.

### Error Handling
- Untyped `throws` is the default. Typed throws (`throws(E)`) only for closed error domains in libraries, generic error propagation (a typed alternative to `rethrows`), and measured hot paths — typed errors become breaking changes.
- Never `try!` outside tests. `try?` only when nil is acceptable, never to discard an error that matters. Throw; don't return `nil` for failure.
- `Result` only for storing an error or crossing a non-throwing boundary, not instead of `throws`.
- Domain errors are enums/structs with associated values; user-facing ones are `LocalizedError`.
- Use `defer` for cleanup that must run on every exit path, including thrown errors. `defer` for cleanup that must run on every exit path.

### Value Types First
- Default to `struct`/`enum`; `class` only for identity, shared mutable state, deinit-based lifetime, or framework/Obj-C interop.
- `final` classes unless subclassing is designed. Prefer `let` over `var`.
- A struct holding a class reference does not have value semantics — enforce COW or don't pretend. COW mechanics → `refs/performance.md`.

### Memory Management

P0 rules → `refs/memory-management.md` (delegates, closures, timers, tasks).

### Protocols & Generics
- Prefer concrete types → `some` → `any`. Never `any` where `some` compiles.
- Constrain generics tightly (`<T: Equatable>`); never an unconstrained `<T>` that force-casts.
- Don't extract a protocol until there are ≥2 real conformers or a genuine test seam; struct-of-closures dependencies are a valid alternative.
- Protocol-extension methods that aren't requirements dispatch statically; declare customization points as requirements.

### Enums & Type Safety
- Switch exhaustively over your own enums — avoid `default` so the compiler flags new cases; `@unknown default` for non-frozen SDK enums.
- No stringly-typed APIs (use enums, `Notification.Name`, key paths); no `Any`/`AnyObject` across module boundaries.
- Codable: never force-decode data crossing a trust boundary (network, user files, IPC). Rest → `refs/language-conventions.md`.

### Access Control
- Least access first: `private` → `internal` → `package` → `public`/`open` (`open` only when external subclassing is a supported contract).
- `private(set)` for externally-read-only state. Avoid `fileprivate`.
- Library code: explicit access modifier and `///` doc on every public declaration.

## Priority: P1 — Style & Conventions

P1 rules → `refs/language-conventions.md` (authoring APIs, naming/structure/style).

## Anti-Patterns

- Blanket `[weak self]`, or missing it on stored/long-running closures; `unowned(unsafe)` ever
- God singletons (`Shared.instance`): inject; `static let shared` only for stateless system facades (`URLSession.shared`)
- `NotificationCenter` as an app-internal event bus; `print()`/`NSLog` in production (use `os.Logger`)

## References

Load only what the task requires:
- [concurrency](refs/concurrency.md) — P0 isolation, Swift 6 migration, actors, Sendable
- [memory-management](refs/memory-management.md) — P0 ARC, retain cycles
- [language-conventions](refs/language-conventions.md) — P1 naming, style, Codable
- [testing](refs/testing.md) — Swift Testing, XCTest
- [tooling](refs/tooling.md) — SwiftLint, swift-format, SPM, CI
- [performance](refs/performance.md) — existentials, ARC traffic, COW
- [interop](refs/interop.md) — C/Obj-C/CF, pointers, KVO
