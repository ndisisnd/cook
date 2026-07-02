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

Default load: this file only. Pull `refs/concurrency.md`, `refs/memory-management.md`, `refs/testing.md`, `refs/tooling.md`, `refs/performance.md`, or `refs/interop.md` only when the task needs that depth.

Swift owns language-level correctness only: optionals, errors, concurrency semantics, value/reference types, protocols and generics, ARC, naming, access control. Platform and app-shape concerns — scenes/windows, SwiftUI architecture, sandboxing, distribution, persistence, localization — live in `standards/macos/`. Universal rules stay in `standards/global/`.

**Scope:** these rules apply in full to new targets and modules. In existing code, match established conventions; propose migrations (language mode, `ObservableObject` → `@Observable`, deployment targets, dependency swaps) as separate explicit tasks — never as a side effect of a feature change.

## Priority: P0 — Language Correctness

### Language Mode & Isolation Defaults
- New app/executable targets: Swift 6 language mode + Approachable Concurrency + default `MainActor` isolation. The latter two are current Xcode template defaults; the template leaves the language mode at Swift 5 — set `SWIFT_VERSION` to 6 explicitly. Single-threaded by default; move work off-main explicitly.
- Library/package targets: Swift 6 mode with `nonisolated` default isolation — never MainActor-bind a networking or domain package.
- Migrate existing modules one at a time (strict checking minimal → targeted → complete), never one big flip. `@preconcurrency import` is a documented temporary bridge — it silences, it doesn't fix. Detail → `refs/concurrency.md`.

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
- A struct holding a class reference does not have value semantics — enforce COW or don't pretend.
- Stdlib collections (`Array`, `Dictionary`, `Set`, `String`) are copy-on-write — assignment is a cheap pointer copy, duplicated only on the next mutation of a shared buffer. Don't hand-roll defensive copies of them "to be safe"; implement custom COW (private reference backing + `isKnownUniquelyReferenced`) only for a large custom buffer where copy cost is measured to matter.

### Concurrency
- Prefer structured concurrency: `async let` for a fixed few parallel ops, `TaskGroup` for dynamic fan-out. Unstructured `Task {}` needs an owner and a cancellation story; `Task.detached` almost never (only to escape actor context, priority, and task-locals at once).
- Mark CPU-heavy functions `@concurrent` to hop off the caller's actor explicitly; under Approachable Concurrency, `nonisolated async` inherits the caller's actor.
- Cancellation is cooperative: long loops call `try Task.checkCancellation()`; in SwiftUI prefer `.task {}` (auto-cancelled) over stored handles.
- Don't reach for `actor` by default — most state belongs on `@MainActor` or in value types. But when state is genuinely shared and mutated across concurrent, suspending contexts, an `actor` is the standard tool, not a failure. `Mutex` (Synchronization, macOS 15+) or `OSAllocatedUnfairLock` (macOS 13+) for small synchronous critical sections — pick per deployment target.
- Actor reentrancy: state can change across every `await` — re-validate invariants after suspension; never split check-and-mutate across a suspension point.
- Make types `Sendable` by design — internal value types of Sendable properties get it implicitly, but `public` library types must declare it (implicit conformance stops at module boundaries except `@frozen`). `@unchecked Sendable` and `nonisolated(unsafe)` require an internal synchronization mechanism plus a justification comment.
- Continuations resume exactly once on every path; use `withCheckedContinuation` variants; never store a continuation beyond its scope. Detail → `refs/concurrency.md`.
- No GCD as concurrency architecture: no `DispatchQueue.main.async` in async contexts (use actor isolation / `MainActor.run`), no semaphores bridging sync→async, no queues guarding state. Exception: next-runloop-tick deferral in synchronous AppKit paths remains legitimate.
- New code uses AsyncSequence/AsyncStream + Observation, not Combine (maintenance-mode, predates Sendable). Bridge existing pipelines with `.values`; don't mix paradigms in one flow.
- `deinit` is nonisolated — never touch actor-isolated state there; use `isolated deinit` where available, or move cleanup to an explicit `invalidate()`/task cancellation called before release.

