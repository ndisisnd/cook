# macOS Performance & Accessibility

## Instruments Usage Patterns

Reach for the right template — don't default to Time Profiler for every problem:

- **Time Profiler** — CPU hotspots, slow UI response, beachballs. Samples all threads' backtraces (~1000×/sec); aggregates into a call tree with **Weight** (% of samples containing that frame) and **Self** (time in that frame only). Use "Separate by Thread" + "Invert Call Tree" to isolate main-thread hotspots. Very short-lived functions can be missed between sampling ticks.
- **Allocations** — tracks memory growth. Use "Mark Generation" to snapshot persisting allocations between two points: repeat the suspect action, mark again — if a generation's "# Persistent" count doesn't return to ~0 after the action completes, that generation is leaking or unexpectedly retained.
- **Leaks** — still useful for genuine "abandoned memory" (no references at all). For **retain-cycle** debugging specifically, prefer Xcode's **Memory Graph Debugger** (Debug Navigator → Debug Memory Graph) — it shows the live object graph with reference paths without a separate profiling run.
- **SwiftUI instrument** (Product → Profile → SwiftUI) — tracks **View Body** (recomputation count + duration per view), **View Properties** (which observed properties changed), and **Core Animation Commits**. The direct tool for "why does this view redraw so often."
- **Hangs instrument** — detects main-run-loop unresponsiveness (default threshold ~250ms of a blocked/busy main thread). Included in Time Profiler, CPU Profiler, and Hitches templates. The direct beachball root-cause tool.
- **Hitches / Animation Hitches** — brief frame-deadline misses during scrolling/animation.
- **App Launch template** — breaks launch into pre-`main`, `main`-to-first-frame, and post-launch phases.

## Main-Thread Hygiene (Beachball Avoidance)

`NSApplication` owns and drives the main run loop. Any synchronous work dispatched to it stalls window, menu, and event handling app-wide — not just one view — producing the spinning beachball. Confirmed common culprits:

- Synchronous network calls on the main thread (`Data(contentsOf: remoteURL)`, blocking `URLSession` semaphore patterns).
- Synchronous disk I/O — large file reads, `FileManager` over big directories.
- Unbounded `JSONDecoder.decode` on a large payload run synchronously on `@MainActor`.
- Unbounded synchronous SwiftData/Core Data fetches on the main context — no fetch limit, no batching, no background context.
- Expensive SwiftUI `body` computation or AppKit layout passes; `DispatchSemaphore.wait()` on the main thread.
- `ReferenceFileDocument` saves — observed running on the main thread in practice despite docs implying otherwise; test large-document saves explicitly.

**Swift 6 strict concurrency**: `@MainActor` isolation is compiler-enforced — UI mutations not marked `@MainActor` are now compile errors, catching many main-thread violations at build time. The **Default Actor Isolation = MainActor** project setting defaults every unmarked declaration to `@MainActor` for new projects — which *raises* the risk of accidentally running heavy synchronous work "on `@MainActor` by default." Keep genuinely heavy work in `nonisolated`/`@concurrent` contexts rather than relying on the default.

## Background Work Patterns

- **`Task { }`** — inherits the caller's actor, priority, and task-locals. Created inside `@MainActor`, its body starts on `@MainActor` unless it explicitly hops. The idiomatic default for async work tied to the current UI flow.
- **`Task { @MainActor in ... }`** — explicit hop back to the main actor to touch UI state.
- **`Task.detached { }`** — no inherited actor, priority, cancellation, or task-locals; closest analog to `DispatchQueue.global(qos:).async`. Avoid as a default — it drops cancellation propagation and priority inheritance. Use only when you specifically need an independent top-level task.
- **`DispatchQueue.global(qos:)`** — still idiomatic for interop with non-async legacy APIs, C libraries, or callback-based frameworks. GCD remains fine at integration boundaries.
- **`OperationQueue`** — still relevant when you need dependencies between units of work, cancellation of queued-but-not-started operations, a max-concurrent cap, or KVO-observable operation state — capabilities a bare `Task` doesn't cleanly model. Common in multi-stage background pipelines in document-based AppKit apps.
- **XPC service** (separate process) — reach for this when the goal is isolation, not just concurrency: (1) untrusted/attacker-controlled file parsing (a crash/exploit stays in the sandboxed helper); (2) plugin/third-party code execution; (3) sustained heavy CPU/memory you don't want sharing the app's memory ceiling; (4) work that should outlive the requesting UI process; (5) privilege separation. Trusted, "just slow" work belongs in an in-process `Task`/`OperationQueue`.

## App Nap & Energy

- Respect App Nap: `NSBackgroundActivityScheduler` for deferrable work, `ProcessInfo.beginActivity(options:reason:)` for user-visible long work that must not be napped, and tolerance on every timer.
- Don't poll where change notifications exist (KVO, `NotificationCenter`, FSEvents); a notification-less external resource may poll with backoff.

