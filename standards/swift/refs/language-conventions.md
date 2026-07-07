# Swift Language Conventions

Style and convention rules (P1) — naming, structure, and expression style.

## Naming (Swift API Design Guidelines)
- Clarity at the point of use; omit needless words; name by role, not type.
- Side-effect-free reads as noun (`sorted()`, `distance(to:)`); side-effecting reads as verb (`sort()`, `append(_:)`). Booleans read as assertions (`isEmpty`, `canSend`).
- Protocols: nouns for is-a (`Collection`); `-able`/`-ible`/`-ing` for capability (`Equatable`).
- First argument label: omit when the call reads as a grammatical phrase (`addSubview(x)`) or for value-preserving conversions (`Int64(int32)`); include prepositions (`move(from:to:)`).
- `UpperCamelCase` types/protocols; `lowerCamelCase` everything else; acronyms uniformly cased (`urlString`, `userID`).

## Structure
- One protocol conformance per `extension`, marked with `// MARK: -`. Keep core stored properties and initializers in the primary declaration.
- Trailing-closure syntax for the final closure; implicit `return` in single-expression bodies.
- `map`/`compactMap`/`filter` when they read clearly; loops when they don't (or when the body needs `break`/`continue`/`return`). `first(where:)` over `filter {}.first`; `contains(where:)` over `filter {}.count > 0`.
- Prefer interpolation over concatenation; raw strings (`#"..."#`) to avoid escaping; multiline literals (`"""`) for embedded text.
- Property wrappers only for reusable cross-cutting storage behavior — not as a substitute for a plain computed property. Author a custom `@resultBuilder` only for a genuine declarative DSL, not to avoid an array literal.
- Omit `self.` except where required (or where the team formatter enforces otherwise).
