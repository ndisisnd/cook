---
name: dart
description: Dart 3.x language standards and code quality conventions. Use when writing or reviewing any Dart code — null safety, patterns, sealed classes, records, class modifiers, naming, immutability, collections, async, and import organisation.
metadata:
  triggers:
    files:
      - '**/*.dart'
    keywords:
      - sealed
      - record
      - switch
      - pattern
      - '!'
      - late
      - async
      - extension
      - naming
      - convention
      - trailing comma
      - import
      - tear-off
---

# Dart Standards

## Priority: P0 — Language Correctness

### Null Safety
- Never use `!` unless you can prove non-null via a prior `if` or `assert`.
- Prefer `?.`, `??`, and null-aware patterns over forced unwrapping.
- `AVOID late` if you need to check whether the variable was initialised — use nullable + null-check instead.
- `DON'T` explicitly initialise variables to `null`; let the type system express optionality.

### Immutability
- Use `const` > `final` > `var`. Use `@freezed` for data classes.
- Prefer `final` for all class members. Use `var` only for locally-obvious short-lived locals.
- `AVOID` public `late final` fields without initializers.

### Pattern Matching (Dart 3.x)
Use `switch` expressions with exhaustive patterns and destructuring. Supported pattern types:

| Pattern | Example |
|---|---|
| Constant | `case 42:` |
| Variable | `case var x:` |
| Wildcard | `case _:` |
| Object | `case Circle(radius: var r):` |
| Record | `case (String name, int age):` |
| List | `case [first, ...rest]:` |
| Map | `case {'key': var v}:` |
| Logical-or | `case 1 || 2:` |
| Guard | `case var x when x > 0:` |

```dart
String describe(Shape s) => switch (s) {
  Circle(radius: var r) when r > 10 => 'large circle',
  Circle(radius: var r) => 'circle r=$r',
  Rectangle(width: var w, height: var h) => '${w}x$h rect',
};
```

### Records
- Use records for returning multiple values: `(String, int)`.
- Use named fields for clarity beyond two elements: `({String name, int age})`.

### Class Modifiers (Dart 3.x)
Choose the right modifier to express API intent explicitly:

| Modifier | Extends outside lib | Implements outside lib | Use for |
|---|---|---|---|
| `sealed` | no | no | Exhaustive domain state (enables exhaustive switch) |
| `final` | no | no | Closed hierarchy — no extension or implementation |
| `base` | yes | no | Allow inheritance, prevent external implementation |
| `interface` | no | yes | Pure contracts — implementation only |

```dart
sealed class AuthState {}
final class Authenticated extends AuthState { final User user; Authenticated(this.user); }
final class Unauthenticated extends AuthState {}
```

### Mixins
- Use `mixin` for behaviour shared across unrelated class hierarchies.
- Use `mixin class` (Dart 3.0) when the type must also be usable as a standalone class.
- Prefer `mixin` over `abstract class` when no constructor is needed.

### Enhanced Enums (Dart 2.17+)
Enums can have fields, constructors, and methods. Prefer over utility classes with static constants.

```dart
enum Status {
  active('Active'),
  inactive('Inactive');

  const Status(this.label);
  final String label;
}
```

### Extensions
- Use `extension` to add utility methods to third-party or built-in types.
- Always name extensions (`extension StringX on String`) — unnamed extensions are harder to import selectively.

### Wildcards (Dart 3.7+)
Use `_` for unused variables in declarations and patterns.

### Async
- Prefer `async/await` over raw `Future.then`.
- Use `unawaited()` for intentional fire-and-forget; never silently discard a future.
- `DON'T` mark a function `async` if it contains no `await` — it adds overhead with no benefit.
- `AVOID` using `Completer` directly; prefer `async/await` or `StreamController`.
- `AVOID` `FutureOr<T>` as a return type.
- `AVOID` returning nullable `Future`, `Stream`, or collection types from public APIs.

### Error Handling
- Use `on ExceptionType catch (e)` — never bare `catch` without `on` (swallows everything).
- `DON'T` silently discard caught errors.
- Throw `Error` subclasses only for programmatic errors (bugs). Use `Exception` for recoverable runtime conditions.
- Use `rethrow` to re-propagate after partial handling; never re-throw the caught object manually.
- Use `assert()` for development-time invariants — stripped in production.

### Types
- No `dynamic`. Use `Object`, `Object?`, or generics.
- Annotate return types and parameter types on all public declarations.
- `DON'T` redundantly annotate initialised local variables — let inference work.
- Use `typedef` for named type aliases (`typedef UserId = String`). Prefer inline function type syntax in parameter positions over typedef.

### Members & Constructors
- Use initializing formals: `const User({required this.name})`.
- Use `;` not `{}` for empty constructor bodies.
- Never use `new`.
- `DON'T` use `this.` except to redirect constructors or avoid shadowing.
- `DON'T` perform complex calculations or async work inside constructors.
- Use a getter for pure computations: `int get invoiceTotal =>` not `int calcTotal()`.

---

## Priority: P1 — Style & Conventions

### Naming
- Types and extensions: `UpperCamelCase`
- Members, variables, parameters: `lowerCamelCase`
- Files, packages, directories: `lowercase_with_underscores`
- Import prefixes: `lowercase_with_underscores`
- Constants: `lowerCamelCase` (not `SCREAMING_CAPS`)
- Capitalise acronyms longer than two letters as words: `HttpRequest`, `parseUrl`
- `DON'T` use a leading `_` on non-private identifiers.
- Name value-object converters for their target context: `get apiFilterType` not `get filterType`.

### Scoping
- No top-level mutable state. Encapsulate in a class or inject via DI.
- Library-private identifiers use `_` prefix.

### Strings
- Prefer single quotes. Use double quotes only when the string itself contains a single quote.
- Prefer interpolation over concatenation: `'Hello $name'` not `'Hello ' + name`.
- Adjacent string literals can be concatenated without `+`.
- Omit curly braces in interpolation unless required: `'$name'` not `'${name}'`.

### Trailing Commas
Always use trailing commas for multi-line argument lists and collection literals.

### Expression Bodies
Prefer `=>` for single-expression functions and getters.

### Collections
- Use `.isEmpty` / `.isNotEmpty` — never `.length == 0`.
- Use collection `if`, `for`, and spread `...` for composable collections.
- Type empty collections explicitly: `<String>[]`, `<String, User>{}`.
- Prefer `.map`, `.where`, `.fold`, `.any` over manual loops where clarity wins.
- Use `.firstOrNull`, `.lastOrNull`, `.elementAtOrNull(i)` for safe indexed access.
- `DON'T` use `Iterable.forEach()` with a function literal — use `for` loops or tear-offs.
- `DON'T` use `cast()` when a nearby operation will do.

### Imports
- Group order: `dart:` → `package:` → relative. Sort each section alphabetically.
- Use relative imports for intra-package files; never `package:app/...` within the same package.
- Specify exports in a separate section after all imports.

### Tear-offs
Prefer `list.forEach(print)` over `list.forEach((e) => print(e))`.

---

## Anti-Patterns

- `!` without a prior null-proof guard
- `var` for class members
- `dynamic` anywhere
- `async` on a function with no `await`
- Bare `catch` without `on`
- Global mutable state
- `new` keyword
- Package imports within the same package
- `FutureOr<T>` as a return type
- Logic or async work inside constructors
- Zero-argument methods for pure computations — use a getter

---

## References

- [tooling](refs/tooling.md)
- [testing](refs/testing.md)
