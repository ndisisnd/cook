---
last_reviewed: 2026-10-18
---

# Swift Concurrency

Targets Swift 6.2+ in Swift 6 language mode. Swift 6.4 (Sept 2026, Xcode 27) features are flagged inline.

## Core Rules (P0)

### Language Mode & Isolation Defaults
- New app/executable targets: Swift 6 language mode + Approachable Concurrency + default `MainActor` isolation. The latter two are Xcode template defaults; set `SWIFT_VERSION` to 6 explicitly. Single-threaded by default; move work off-main explicitly.
- Library/package targets: Swift 6 mode with `nonisolated` default isolation — never MainActor-bind a networking or domain package.
- Know which default a module uses before reasoning about a bare declaration's isolation. Xcode: **Default Actor Isolation** build setting. SwiftPM (tools 6.2+): `swiftSettings: [.defaultIsolation(MainActor.self)]` or `.defaultIsolation(nil)`; omitted = nonisolated.
- Migrate existing modules one at a time (strict checking minimal → targeted → complete), leaf modules first. `@preconcurrency import` is a temporary bridge — it silences, it doesn't fix.

### Tasks & Cancellation
- Prefer structured concurrency: `async let` for a fixed few parallel ops, `TaskGroup` for dynamic fan-out. Unstructured `Task {}` needs an owner and a cancellation story; `Task.detached` almost never (only to escape actor context, priority, and task-locals at once).
- Mark CPU-heavy functions `@concurrent` to hop off the caller's actor; under Approachable Concurrency, `nonisolated async` runs on the caller's actor (`nonisolated(nonsending)`).
- Cancellation is cooperative: long loops call `try Task.checkCancellation()`; in SwiftUI prefer `.task {}` (auto-cancelled) over stored handles. A stored `Task` handle is cancelled explicitly in teardown.
- Swift 6.4: `withTaskCancellationShield { }` (SE-0504) runs must-finish cleanup as if the task were not cancelled. It needs the new runtime (no back-deployment) — gate with `#available`.
- Swift 6.4: `defer` may `await` inside async functions (SE-0493) — use it for async teardown instead of duplicating cleanup on every exit path.

### Shared State
- Don't reach for `actor` by default — most state belongs on `@MainActor` or in value types. When state is genuinely shared and mutated across suspending contexts, an `actor` is the standard tool.
- Small synchronous critical sections: `Mutex` (Synchronization, macOS 15+) or `OSAllocatedUnfairLock` (macOS 13+) — pick per deployment target. Never raw `os_unfair_lock` from Swift (address instability).
- Actor reentrancy: state can change across every `await` — re-validate invariants after suspension; never split check-and-mutate across a suspension point.
- Make types `Sendable` by design. `public` library types must declare it (implicit conformance stops at module boundaries except `@frozen`). `@unchecked Sendable` and `nonisolated(unsafe)` require an internal `Mutex`/lock plus a justification comment.
- `sending` (SE-0430) hands a non-`Sendable` value with no other owners across an isolation boundary without making the type `Sendable`.
- Continuations resume exactly once on every path; use the `withChecked…Continuation` variants; never store a continuation beyond its scope.
- `deinit` is nonisolated — never touch isolated state there; use `isolated deinit` where available, or an explicit `invalidate()` called before release.

### GCD & Combine — the single exception list
No GCD or Combine as concurrency architecture: no `DispatchQueue.main.async` in async contexts (use isolation / `MainActor.run`), no semaphores bridging sync→async, no queues guarding state, no new Combine pipelines. Platform refs (`standards/macos/`) defer to this list. Allowed only for:
1. Next-runloop-tick deferral (`DispatchQueue.main.async`) in synchronous AppKit/UIKit paths.
2. Callback- or queue-based APIs that require a `DispatchQueue` parameter (AVFoundation delegates, `Network.framework`, C libraries) — wrap at the boundary with a continuation or `AsyncStream`.
3. Existing Combine code: keep it, bridge out with `.values`; never mix Combine and `await` in one flow.
4. Framework APIs that only vend publishers — bridge with `.values` immediately.

New code uses `AsyncSequence`/`AsyncStream` + Observation. Timers: `Task` + `Task.sleep(for:)` or `clock.sleep`, or a tolerance-set `Timer`. Notifications: `NotificationCenter.default.notifications(named:)`. Debounce/throttle/merge: swift-async-algorithms, not Combine.

## Default MainActor Isolation & Conformances

