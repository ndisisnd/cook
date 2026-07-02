# macOS Localization & Formatting

Localize from the first line of UI, even a single-locale app — retrofitting concatenated strings and hardcoded formats later is far more expensive than doing it right up front.

## String Catalogs (`.xcstrings`)

- Use **String Catalogs** (`.xcstrings`, Xcode 15+) as the single source of user-facing strings — they replace `.strings`/`.stringsdict` and auto-extract keys from `String(localized:)` at build time.
- Every user-visible string goes through `String(localized:)` with a **comment** giving the translator context:
```swift
Text(String(localized: "cart.checkout.button", defaultValue: "Check Out",
            comment: "Title of the button that starts payment"))
```
- **Never build a sentence by concatenating fragments.** Word order, gender, and grammar differ per language — `"You have " + count + " items"` is unlocalizable. Put the whole sentence in the catalog with interpolation.
- **Plurals via catalog plural variants**, not `count == 1 ? "item" : "items"`. String Catalogs express plural rules per language (many languages have more than two plural categories — zero/one/two/few/many/other):
```swift
Text("^[\(count) item](inflect: true)")   // or a plural variation in the catalog
```
- Keys are stable identifiers; the default value is the source-language text. Don't reuse one key for two different meanings just because the English happens to match.

## Formatting (`FormatStyle`)

- All user-facing dates, numbers, currency, measurements, and lists go through `FormatStyle` / `.formatted()` — it is locale-aware, respects the user's region settings, and handles grouping/decimal separators correctly:
```swift
price.formatted(.currency(code: "USD"))
date.formatted(.dateTime.year().month().day())
count.formatted()                       // locale-correct digit grouping
names.formatted(.list(type: .and))      // "A, B, and C"
```
- **Never `String(format:)` for user-facing numbers** — it ignores locale (wrong decimal/grouping separators) and is easy to get wrong.
- **Wire formats (persistence, network, filenames) must be locale-independent**: ISO 8601 (`Date.ISO8601FormatStyle`) or a formatter pinned to `en_US_POSIX`. Never round-trip a user-facing formatted string back into data.
- `DateFormatter`/`NumberFormatter` are **expensive to create** — cache them; never allocate one inside a SwiftUI `body`, a `List` row builder, or a tight loop. `FormatStyle` values are cheaper and the preferred modern path.

## Testing Localization

- **Pseudo-localization**: run the app under a pseudo-language (Scheme → Options → App Language → an accented/expanded pseudo-locale, or `-AppleLanguages`) to surface hardcoded strings, truncation, and layout that breaks under ~30–40% text expansion — before any real translation exists.
- **RTL**: test a right-to-left language (Arabic/Hebrew, or the RTL pseudo-language). Use leading/trailing layout (not left/right); SF Symbols and system layout flip automatically, custom-drawn chrome does not.
- Launch with `-AppleLanguages "(ar)"` / `-AppleLocale "ar_SA"` as scheme arguments to force a locale for a test run.
- Verify number/date/currency rendering in at least one non-US locale (e.g. `de_DE` uses `.` for thousands and `,` for decimals — the inverse of `en_US`).

## Anti-Patterns

- Hardcoded English string literals in UI
- Building sentences by string concatenation
- `count == 1 ? "item" : "items"` instead of catalog plural variants
- `String(format:)` for user-facing numbers/dates; locale-dependent formatting for wire/persistence data
- `DateFormatter`/`NumberFormatter` allocated inside `body`/row builders instead of cached
- Left/right (instead of leading/trailing) layout that breaks under RTL
- Shipping without a single pseudo-localization or non-US-locale pass
