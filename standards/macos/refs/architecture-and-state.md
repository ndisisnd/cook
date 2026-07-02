# macOS Architecture & State

## Observation Framework (`@Observable`)

- Framework: `Observation` (`import Observation`), introduced WWDC23 via SE-0395. Minimum OS: macOS 14+. Class-only — `@Observable` applies to `class` types, not `struct`/`enum`.
- **Macro expansion**: each stored property becomes a computed property. The synthesized getter calls `access(keyPath:)` to register read-tracking for that specific keyPath; the synthesized setter wraps the mutation in `withMutation(keyPath:) { ... }`, which fires the change notification after the mutation completes. A hidden `@ObservationIgnored private let _$observationRegistrar` plus forwarding helpers back this. The registrar maps `(object, keyPath) → view-update closure` and is thread-safe.
- **Fundamental difference vs `ObservableObject` + `@Published`**: Observation tracks dependencies at the individual property (keyPath) level, discovered dynamically by which properties a view's `body` actually reads during render. `ObservableObject` broadcasts one `objectWillChange` on **any** `@Published` mutation — every view holding `@ObservedObject`/`@StateObject` on that instance re-evaluates its whole `body` regardless of which property it uses.
- Works with plain Swift reference types (not just `NSObject` subclasses like KVO required), and is usable outside SwiftUI (AppKit/UIKit too).
- **Gotcha — `@State` init-timing**: unlike `@StateObject`'s once-only `@autoclosure` initialization, `@State`'s initial-value expression can be re-evaluated across view-struct rebuilds if object ownership isn't respected. Side-effectful `init()` logic (notification registration, `UserDefaults` reads) can run more than once and leak. Mitigation: keep such objects at the `App`/root-scene level, keep `init()` side-effect-free, and do one-time setup in `.task {}`.

```swift
@Observable
final class CounterModel {
    var count = 0
    @ObservationIgnored private var cache: [Int: String] = [:]  // opt a property out of tracking
}
```

## `@State`, `@Bindable`, and Ownership

- **`@State` owns the instance.** Only the view that creates an `@Observable` object should hold it in `@State`; every downstream view receives it as a plain `let`/parameter (or via `@Bindable`/`@Environment`) — SwiftUI propagates observation automatically without re-wrapping.
- **`@StateObject` is legacy** — needed only for `ObservableObject` conformers or pre-macOS-14 deployment targets. Downstream views no longer need `@ObservedObject` at all with `@Observable` types; a plain property is sufficient.
- **`@Bindable`** produces `Binding`s (`$model.property`) to mutable properties of an `@Observable` object. Required whenever the object arrived as a parameter or via `@Environment` (not already `@State` in the same view — SwiftUI derives those automatically).

```swift
struct DetailView: View {
    @Bindable var model: MyModel          // param-sourced: needs @Bindable for $model.name
    var body: some View { TextField("Name", text: $model.name) }
}

// Inline form when you only have a local `let`/plain var:
var body: some View {
    @Bindable var model = model
    TextField("Name", text: $model.name)
}
```

## Why `@Observable` Replaced `ObservableObject` for New Code

- **Core claim (WWDC23 "Discover Observation in SwiftUI")**: view invalidation becomes per-property, not per-object — a view re-renders only if a property it actually read in `body` changed. No official numeric benchmark is published; the behavioral difference (unobserved-property change → zero redraw with `@Observable` vs guaranteed redraw with `ObservableObject`) is confirmed by third-party testing.
- Apple explicitly decoupled the view layer from Combine — "the reactive stream model is not always the best model for interface state."
- Tracking propagates through nested `@Observable` object graphs and arrays of observable elements at runtime; everything is tracked by default unless marked `@ObservationIgnored` — no `@Published`-style per-property annotation.

## When Combine Is Still Appropriate

Combine is **not deprecated** — Apple continues to ship and maintain it. Reach for it specifically for:
- Complex multi-publisher composition (`combineLatest`, `merge`, `zip`).
- Timers (`Timer.publish`) and `NotificationCenter` interop.
- Existing large Combine-based codebases not worth migrating.
- Bridging a publisher to async/await via `.values` (`AsyncPublisher`).

For debounce/throttle in new async/await code, prefer the **Swift Async Algorithms** package (`debounce`, `throttle`, `merge`, `combineLatest` over `AsyncSequence`) over introducing Combine just for that. Default to async/await + `AsyncSequence` for new code; use Combine for multi-publisher composition or legacy interop, not as the default reactive layer under views.

## MVVM on SwiftUI-for-Mac: No Settled Consensus

