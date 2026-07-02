# Swift Testing

## Swift Testing vs XCTest

| | Swift Testing | XCTest |
|---|---|---|
| Import | `import Testing` | `import XCTest` |
| Test declaration | `@Test` function (any name, any file) | `func test...()` inside an `XCTestCase` subclass |
| Assertions | `#expect(...)`, `#require(...)` | `XCTAssert...` family |
| Grouping | `@Suite` (struct/class/actor) | `XCTestCase` subclass |
| Parameterized tests | Native (`@Test(arguments:)`) | Manual loops or third-party helpers |
| Parallel execution | Default | Opt-in, coarser-grained |
| UI testing (`XCUIApplication`) | Not supported | Required |
| Performance testing (`measure { }`, `XCTMetric`) | Not supported | Required |
| Availability | Swift 6 toolchain / Xcode 16+ | All Xcode versions |

- Both frameworks can live in the same test target; `swift test` and Xcode run and merge results from both. Incremental adoption is practical — no forced big-bang migration.
- **Use Swift Testing for new code**: unit tests, integration tests, async tests, parameterized tests.
- **Keep XCTest** for: UI automation (`XCUIApplication`/`XCUIElement`), performance tests (`measure { }`, `XCTMetric`), and existing large XCTest suites where the migration cost isn't currently justified. Also reach for XCTest where a third-party CI/coverage/report integration is only wired up for `XCTestCase` until it catches up.

## `@Test` and `@Suite`

```swift
import Testing

@Suite("User repository")
struct UserRepositoryTests {
    @Test("returns nil when user not found")
    func userNotFound() async throws {
        let repo = UserRepository(dataSource: MockDataSource())
        #expect(await repo.getUser(id: "missing") == nil)
    }
}
```
- `@Test` functions don't need a `test` name prefix and aren't required to live in a type — a free function annotated `@Test` is a valid test.
- `@Suite` types can be a `struct`, `class`, or `actor`; a fresh instance is created per test by default (matching XCTest's per-test isolation), so shared mutable fixtures need explicit lifetime management (an `init`/`deinit` pair, or a shared fixture you deliberately opt into).
- Traits customize behavior: `.tags(_:)`, `.enabled(if:)`, `.disabled(_:)`, `.timeLimit(_:)`, `.bug(_:)`.

## `#expect` and `#require`

- `#expect(condition)` records a failure but **continues** the test — use for assertions where you want to see multiple failures in one run.
- `#require(expression)` **stops** the test immediately on failure — use for preconditions the rest of the test depends on (typically unwrapping an optional):
```swift
@Test func videoHasMetadata() async throws {
    let video = try #require(await library.video(named: "Beach"))
    #expect(video.duration > 0)
}
```
- `#expect(throws:)` / `#require(throws:)` assert that an expression throws (optionally, a specific error type):
```swift
#expect(throws: ValidationError.self) {
    try validate(input: "")
}
```
- Exit tests (`#expect(processExitsWith:)`) cover `fatalError`/`precondition` paths that would otherwise crash the runner.

## Parameterized Tests

```swift
@Test("Valid emails pass validation", arguments: [
    "user@example.com",
    "a.b+c@sub.example.co",
])
func validEmail(_ address: String) throws {
    #expect(try EmailValidator.isValid(address))
}
```
- Each argument produces an independently reported, independently parallelizable test case — failures identify exactly which input failed, unlike a hand-rolled `for` loop inside a single XCTest method.
- Supports zipped/cross-producted argument collections for multi-parameter cases (`arguments: names, ages`). Use `zip` to pair inputs — passing two bare collections cross-products them, which is rarely what you want.

## Async & Concurrency

- `@Test` functions can be `async throws` directly — no `XCTestExpectation`/`waitForExpectations` ceremony.
- Tests run in parallel by default (in-process, across suites); apply `.serialized` to a `@Suite` (or a parameterized `@Test`) when shared mutable state (a shared database, a singleton) makes parallel execution unsafe, rather than disabling parallelism project-wide. `.serialized` applies recursively to everything nested in that suite. Treat it as an escape hatch, not a default.

## Mocking via Protocols & Dependency Injection

- Depend on protocols at architectural seams (network client, persistence, clock) and inject a fake/mock conforming implementation in tests — constructor injection over a shared/singleton default.
```swift
protocol Clock {
    func now() -> Date
}

struct SystemClock: Clock { func now() -> Date { Date() } }

struct FixedClock: Clock {
    let fixedDate: Date
    func now() -> Date { fixedDate }
}
```
- Prefer hand-written fakes/stubs (or a struct-of-closures) over a mocking framework with runtime interception — Swift's `final`-by-default classes and value types make protocol-based fakes the idiomatic default. If the codebase already generates mocks, follow it.
- For `async` dependencies, make the protocol's methods `async throws` so both the real and fake implementations share the same call shape at use sites.

## Snapshot & Coverage

- Snapshot testing (e.g. swift-snapshot-testing): set record mode to `.never` on CI so a missing reference fails instead of silently re-recording; pin the OS/environment that generates references.
- Coverage: aim 70–90% on logic modules, measured per module; gate PRs on **no-drop**, not an absolute number.

## Migration Guidance (XCTest → Swift Testing)

- Migrate leaf/unit-test files first; leave UI and performance test targets on XCTest.
- Mechanical mappings: `XCTAssertEqual(a, b)` → `#expect(a == b)`; `XCTAssertNil(x)` → `#expect(x == nil)`; `XCTAssertThrowsError` → `#expect(throws:)`; `XCTUnwrap` → `#require`; `setUp()`/`tearDown()` → the suite type's `init()`/`deinit`.
- Don't migrate a suite purely for the sake of migrating — prioritize suites that would actually benefit from parameterization or parallelism.

## Anti-Patterns

- Writing new unit tests in XCTest when Swift Testing is available and nothing UI/performance-specific is required
- Hand-rolled `for` loops over test cases inside one XCTest method instead of `@Test(arguments:)` parameterization
- `#expect` used for a precondition the rest of the test depends on (should be `#require`, so failure stops the test instead of cascading into unrelated failures)
- Shared mutable fixture state across parallel `@Test` cases without `.serialized`
- Mocking frameworks that rely on runtime method swizzling instead of protocol-based fakes
- Migrating XCTest UI/performance test targets to Swift Testing (unsupported)
- Snapshot suites left in auto-record mode on CI
