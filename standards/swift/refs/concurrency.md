# Swift Concurrency

## Core Rules (P0)

### Language Mode & Isolation Defaults
- New app/executable targets: Swift 6 language mode + Approachable Concurrency + default `MainActor` isolation. The latter two are current Xcode template defaults; the template leaves the language mode at Swift 5 — set `SWIFT_VERSION` to 6 explicitly. Single-threaded by default; move work off-main explicitly.
- Library/package targets: Swift 6 mode with `nonisolated` default isolation — never MainActor-bind a networking or domain package.
- Migrate existing modules one at a time (strict checking minimal → targeted → complete), never one big flip. `@preconcurrency import` is a documented temporary bridge — it silences, it doesn't fix.

### Concurrency
- Prefer structured concurrency: `async let` for a fixed few parallel ops, `TaskGroup` for dynamic fan-out. Unstructured `Task {}` needs an owner and a cancellation story; `Task.detached` almost never (only to escape actor context, priority, and task-locals at once).
- Mark CPU-heavy functions `@concurrent` to hop off the caller's actor explicitly; under Approachable Concurrency, `nonisolated async` inherits the caller's actor.
- Cancellation is cooperative: long loops call `try Task.checkCancellation()`; in SwiftUI prefer `.task {}` (auto-cancelled) over stored handles.
- Don't reach for `actor` by default — most state belongs on `@MainActor` or in value types. But when state is genuinely shared and mutated across concurrent, suspending contexts, an `actor` is the standard tool, not a failure. `Mutex` (Synchronization, macOS 15+) or `OSAllocatedUnfairLock` (macOS 13+) for small synchronous critical sections — pick per deployment target.
- Actor reentrancy: state can change across every `await` — re-validate invariants after suspension; never split check-and-mutate across a suspension point.
- Make types `Sendable` by design — internal value types of Sendable properties get it implicitly, but `public` library types must declare it (implicit conformance stops at module boundaries except `@frozen`). `@unchecked Sendable` and `nonisolated(unsafe)` require an internal synchronization mechanism plus a justification comment.
- Continuations resume exactly once on every path; use `withCheckedContinuation` variants; never store a continuation beyond its scope.
- No GCD as concurrency architecture: no `DispatchQueue.main.async` in async contexts (use actor isolation / `MainActor.run`), no semaphores bridging sync→async, no queues guarding state. Exception: next-runloop-tick deferral in synchronous AppKit paths remains legitimate.
- New code uses AsyncSequence/AsyncStream + Observation, not Combine (maintenance-mode, predates Sendable). Bridge existing pipelines with `.values`; don't mix paradigms in one flow.
- `deinit` is nonisolated — never touch actor-isolated state there; use `isolated deinit` where available, or move cleanup to an explicit `invalidate()`/task cancellation called before release.

## Language Mode Migration (Swift 5 → Swift 6)

Three concurrency-checking levels exist, opt-in under Swift 5 mode and unconditionally enforced under Swift 6 mode:

| Level | Behavior |
|---|---|
| Minimal | `Sendable` checked only where explicitly requested (e.g. explicit conformance) |
| Targeted | `Sendable` + actor-isolation checked wherever code has already adopted concurrency (`async`, actors) |
| Complete | `Sendable` + actor-isolation checked everywhere, whether or not the code uses concurrency |

- Swift 6 language mode == "Complete" checking, enforced as compiler **errors** instead of warnings.
- Enable per target:
  - Xcode: build setting **Swift Language Version** → 6, or **Strict Concurrency Checking** → Complete first (for Swift 5 mode projects migrating incrementally).
  - SwiftPM (`swift-tools-version: 6.0`+): `swiftLanguageMode(.v6)` on the package, or per-target `swiftSettings: [.swiftLanguageMode(.v6)]`.
- Migrate leaf modules (no dependents) first, then work upward to the app/executable target last — you cannot fully verify a module against Swift 6 rules while its dependents still assume Swift 5 semantics for it.
- Use `@preconcurrency import SomeUnmigratedDependency` to suppress errors caused by a dependency that hasn't adopted concurrency annotations yet, without disabling checking for your own code. It silences, it doesn't fix — a mixed Swift 5/6 graph can still hit real data-race crashes the `@preconcurrency` mask hid.
- `@preconcurrency` on your own declarations lets Swift-5-mode clients keep calling them without new warnings while you internally enforce Swift 6 rules underneath.

```swift
// Package.swift
let package = Package(
    name: "Feature",
    // ...
    targets: [
        .target(
            name: "Feature",
            swiftSettings: [.swiftLanguageMode(.v6)]
        )
    ]
)
```

## Actors

- `actor` types serialize access to their own mutable state — only one task executes inside an actor's isolated code at a time.
- Cross-actor calls are implicitly `async`; call from outside the actor with `await`.

```swift
actor BankAccount {
    private(set) var balance: Decimal

    init(balance: Decimal) { self.balance = balance }

    func withdraw(_ amount: Decimal) throws {
        guard balance >= amount else { throw BankError.insufficientFunds }
        balance -= amount
    }
}
```

