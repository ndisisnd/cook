# Swift Performance

Reach for this only after a profiler says a path is hot. Measure first — most of these tradeoffs are invisible outside tight loops, and premature application hurts readability for no gain.

## Dispatch & Boxing

- **Existentials (`any`) box and dynamically dispatch.** In a hot path, an `any Protocol` value allocates a box and calls through a witness table; a generic (`some`/`<T: P>`) is specialized and statically dispatched. Prefer generics on hot APIs; reserve `any` for genuine heterogeneous storage.
- Use **primary associated types** (`some Collection<Element>`) so the compiler keeps the concrete type and can specialize.
- **`final` / `private` enable devirtualization.** A non-`final` class method is called through the class's vtable; marking the class or method `final` (or `private`, which is implicitly final within the file) lets the optimizer inline the call. Mark classes `final` by default.
- Whole-module optimization (`-O` + WMO, the Release default) is what makes cross-file devirtualization and specialization possible — Debug builds keep it off for incremental speed, so don't benchmark in Debug.

## ARC Traffic

- Every strong-reference copy in a tight loop is a `retain`/`release` pair — real, if small, cost. In a measured hotspot, prefer value types (no ARC), hoist a class reference out of the loop, or use `borrowing`/`consuming` parameter ownership (where available) to avoid redundant retains.
- Passing a class instance across many calls churns ARC; a `struct` of the fields you actually need does not.

## Strings & Collections

- `String.count` is **O(n)** (it counts grapheme clusters) — never call it repeatedly in a loop or use it for a fast emptiness check; use `isEmpty`. Avoid repeated index arithmetic; iterate with the view you need (`.utf8` for byte-level parsing).
- Reserve capacity (`reserveCapacity(_:)`) before a known-size append loop to avoid repeated reallocation.
- Use `NSCache` (bounded, memory-pressure-aware) for caches instead of an unbounded `Dictionary` that grows until the app is killed.

## Build-Time Hygiene

- The type checker can explode on large literals and long operator chains. Enable `-warn-long-expression-type-checking=<ms>` and `-warn-long-function-bodies=<ms>` to surface offenders.
- Fixes: split a complex expression into intermediate `let`s, and add explicit types to big collection/dictionary literals so the checker doesn't infer across the whole expression.

## Measuring: Instruments & Field Metrics

- **Time Profiler** for CPU hotspots; **Hangs** / **Hitches** for main-thread stalls and dropped frames (see also `standards/macos/refs/performance-accessibility.md` for the platform-level beachball workflow).
- Instrument your own intervals with **`OSSignposter`** — begin/end signposts show up as named regions in Instruments, far more useful than eyeballing the call tree.
- **MetricKit** (`MXMetricManager`) delivers aggregated CPU, memory, hang, and launch metrics from real user devices — wire it up so you learn about field regressions you can't reproduce locally.
- Automate **dSYM upload** in CI so field crash/metric reports symbolicate.

## Anti-Patterns

- Optimizing without a profiler pointing at the line
- `any` in a hot path where `some`/generics would specialize
- Non-`final` classes on a hot dispatch path
- `String.count` for emptiness or inside a loop
- Unbounded `Dictionary` used as a cache
- Benchmarking in Debug (no WMO), then trusting the numbers
- Giant type-inferred literals that blow up compile time