### Memory Management
- Delegates are `weak`, and delegate protocols are `AnyObject`-constrained.
- `unowned` only when the referenced object provably outlives the reference; when in doubt, `weak`. Accessing a deallocated `unowned` reference traps deterministically — `unowned(unsafe)` is genuine UB, never reach for it.
- `[weak self]` where a real cycle or unwanted lifetime extension exists — not reflexively. Needed: closures stored on `self` (handlers, observers, subscriptions), indefinite `Task` bodies (`for await` loops), task handles stored on `self`. Not needed: non-escaping closures; finite `Task {}` bodies where extending `self` until completion is correct. Prefer cancelling tasks as the primary lifetime tool.
- Invalidate `Timer`s (they retain targets); remove block-based NotificationCenter observers explicitly. Detail → `refs/memory-management.md`.

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

### Naming (Swift API Design Guidelines)
- Clarity at the point of use; omit needless words; name by role, not type.
- Side-effect-free reads as noun (`sorted()`, `distance(to:)`); side-effecting reads as verb (`sort()`, `append(_:)`). Booleans read as assertions (`isEmpty`, `canSend`).
- Protocols: nouns for is-a (`Collection`); `-able`/`-ible`/`-ing` for capability (`Equatable`).
- First argument label: omit when the call reads as a grammatical phrase (`addSubview(x)`) or for value-preserving conversions (`Int64(int32)`); include prepositions (`move(from:to:)`).
- `UpperCamelCase` types/protocols; `lowerCamelCase` everything else; acronyms uniformly cased (`urlString`, `userID`).

### Structure
- One protocol conformance per `extension`, marked with `// MARK: -`. Keep core stored properties and initializers in the primary declaration.
- Trailing-closure syntax for the final closure; implicit `return` in single-expression bodies.
- `map`/`compactMap`/`filter` when they read clearly; loops when they don't (or when the body needs `break`/`continue`/`return`). `first(where:)` over `filter {}.first`; `contains(where:)` over `filter {}.count > 0`.
- Prefer interpolation over concatenation; raw strings (`#"..."#`) to avoid escaping; multiline literals (`"""`) for embedded text.
- Property wrappers only for reusable cross-cutting storage behavior — not as a substitute for a plain computed property. Author a custom `@resultBuilder` only for a genuine declarative DSL, not to avoid an array literal.
- Omit `self.` except where required (or where the team formatter enforces otherwise).

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

Load only what the current task requires:

- [concurrency](refs/concurrency.md) — Swift 6 migration mechanics, actors and reentrancy, `Sendable`/`sending`, structured vs unstructured tasks, `AsyncSequence`/`AsyncStream`, continuation/callback bridging; keywords: Sendable, data race, strict concurrency, continuation, AsyncStream, actor, isolation
- [memory-management](refs/memory-management.md) — ARC model, `weak`/`unowned` decision-making, delegate and parent/child patterns, retain-cycle sources (timers, `NotificationCenter`, stored closures), diagnosing with the Memory Graph Debugger; keywords: ARC, retain cycle, weak, unowned, deinit, Timer, leak
- [testing](refs/testing.md) — Swift Testing (`@Test`/`#expect`/`#require`, parameterized tests, traits), what stays XCTest, protocol-based fakes, async test patterns, migration mapping; files under `**/Tests/**`, `**/*Tests.swift`; keywords: Swift Testing, #expect, #require, XCTest, parameterized, coverage
- [tooling](refs/tooling.md) — SwiftLint + swift-format setup and CI enforcement, SPM/`Package.resolved` hygiene, Xcode build settings, CI ordering; files matching `Package.swift`, `Package.resolved`, `.swiftlint.yml`, `.swift-format`, `.github/workflows/**`; keywords: SwiftLint, swift-format, SPM, Package.resolved, xcodebuild, build settings
- [performance](refs/performance.md) — existential boxing vs generics, ARC traffic, string/collection processing costs, devirtualization, WMO, type-checker build-time hygiene, Instruments/OSSignposter/MetricKit workflow; keywords: performance, Instruments, existential, slow build, type-checker, OSSignposter, MetricKit
- [interop](refs/interop.md) — C/Obj-C/CoreFoundation: CF ownership (`takeRetainedValue` vs `takeUnretainedValue`), pointer lifetime rules, nullability audits, `@objc`/`dynamic` discipline, block-based KVO; keywords: CoreFoundation, Unmanaged, takeRetainedValue, UnsafePointer, bridging header, @objc, KVO