### Reentrancy
- An actor is **reentrant**: an `await` inside an actor method is a suspension point where another task can run on the same actor before the first call resumes. The actor's state can change between the line before an `await` and the line after it.
- Never assume an invariant checked before an `await` still holds after it — recheck it, or restructure to do the check-and-mutate without an intervening suspension point.

```swift
actor Account {
    var balance = 100

    // BUG: balance can change during the `await` — two concurrent withdrawals
    // can both pass the guard before either decrements balance.
    func withdraw(_ amount: Int) async throws {
        guard balance >= amount else { throw AccountError.insufficientFunds }
        await auditLog.record(amount)   // suspension point — reentrancy window
        balance -= amount               // stale check by the time we get here
    }
}
```
Fix: perform the balance mutation before the `await`, or re-validate the guard after resuming.

### Sync critical sections
- For a small **synchronous** critical section (not suspending work), an `actor` is overkill. Use `Mutex` (Synchronization framework, macOS 15+) or `OSAllocatedUnfairLock` (macOS 13+) — pick by deployment-target floor. Both give a genuinely-checked `Sendable` type without the async hop of an actor.

## @MainActor

- Annotate UI-facing types/methods/properties `@MainActor` to pin them to the main thread; the compiler then rejects calls from other isolation contexts without `await`.
- `MainActor.run { }` hops onto the main actor from a nonisolated context for a single block — prefer structuring the call site to already be `@MainActor` over sprinkling `MainActor.run`.
- **Swift 6.2 / Xcode 26 default actor isolation**: new projects default every declaration to `@MainActor` isolation unless explicitly marked `nonisolated` or assigned to another actor (build setting **Default Actor Isolation** → `MainActor`; existing/migrated projects default to `nonisolated`, matching pre-6.2 behavior). This is a companion to "Approachable Concurrency" (a separate Xcode 26 toggle, not the same setting) — together the goal is single-threaded-by-default code that only goes concurrent where you say so. Know which mode a given project is in before assuming a bare declaration's isolation.
- Paired change: `nonisolated` **synchronous** functions behave as before; `nonisolated` **async** functions gain a new default under Approachable Concurrency — `nonisolated(nonsending)` — where they run on the *caller's* actor instead of hopping to the global executor. Use the explicit `@concurrent` attribute when you specifically want a `nonisolated async` function to run off the caller's actor on the cooperative thread pool.

## Sendable

- `Sendable` marks a type as safe to share across isolation domains (into a `Task`, across an actor boundary, into a `@Sendable` closure).
- Implicit conformance: `struct`/`enum` where every stored property/associated value is `Sendable`. A `class` only conforms implicitly when it is `final` and every stored property is an immutable (`let`) `Sendable` value. Implicit conformance stops at module boundaries — `public` library types must declare `Sendable` explicitly (except `@frozen`).
- `@unchecked Sendable` — opt out of compiler verification for a type you have manually made thread-safe (internal locking, `os_unfair_lock`, a `Mutex` from the Synchronization module). Comment *how* it's safe; never add it just to silence the compiler. Prefer a `Mutex`/`actor` over `@unchecked Sendable` + manual locking in new code.
- `@Sendable` on a closure asserts the closure's captures are safe to run concurrently/store past the current isolation domain — required for closures passed to `Task { }`, `Task.detached`, or stored for later concurrent invocation.
- `sending` (SE-0430) on a parameter or return value lets a **non-`Sendable`** value cross an isolation boundary safely by proving, via region-based isolation analysis, that the caller gives up all other references to it. Useful for handing off a freshly created object with no other owners into an actor without making the whole type `Sendable`.

## Structured Concurrency

- `async let` — a fixed, small number of known-in-advance concurrent child tasks:
```swift
async let profile = fetchProfile(id)
async let posts = fetchPosts(id)
return try await Profile(info: profile, posts: posts)
```
  If the enclosing scope exits (including via a thrown error) before an `async let` is awaited, its child task is implicitly awaited (or cancelled, on the error path) — you cannot leak it past the scope.
- `withTaskGroup` / `withThrowingTaskGroup` — a dynamic/variable number of child tasks:
```swift
try await withThrowingTaskGroup(of: Post.self) { group in
    for id in postIDs {
        group.addTask { try await fetchPost(id) }
    }
    return try await group.reduce(into: []) { $0.append($1) }
}
```
  Child tasks cannot outlive the `with...TaskGroup` closure; cancellation of the parent propagates to all children automatically. Never let the `TaskGroup` value escape its closure.

## Unstructured Tasks — and Their Dangers