- Under default `MainActor` isolation, `nonisolated` **synchronous** functions behave as before; `nonisolated` **async** functions run on the caller's actor unless marked `@concurrent`.
- Isolated conformances (SE-0470, Swift 6.2): a `@MainActor` type can satisfy a nonisolated protocol with `extension Model: @MainActor Equatable { … }`. The conformance is usable only on the main actor, and never where the generic signature requires `Sendable`/`SendableMetatype`.
- Enable the `InferIsolatedConformances` upcoming feature in MainActor-default modules so conformances inherit the type's isolation. Mark a conformance `nonisolated P` when it must be used off-main (e.g. `Codable` decoded in a background task).

## Actor Reentrancy

```swift
actor Account {
    var balance = 100

    // BUG: two concurrent withdrawals can both pass the guard
    func withdraw(_ amount: Int) async throws {
        guard balance >= amount else { throw AccountError.insufficientFunds }
        await auditLog.record(amount)   // suspension point — reentrancy window
        balance -= amount               // stale check by the time we get here
    }
}
```
Fix: mutate before the `await`, or re-validate the guard after resuming.

## Sendable Details

- Implicit conformance: `struct`/`enum` whose stored properties are all `Sendable`; a `final class` with only `let` `Sendable` properties.
- `@unchecked Sendable` — only for a type made thread-safe with a `Mutex`/`OSAllocatedUnfairLock`. Comment *how* it is safe. Prefer `Mutex` or an `actor` in new code.
- `@Sendable` closures are required for closures stored or run concurrently past the current isolation domain.

## Structured Concurrency

```swift
async let profile = fetchProfile(id)
async let posts = fetchPosts(id)
return try await Profile(info: profile, posts: posts)
```
An un-awaited `async let` is implicitly cancelled and awaited at scope exit.

```swift
try await withThrowingTaskGroup(of: Post.self) { group in
    for id in postIDs { group.addTask { try await fetchPost(id) } }
    return try await group.reduce(into: []) { $0.append($1) }
}
```
Never let the group escape its closure. Parent cancellation propagates to children.

## AsyncSequence / AsyncStream / Observations

```swift
let (stream, continuation) = AsyncStream.makeStream(of: LocationUpdate.self,
                                                    bufferingPolicy: .bufferingNewest(10))
locationManager.onUpdate = { continuation.yield($0) }
locationManager.onStop = { continuation.finish() }
```
- Set a buffering policy for a producer that can outpace its consumer; the default is unbounded.
- Always `finish()` the continuation — an unfinished stream suspends its consumer forever.
- `Observations { model.value }` (Observation, macOS 26+/iOS 26+) is an `AsyncSequence` of an `@Observable` value's changes; synchronous changes coalesce into one emission. Prefer it over hand-rolled `withObservationTracking` loops on a 26+ floor.

## Migrating Completion-Handler Code

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
- Audit every early `return` in the callback for a missed resume. Don't wrap APIs that already have an `async` overload.

## Language Mode Migration (Swift 5 → 6)

| Level | Behavior |
|---|---|
| Minimal | `Sendable` checked only where explicitly requested |
| Targeted | `Sendable` + isolation checked where code already adopted concurrency |
| Complete | Checked everywhere; Swift 6 mode = Complete as **errors** |

- Xcode: **Swift Language Version** → 6, or **Strict Concurrency Checking** → Complete first. SwiftPM: per-target `swiftSettings: [.swiftLanguageMode(.v6)]`.
- `@preconcurrency` on your own declarations keeps Swift-5-mode clients compiling while you enforce Swift 6 internally.

## Testing Async Code

- Inject a `Clock` (stdlib protocol, e.g. `any Clock<Duration>` / `some Clock<Duration>`) instead of calling `Task.sleep` or reading wall time directly. Test clocks such as `ImmediateClock`/`TestClock` come from the third-party swift-clocks package — use them only if it is already a dependency. Wall-time reads use a separate seam (see `refs/testing.md`).
- Test cancellation explicitly: start the work, cancel it, assert the cancellation path ran.
- Run the concurrency suite under Thread Sanitizer in CI.

## Anti-Patterns

- `Task { }` in synchronous code purely to silence an isolation error
- `Task.detached` as the default; discarding a handle for work that must be cancellable
- Blocking a task with a semaphore, lock wait, or `Thread.sleep` — starves the cooperative pool
- Assuming state is unchanged after an `await` (reentrancy)
- `@unchecked Sendable` without a lock; raw `os_unfair_lock` in Swift
- Continuation resumed zero times or twice; `AsyncStream` never finished or unbounded for a fast producer
- Touching isolated state from `deinit`
- GCD or Combine outside the exception list; `DispatchQueue.main.async` and `@MainActor` as competing ways to reach main
- Isolated conformance used where `Sendable` is required, or a MainActor-default conformance needed off-main without `nonisolated`
