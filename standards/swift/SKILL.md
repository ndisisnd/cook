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
---

# Swift Standards

Default load: this file only; pull refs (see References) on demand.

Swift owns language-level correctness only: optionals, errors, concurrency semantics, value/reference types, protocols and generics, ARC, naming, access control. Platform and app-shape concerns — scenes/windows, SwiftUI architecture, sandboxing, distribution, persistence, localization — live in `standards/macos/`. Universal rules stay in `standards/global/`.

**Scope:** these rules apply in full to new targets and modules. In existing code, match established conventions; propose migrations (language mode, `ObservableObject` → `@Observable`, deployment targets, dependency swaps) as separate explicit tasks — never as a side effect of a feature change.

## Priority: P0 — Language Correctness

### Language Mode, Isolation & Concurrency

P0 rules → `refs/concurrency.md` — load for any concurrency, isolation, or language-mode task.

### Availability
- Gate every API newer than the deployment target with `if #available` / `@available` and a real fallback path. Annotate declarations rather than sprinkling runtime checks. Never raise the deployment target to dodge a check.

### Optionals
- Never force-unwrap (`!`) or force-cast (`as!`) in production paths. If non-nil is a true invariant, use `guard let x else { preconditionFailure("why") }` so failure carries a message.
- No implicitly unwrapped optionals (`T!`) in new pure-Swift code; acceptable only for UI-lifecycle objects (`@IBOutlet`) and Obj-C bridging.
- `guard let` for early-exit preconditions (happy path stays unindented); `if let` for genuine branching. Use shorthand: `if let user`, `guard let self`.
- Prefer `??` and optional chaining; never `if x != nil` followed by `x!`.
- Return empty collections, not optional collections, unless nil vs empty is semantically meaningful.

### Error Handling
- Untyped `throws` is the default. Typed throws (`throws(E)`) only for closed error domains in libraries, generic error propagation (a typed alternative to `rethrows`), and measured hot paths — error domains grow, and typed errors become breaking changes.
- Never `try!` outside tests. `try?` only when nil is a genuinely acceptable outcome — never to discard an error that matters. Don't return `nil` to signal failure — throw.
- `Result` is for storing an error or crossing a non-throwing boundary — not a general replacement for `throws`. Convert with `Result(catching:)` / `.get()`.
- Domain errors are enums/structs with associated values; user-facing errors conform to `LocalizedError`, separating user message from debug detail.
- Use `defer` for cleanup that must run on every exit path, including thrown errors.

### Value Types First
- Default to `struct`/`enum`. Use `class` only for identity (`===`), shared mutable state, deinit-based resource lifetime, or framework/Obj-C interop.
- Mark classes `final` unless subclassing is a designed contract. Prefer `let` over `var` everywhere.
- A struct holding a class reference does not have value semantics — enforce COW or don't pretend. COW mechanics and custom-COW rules → `refs/performance.md`.

### Memory Management

P0 rules → `refs/memory-management.md` — load when writing delegates, stored closures, timers, or long-lived tasks.

### Protocols & Generics
- Prefer, in order: concrete types → `some` (opaque/generics) → `any` (existentials). Never `any` where `some` compiles.
- Use primary associated types (`some Collection<String>`) to constrain opaque and existential types.
- Constrain generic parameters as tightly as the implementation needs (`<T: Equatable>`), never an unconstrained `<T>` that force-casts internally.
- Don't extract a protocol until there are ≥2 real conformers or a genuine test seam; struct-of-closures dependencies are a valid alternative for seams.
- Protocol-extension methods that aren't requirements are statically dispatched — declare customization points as protocol requirements.

### Enums & Type Safety
- Switch exhaustively over your own enums — avoid `default` so the compiler flags new cases; `@unknown default` for non-frozen SDK enums.
- No stringly-typed APIs: enums, `Notification.Name` constants, key paths, and typed wrappers over raw strings/dictionaries. No `Any`/`AnyObject` payloads crossing module boundaries.
- Codable: synthesized conformance + `CodingKeys`; set strategies on the encoder/decoder, don't hand-write keys; manual `init(from:)` only for versioned/polymorphic payloads; keep wire DTOs separate from domain models; never force-decode data crossing a trust boundary (network, user files, IPC) — compile-time-bundled resources may instead fail fast with a message.

### Access Control
- Least access first: `private` → `internal` → `package` (cross-module within a package) → `public`/`open` (`open` only when external subclassing is a supported contract).
- `private(set)` for externally-read-only state. Avoid `fileprivate`.
- Library code: explicit access modifier and `///` doc comment on every public declaration.

---

## Priority: P1 — Style & Conventions

P1 rules → `refs/language-conventions.md` — load when authoring APIs or reviewing naming/structure/style.

---

## Anti-Patterns

- `!`, `as!`, `try!` outside tests; IUO stored properties in new code
- `try?` to discard errors that matter; returning `nil` to signal failure
- `DispatchQueue.main.async` / semaphores / GCD state-queues inside async code
- `Task.detached` as a habit; fire-and-forget `Task {}` sprawl with no cancellation
- `@unchecked Sendable` / `nonisolated(unsafe)` without a lock and a justification comment
- Blanket `[weak self]` everywhere — or missing it on stored/long-running closures
- `unowned` where lifetime is not provable; `unowned(unsafe)` ever
- Actors wrapping trivial state; check-then-mutate split across `await`
- Introducing Combine in new code; mixing Combine and structured concurrency in one flow
- Protocols with one conformer; `any` where `some` compiles; unconstrained `<T>` that force-casts internally
- Non-`final` classes with no subclassing design; `class` where a `struct` would do
- Stringly-typed identifiers; `Any` in public signatures; dictionary-shaped models
- God singletons (`Shared.instance` service locators) — initializer/environment injection; `static let shared` only for stateless system facades (`URLSession.shared`)
- `NotificationCenter` as an app-internal event bus
- Unguarded use of APIs newer than the deployment target
- `print()`/`NSLog` in production — use `os.Logger` with privacy annotations

---

## References

Load only what the task requires:

- [concurrency](refs/concurrency.md) — P0 concurrency + isolation rules, Swift 6 migration, actors/reentrancy, Sendable, tasks, AsyncStream, continuations
- [memory-management](refs/memory-management.md) — P0 ARC rules, weak/unowned, retain-cycle sources, leak diagnosis
- [language-conventions](refs/language-conventions.md) — P1 naming (API Design Guidelines) and structure/style conventions
- [testing](refs/testing.md) — Swift Testing, XCTest boundaries, fakes, async test patterns
- [tooling](refs/tooling.md) — SwiftLint, swift-format, SPM hygiene, build settings, CI ordering
- [performance](refs/performance.md) — existential boxing, ARC traffic, COW, collection costs, Instruments
- [interop](refs/interop.md) — C/Obj-C/CF ownership, pointer lifetimes, `@objc` discipline, KVO