- `Task { }` starts a new, unstructured top-level task. It inherits the creating context's actor isolation, priority, and task-local values — but it does **not** inherit structured lifetime: nothing automatically cancels it when the enclosing scope exits.
- If you store a `Task`'s handle, cancel it explicitly when it's no longer needed (`task.cancel()`) — typically in `deinit` or a teardown hook (`.onDisappear`). If you discard the handle, you lose the ability to cancel it at all.
- In SwiftUI, prefer the `.task {}` view modifier over a stored `Task` — it is automatically cancelled when the view disappears, which is the lifetime you almost always want.
- `Task.detached` additionally severs inheritance of actor context, priority, and task-local values — it always starts fresh on the cooperative thread pool. Reserve it for genuinely independent background work (e.g., a fire-and-forget analytics flush) that must not inherit the caller's `@MainActor` context; it is not a general-purpose substitute for `Task { }`.
- Long-running or infinite-loop unstructured tasks (e.g. a polling loop) must check `Task.isCancelled` / call `Task.checkCancellation()` between iterations, or they keep running forever even after their owner is gone.

## `deinit` Isolation

- `deinit` is `nonisolated` — you cannot touch actor-isolated or `@MainActor`-isolated stored state from it without triggering a concurrency error (or, worse, a hop that races deallocation).
- Where available, `isolated deinit` lets a `deinit` run on the type's actor. Otherwise, move teardown that must touch isolated state into an explicit `invalidate()` / `cancel()` method the owner calls **before** releasing the object, and keep `deinit` limited to non-isolated cleanup.

## AsyncSequence / AsyncStream

- `AsyncSequence` is the async analogue of `Sequence` — iterate with `for try await element in sequence`. Use `[weak self]` in a `for await` loop stored on a long-lived owner, as with any indefinite task body.
- `AsyncStream` / `AsyncThrowingStream` adapt a push-style/callback source into an `AsyncSequence`:
```swift
let (stream, continuation) = AsyncStream.makeStream(of: LocationUpdate.self)
locationManager.onUpdate = { update in continuation.yield(update) }
locationManager.onStop = { continuation.finish() }
```
  `makeStream()` (Swift 5.9+, SE-0388) hands back the stream and its continuation together, so you can store the continuation in a property and call `yield`/`finish` from anywhere.
- Continuations are `Sendable` and safe to call from any thread — but a stream's default buffering policy is unbounded; set `.bufferingNewest(_:)` / `.bufferingOldest(_:)` explicitly for a producer that can outpace its consumer.
- Always call `continuation.finish()` (or `finish(throwing:)`) when the underlying source is done — an un-finished stream leaves its consumer suspended forever on the next `for await`.
- Prefer `NotificationCenter.default.notifications(named:)` (an `AsyncSequence`) over the legacy block-based observer API when the consumer is already in an async context.

## Migrating Completion-Handler / GCD Code

- Bridge a callback-based API to `async`/`await` with `withCheckedContinuation` / `withCheckedThrowingContinuation`:
```swift
func fetchUser(id: String) async throws -> User {
    try await withCheckedThrowingContinuation { continuation in
        legacyAPI.fetchUser(id: id) { user, error in
            if let error { continuation.resume(throwing: error) }
            else if let user { continuation.resume(returning: user) }
            else { continuation.resume(throwing: LegacyError.noResult) }
        }
    }
}
```
- A continuation must be resumed **exactly once** — zero times leaks the awaiting task forever (it hangs); more than once is a runtime trap (checked variant) or undefined behavior (`withUnsafeContinuation`). Always prefer the *checked* variant; its safety checks cost nothing next to real async work.
- Every code path in the wrapped callback (success, failure, any early-return/guard) must resume the continuation — audit for early `return`s that skip it. For a 0-or-2-callback API, guard against the double-resume.
- Don't wrap something that already has a native `async` entry point (e.g., don't hand-roll a continuation around `URLSession.shared.data(for:)`, which already has an `async` overload).

## Testing Async Code

- Inject a clock (`any Clock`) rather than reading wall time directly; substitute an `ImmediateClock`/test clock so time-dependent code runs deterministically and instantly.
- Test cancellation explicitly: start the work, cancel it, assert the cooperative-cancellation path ran.
- Run the concurrency suite under the Thread Sanitizer in CI to catch races the type system can't.

## Anti-Patterns

- Reaching for `Task { }` inside synchronous code purely to silence an actor-isolation compiler error, without considering whether the call site should itself become `async`
- Discarding a `Task` handle when the work needs to be cancellable
- `Task.detached` used as the default instead of `Task { }` — losing context/priority/task-local inheritance for no reason
- Blocking a task's thread with a semaphore, lock, or `Thread.sleep` to fake synchronous behavior — starves the cooperative thread pool and can deadlock it
- Assuming actor/`@MainActor` state is unchanged immediately after an `await` without rechecking (reentrancy)
- `@unchecked Sendable` applied without actually auditing/enforcing thread-safety
- A continuation resumed zero times (hung task) or more than once (trap/undefined behavior)
- An `AsyncStream` whose continuation is never `finish()`-ed, leaving consumers suspended forever
- Unbounded `AsyncStream` buffering for a fast producer / slow consumer pair, growing memory without bound
- Touching actor-isolated state from `deinit`; relying on `deinit` for isolated teardown
- Mixing `DispatchQueue.main.async` with `@MainActor`/`await` as competing ways to "get to the main thread" in the same codebase
