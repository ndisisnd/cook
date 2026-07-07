# Swift Memory Management (ARC)

## Core Rules (P0)
- Delegates are `weak`, and delegate protocols are `AnyObject`-constrained.
- `unowned` only when the referenced object provably outlives the reference; when in doubt, `weak`. Accessing a deallocated `unowned` reference traps deterministically — `unowned(unsafe)` is genuine UB, never reach for it.
- `[weak self]` where a real cycle or unwanted lifetime extension exists — not reflexively. Needed: closures stored on `self` (handlers, observers, subscriptions), indefinite `Task` bodies (`for await` loops), task handles stored on `self`. Not needed: non-escaping closures; finite `Task {}` bodies where extending `self` until completion is correct. Prefer cancelling tasks as the primary lifetime tool.
- Invalidate `Timer`s (they retain targets); remove block-based NotificationCenter observers explicitly.

## How ARC Works
- Every class instance carries a reference count; each strong reference increments it, and each strong reference going out of scope decrements it. At zero, `deinit` runs and the instance is deallocated.
- Structs, enums, and other value types are not reference-counted — they're copied (or, for stdlib containers, copy-on-write). ARC only applies to `class` instances (and boxed existentials/closures that capture class references).
- A **retain cycle**: two (or more) instances hold strong references to each other, so neither ever reaches a refcount of zero — a leak the app never recovers from without external intervention (e.g., a memory-pressure kill).

## Closures: [weak self] vs [unowned self]

A closure captures the variables it references. If a closure captures `self` strongly and that closure is itself stored (directly or indirectly) on a property of `self`, you have a cycle.

```swift
final class ViewModel {
    var onUpdate: (() -> Void)?

    func start() {
        // Cycle: self.onUpdate -> closure -> self (strong)
        onUpdate = { self.refresh() }
    }
}
```

Fix with a capture list:

```swift
onUpdate = { [weak self] in self?.refresh() }
```

| | `[weak self]` | `[unowned self]` |
|---|---|---|
| Type inside closure | `Self?` (optional) | `Self` (non-optional) |
| If `self` is deallocated | Reference becomes `nil`; safe to check | **Crash** (trap) on access — no graceful failure |
| When to use | Default choice: closure can outlive `self`, or the lifetime relationship isn't certain | Only when you have *proven* `self` cannot be deallocated before the closure runs |
| Cost | Tiny (weak-reference side-table bookkeeping) | None — but the safety is entirely on you |

- Default to `[weak self]`. Only switch to `unowned` after you've established an invariant (e.g., a child object created and owned exclusively by `self`, guaranteed to be deallocated no later than `self`) — otherwise `unowned` turns a hard-to-hit race into a hard crash.
- Accessing a deallocated `unowned` reference **traps deterministically** (a well-defined crash). Only `unowned(unsafe)` is genuine undefined behavior (silent memory corruption) — never reach for it just to avoid a trap you don't like.
- `[weak self]` requires unwrapping inside the closure: `self?.foo()`, or `guard let self else { return }` (Swift 5.7+ shorthand rebinding).
- Capture list syntax: `{ [weak self, unowned delegate] value in ... }` — mix weak/unowned/strong per captured name; you can also capture a renamed/derived value: `{ [weak viewModel = self.viewModel] in ... }`.
- `@escaping` closures are the ones that matter for cycles — a non-escaping closure (the default for a function parameter) can't outlive the call, so it can't create a lasting cycle.

## Delegate Pattern

- Delegate properties are always `weak`: the delegate (typically a view controller or coordinator) outlives the delegating object in the common ownership direction (parent owns child, child references parent as delegate).
```swift
protocol DownloadDelegate: AnyObject {
    func downloadDidFinish(_ download: Downloader)
}

final class Downloader {
    weak var delegate: DownloadDelegate?
}
```
- A delegate protocol must be constrained to reference types (`: AnyObject`) for `weak var delegate:` to compile.

## Parent/Child Reference Cycles

- When a parent owns children in a collection and children need to reference their parent, the child's back-reference must be `weak` (or `unowned` if the child's lifetime is provably bounded by the parent's).
```swift
final class Node {
    weak var parent: Node?
    var children: [Node] = []   // strong — parent owns children
}
```
- Getting the direction backwards (children hold `parent` strongly, or a cache holds strong references to objects that should instead hold a weak back-reference to the cache) is one of the most common cycle sources in view/coordinator hierarchies.

## Common Leak Patterns

- **`Timer`**: `Timer.scheduledTimer` retains its target (or the closure, for the closure-based API) strongly, and a repeating timer keeps firing — and keeps its target alive — until `invalidate()` is called. If the object holding the `Timer` is also referenced by the timer, relying on `deinit` isn't enough (`deinit` won't run while the cycle exists) — invalidate the timer explicitly when the owning screen/session ends (`onDisappear`, teardown), and use `[weak self]` in the closure-based initializer as a second line of defense.
- **`NotificationCenter` observers**: the block-based `addObserver(forName:object:queue:using:)` returns an opaque token that `NotificationCenter` does *not* automatically release — you must call `removeObserver(_:)` with that token (commonly in `deinit`), or the closure (and anything it captures) is kept alive indefinitely. Prefer wrapping the token in an object whose own `deinit` calls `removeObserver`, or use the `NotificationCenter.notifications(named:)` async sequence inside a cancellable `Task` for new code.
- **Closures stored in properties**: any `var onComplete: (() -> Void)?`-style stored closure property that captures `self` needs `[weak self]` at the capture site, not at the property declaration — the property declaration itself can't fix this.
- **`CADisplayLink`**: same shape as `Timer` — retains its target until `invalidate()`; invalidate it when the associated view disappears.
- **Combine / async subscriptions**: a `Cancellable` (or `Task` handle) stored in a `Set<AnyCancellable>` or property that is never cleared keeps the subscription's closures (and their captures) alive for the lifetime of the owner — make sure the owner's lifetime is actually what you want to key the subscription to.

## Diagnosing Leaks

- Xcode's **Memory Graph Debugger** (the memory icon in the debug bar) shows retain cycles directly — purple exclamation marks flag cycles that a `deinit` breakpoint would otherwise never catch.
- Instruments' **Leaks** and **Allocations** templates catch cycles and unbounded growth over a running session. The full Instruments workflow lives in the macOS platform standards (`standards/macos/refs/performance-accessibility.md`) — this file covers the ARC-level cause, not the profiling tool.

## Anti-Patterns

- Strong `self` capture in an escaping closure stored on `self` (directly or via a delegate/callback chain)
- `[unowned self]` used without proving `self`'s lifetime bounds the closure's; `unowned(unsafe)` ever
- Delegate property declared `var delegate: SomeDelegate?` (strong) instead of `weak var delegate: SomeDelegate?`
- Parent-owned child holding a strong back-reference to its parent
- `Timer`/`CADisplayLink` never `invalidate()`-d when its owner's lifecycle ends
- Block-based `NotificationCenter` observer token never passed to `removeObserver(_:)`
- Assuming `deinit` will run to "clean up later" on an object that is itself part of the cycle it needs to break