There is no single Apple-mandated pattern as of 2025–2026 — this is a live community debate:
- One camp argues ViewModels are UIKit-era baggage misapplied to SwiftUI's declarative model, and that state should live directly in views plus `@Environment`.
- The counter-camp argues dropping ViewModels hurts testability, maintainability, and preview isolation.
- **Practical guidance**: treat MVVM as optional, not default. `@Observable` + `@Environment` makes thin/no-ViewModel architectures far more viable than pre-2023 (no Combine boilerplate). A slim `@Observable` "model" type — not necessarily named `ViewModel` — is still reasonable when you need business-logic isolation or unit-testability independent of the view. Don't introduce a ViewModel layer purely out of habit; don't refuse one purely out of trend. A dedicated `ViewModels/` folder is optional; many `@Observable` apps keep state on the view or in a flat `Models/` layer.

## Dependency Injection: `@Environment` / `@Entry`

- **`@Entry` macro** (Xcode 16+) collapses the old custom-`EnvironmentKey`-struct boilerplate into one line. `EnvironmentKey` itself is not deprecated — `@Entry` expands to the same underlying pattern.
```swift
extension EnvironmentValues {
    @Entry var favoriteColor: Color = .blue
}
```
- **`@Environment(MyService.self)` replaces `@EnvironmentObject`** for `@Observable` types — the type itself is the lookup key:
```swift
ContentView().environment(searchModel)          // .environment(_:), not .environmentObject(_:)
@Environment(SearchModel.self) var searchModel   // consume
```
`@EnvironmentObject`/`.environmentObject()` remain only for legacy `ObservableObject` types.
- **DI guidance**: use `@Environment` for cross-cutting/shared services reachable from many descendant views (theming, auth session, shared caches). Use plain initializer injection for a view's directly-owned, narrowly-scoped dependencies. Pick one DI mechanism app-wide; `swift-dependencies` or Factory are reasonable library options if you outgrow plain injection.

## SwiftData vs Core Data (Decision Guidance)

Default to **SwiftData** for new, simple/local-first or single-user-iCloud apps. Use **Core Data** (or GRDB for a SQLite-first stack) instead when the app needs any of:
- **CloudKit sharing** (multi-user shared records) — SwiftData's story is narrower than Core Data + CloudKit's mature sharing.
- **Complex, versioned migrations**, especially custom hooks — SwiftData's `willMigrate`/`didMigrate`-style hooks are not invoked in CloudKit-synced configurations, and custom `MigrationStage` remains fragile.
- **`NSPersistentDocument`/multi-window, document-based architecture** — Core Data's document integration is significantly more mature.
- **Fine-grained undo** in a document-based app — SwiftData exposes `ModelContext.undoManager` (opt-in, off by default) but it is newer and less battle-tested than Core Data's `NSDocument`/`UndoManager` integration.
- Raw performance at scale — several 2025 comparisons found SwiftData measurably slower than Core Data for equivalent workloads.

Both frameworks share the same CloudKit production gotchas: the dev/prod CloudKit schema must be manually promoted after first release or sync silently breaks, and all synced attributes must be optional/defaulted with no unique constraints. Treat SwiftData's API surface as still evolving between OS versions — verify behavior on your actual minimum deployment target. Existing SwiftData codebases stay on it unless migration is the explicit task.

## Core Data Concurrency (when you choose it)

- Contexts are confined: touch a context and its managed objects only inside `perform`/`performAndWait`. `viewContext` is main-thread only; do background work on a background context.
- Never pass an `NSManagedObject` across an actor/thread boundary — pass an `NSManagedObjectID` (and re-fetch on the destination context) or a `Sendable` value snapshot.
- `NSPersistentCloudKitContainer` constraints: optional/defaulted attributes only, no unique constraints, and push the dev schema to production before shipping sync.

## Anti-Patterns

- New `ObservableObject`/`@Published`/Combine view models for new code (exception: pre-macOS-14 targets or genuine multi-stream composition)
- `@EnvironmentObject`/`.environmentObject()` for an `@Observable` type
- Side-effectful `@Observable` `init()` relied on to run exactly once
- Reading a whole object gratuitously in `body` (e.g. `print(model)`), defeating per-property invalidation
- Introducing a `ViewModel` layer purely out of habit, or refusing one purely out of trend
- Introducing Combine just to get debounce/throttle — use Swift Async Algorithms
- `NSManagedObject` crossing actor boundaries; `viewContext` used for background work
- Unique constraints or non-optional attributes on a CloudKit-synced Core Data/SwiftData model