## Launch-Time Optimization

Apple's framing: **minimize** (defer anything not needed for the first frame), **prioritize** (essential-first), **optimize** (make necessary work faster).

- Avoid heavy synchronous work in `applicationDidFinishLaunching(_:)`, `App.init()`, or an unconditional launch-time `.task {}` (large loads, eager singleton graphs, startup network calls). Defer to a lazy `.task {}` on the view that needs the data, or background-load behind a loading state.
- Fewer, statically-linked, or lazily-loaded (`dlopen`) third-party dependencies reduce dyld binding/rebasing before `main()`. The dyld shared cache mitigates this for system frameworks, not your own dynamic frameworks.
- Measure with the **App Launch** template; `DYLD_PRINT_STATISTICS=1` gives a dyld-phase breakdown.

## VoiceOver / Accessibility

Required for App Store and enterprise accessibility compliance.

**SwiftUI modifiers**: `.accessibilityLabel(_:)`, `.accessibilityValue(_:)`, `.accessibilityHint(_:)`, `.accessibilityAddTraits(_:)`/`.accessibilityRemoveTraits(_:)`, `.accessibilityElement(children:)`, `.accessibilityHidden(_:)`, `.accessibilityAction(_:_:)`, and `.accessibilityIdentifier(_:)` (UI-test targeting only — no VoiceOver-user-facing effect).

**Custom `NSView` / AppKit** — implement `NSAccessibilityProtocol`, the current protocol-based API (the older informal key-value API still exists for back-compat but the formal protocol takes precedence). Key overridable members: `isAccessibilityElement`, `accessibilityLabel`, `accessibilityRole`, `accessibilityValue`, `accessibilityChildren`, plus role-specific actions (e.g. `accessibilityPerformPress()`). For a view drawing multiple independently-accessible sub-elements with no backing `NSView` each, return `NSAccessibilityElement` instances from `accessibilityChildren`.

```swift
final class SwatchView: NSView {
    override var isAccessibilityElement: Bool { true }
    override var accessibilityRole: NSAccessibility.Role? { .button }
    override var accessibilityLabel: String? { "Select red" }
}
```

**Auditing**: **Accessibility Inspector** (ships with Xcode) has an Audit tab that scans for missing labels, low contrast, clipped text, and missing Dynamic Type support. The same checks are automatable in XCTest since Xcode 15 via `XCUIApplication().performAccessibilityAudit(for:_:)` — fails the test on unhandled issues, with an issue-handler closure to filter accepted findings. Wire this into CI, not just manual spot-checks.

**Manual VoiceOver testing on Mac**: `⌘F5` toggles VoiceOver system-wide. VoiceOver Utility configures speech rate, verbosity, and navigation style for testing sessions. Verify UI under Reduce Transparency and Increase Contrast (glass materials especially) and honor Reduce Motion.

## Dynamic Type on Mac (do not assume iOS parity)

macOS Dynamic Type support is historically limited and structurally different from iOS, and this remains true through the macOS 26 "Tahoe" era:

- `DynamicTypeSize`/`.dynamicTypeSize()` exist as SwiftUI API on Mac, but text using system `Font.TextStyle` values has not reliably responded to a system-wide user text-size setting the way it does on iOS — Mac text sizing has behaved closer to fixed point sizes per style, with users adjusting perceived size via display scaling.
- macOS 26 Tahoe added a System Settings → Accessibility → Display → Text Size slider, but as of current documentation it is limited to a small, Apple-curated set of first-party apps — no confirmed evidence it drives `DynamicTypeSize` for arbitrary third-party SwiftUI apps yet.
- **Practical rule**: do not assume a Mac app gets free Dynamic Type scaling from `Font.TextStyle` alone. Use `@ScaledMetric` to scale custom numeric values (padding, icon size, custom font sizes) proportionally — the reliable, cross-platform mechanism, including on Mac. Verify visually at multiple system text-size settings.

## Anti-Patterns

- Defaulting to Time Profiler for a memory or redraw problem instead of the matching template
- Synchronous network/disk I/O, unbounded decode, or unbounded main-context fetch on `@MainActor`
- Relying on Default-Actor-Isolation=MainActor and then running heavy synchronous work "for free" on the main actor
- `Task.detached` as the default background choice; `DispatchSemaphore.wait()` on the main thread
- Heavy work in `applicationDidFinishLaunching`/`App.init`; eager singleton graphs at launch
- Polling where change notifications exist; timers without tolerance
- Custom `NSView`/control with a label but no role/value/actions; UI never run through the Accessibility Inspector audit or `performAccessibilityAudit`
- Assuming iOS-style Dynamic Type from `Font.TextStyle`; not backing custom sizing with `@ScaledMetric`
