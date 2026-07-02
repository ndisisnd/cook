# Swift Interop — C / Objective-C / CoreFoundation

Bridging boundaries are where Swift's safety guarantees stop. Ownership, nullability, and lifetime become your responsibility again — get them wrong and you get the classic crash/leak pairs below.

## CoreFoundation Ownership (`Unmanaged`)

CF functions return `Unmanaged<T>` when the compiler can't infer ownership. Which accessor you call depends on the function's naming rule:

- **Create Rule** — functions with `Create` or `Copy` in the name return an object you **own** (+1 retain). Take it with `takeRetainedValue()` — this consumes the +1, and ARC will release it. Using `takeUnretainedValue()` here **leaks**.
- **Get Rule** — functions with `Get` in the name return an object you **do not own** (borrowed). Take it with `takeUnretainedValue()`. Using `takeRetainedValue()` here **over-releases** → crash.

```swift
// Create/Copy → owned → takeRetainedValue
let url = CFURLCreateWithString(nil, "https://example.com" as CFString, nil)!
    .takeRetainedValue()

// Get → borrowed → takeUnretainedValue
let allocator = CFAllocatorGetDefault().takeUnretainedValue()
```

This is the single most common CF bug — mismatching the rule leaks or crashes. When in doubt, check the function's documented ownership, not its return type.

## Pointer Lifetime

- Pointers vended by `withUnsafeBytes`, `withUnsafeMutableBufferPointer`, `withExtendedLifetime`, etc. are valid **only inside the closure**. Never let the pointer (or anything derived from it) escape the closure — the buffer may be deallocated or moved the moment the closure returns.
- Don't take the address of a Swift value and stash it; there's no guarantee of a stable address for a Swift variable across statements.
- When a C API needs a buffer to outlive a single call, allocate it explicitly (`UnsafeMutablePointer.allocate(capacity:)`) and `deallocate()` it deterministically — pair them like `defer`.

## Objective-C Nullability & Bridging

- Audit imported Obj-C/C headers for nullability. An unannotated Obj-C pointer imports into Swift as an implicitly-unwrapped optional (`T!`) — a hidden force-unwrap that crashes on an unexpected `nil`. Annotate headers with `NS_ASSUME_NONNULL_BEGIN`/`_END` and explicit `nullable`/`nonnull` so the Swift side gets honest optionals.
- Treat a bridged `T!` as `T?` and unwrap it defensively at the boundary rather than trusting the annotation.

## `@objc` / `dynamic` Discipline

- Add `@objc` / `dynamic` **only** where the Obj-C runtime genuinely needs it: selector-based APIs (`#selector`, target/action), KVO, Interface Builder outlets/actions. Each one opts out of static dispatch and Swift optimizations.
- Never blanket-annotate a class `@objcMembers` "just in case" — it exposes and de-optimizes every member.

## KVO in Swift

- Prefer the block-based `observe(_:options:changeHandler:)` API over manual `observeValue(forKeyPath:...)`.
- It returns an `NSKeyValueObservation` token — **retain it** (store it on `self`); when the token deallocates, the observation stops. A dropped token silently stops observing.

```swift
final class Model: NSObject {
    @objc dynamic var progress: Double = 0
}

final class Watcher {
    var token: NSKeyValueObservation?
    func watch(_ model: Model) {
        token = model.observe(\.progress, options: [.new]) { _, change in
            print(change.newValue ?? 0)
        }
    }
}
```

## Anti-Patterns

- `takeUnretainedValue()` on a `Create`/`Copy` result (leak) or `takeRetainedValue()` on a `Get` result (over-release crash)
- Letting an `Unsafe*Pointer` from a `withUnsafe...` closure escape the closure
- Trusting an unannotated bridged `T!` instead of unwrapping it defensively
- `@objc`/`dynamic`/`@objcMembers` applied where the runtime doesn't require it
- Discarding the `NSKeyValueObservation` token returned by block-based `observe`
