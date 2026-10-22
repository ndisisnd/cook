---
last_reviewed: 2026-10-18
---

# Swift Memory Management (ARC)

## Core Rules (P0)
- Delegates are `weak`, and delegate protocols are `AnyObject`-constrained.
- `unowned` only when the referenced object provably outlives the reference; when in doubt, `weak`. Accessing a deallocated `unowned` reference traps deterministically — `unowned(unsafe)` is genuine UB, never reach for it.
- `[weak self]` where a real cycle or unwanted lifetime extension exists — not reflexively. Needed: closures stored on `self` (handlers, observers, subscriptions), indefinite `Task` bodies (`for await` loops), task handles stored on `self`. Not needed: non-escaping closures; finite `Task {}` bodies where extending `self` until completion is correct. Prefer cancelling tasks as the primary lifetime tool.
- Invalidate `Timer`s (they retain targets); remove block-based NotificationCenter observers explicitly.
- Child back-references to a parent are `weak` (parent owns children strongly).

## Common Leak Sources

- **`Timer` / `CADisplayLink`**: retain their target (or closure) until `invalidate()`. `deinit` will not run while the cycle exists — invalidate when the owning screen/session ends, and use `[weak self]` in the closure initializer as a second line of defense.
- **Block-based `NotificationCenter` observers**: the returned token keeps the closure alive until `removeObserver(_:)`. In new code use `notifications(named:)` inside a cancellable `Task`.
- **Stored closure properties** (`var onComplete: (() -> Void)?`): fix the cycle with `[weak self]` at the capture site; the property declaration cannot fix it.
- **Subscriptions**: a `Set<AnyCancellable>` or stored `Task` handle keeps its closures alive for the owner's lifetime — confirm that lifetime is the one you want.
- **Indefinite `for await` loops** in a `Task` stored on `self`: capture `[weak self]` and cancel the task in teardown.

## Diagnosing Leaks

- Xcode **Memory Graph Debugger** shows retain cycles with reference paths — the first tool for cycles.
- Instruments **Leaks** and **Allocations** (Mark Generation) catch abandoned memory and unbounded growth. Profiling workflow → `standards/macos/refs/performance-accessibility.md`.

## Anti-Patterns

- Strong `self` capture in an escaping closure stored on `self` (directly or via a callback chain)
- `[unowned self]` without proving lifetime bounds; `unowned(unsafe)` ever
- Strong delegate property (`var delegate: SomeDelegate?`)
- Parent-owned child holding a strong back-reference to its parent
- `Timer`/`CADisplayLink` never invalidated when its owner's lifecycle ends
- Block-based observer token never passed to `removeObserver(_:)`
- Relying on `deinit` to break a cycle the object itself is part of
