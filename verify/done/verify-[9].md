---
status: planned
---

# Verification Run [9] — Flutter Refs: Remove Conflicts & Gaps

> Following verify-[7] (Flutter archive) and the re-analysis of `standards/flutter/refs/`,
> this run fixes the two critical conflicts and three gap/cross-reference issues found in
> the consolidated ref files. **No content is deleted.** All changes are additive edits or
> minor demotions within the existing 14-file ref set. Nothing in `archive/flutter/` is
> touched. The goal is a ref set with no ambiguous routing decisions, no unguided pattern
> choices, and no rules that silently break when a developer reads only one file.

---

## 1. What Will Change

### Problems Before

Six issues were identified across `standards/flutter/refs/`:

| # | File(s) | Issue | Severity |
|---|---|---|---|
| A | `navigation.md` | `go_router` and `GetX` both marked P0 — mutually exclusive but equally weighted | **CRITICAL** |
| B | `state-management.md` | Three BLoC state templates (Union, Flat, Equatable) with no guidance on which to prefer | **CRITICAL** |
| C | `architecture.md` | Feature-Based and Layer-Based both P0 with no "when to use" decision guidance | Medium |
| D | `design-system.md` | Spacing token rules present but `Row(spacing:)` idiom absent — only in SKILL.md | Medium |
| E | `security.md` | `FlutterSecureStorage` shown as raw `const FlutterSecureStorage()` — not DI-registered | Medium |
| F | `error-handling.md` | No cross-reference to `networking.md § Token Refresh` for global HTTP concerns | Low |

### After

- A developer reading `navigation.md` can immediately tell which router applies to their project.
- A developer reading `state-management.md` knows which BLoC state template to start with.
- A developer reading `architecture.md` can pick a pattern from a decision table.
- A developer reading `design-system.md` is pointed to the idiomatic spacing preference.
- A developer reading `security.md` sees `FlutterSecureStorage` wired through DI.
- A developer reading `error-handling.md` knows where global HTTP handling lives.

No ref is restructured. Each change is a targeted addition or clarification within its existing file.

---

## 2. Execution Steps

### Step A — `navigation.md`: Resolve dual-P0 conflict

Add a **Router Decision Rule** block at the very top of the file (before the first `##`
section), containing:

```
## Router Decision Rule

Choose **one** routing framework per project. This file covers all three.

| Scenario | Framework | Priority in this file |
|---|---|---|
| New project | go_router | P0 (CRITICAL) |
| Existing auto_route project | auto_route | P1 (HIGH) |
| Existing GetX project | GetX Navigation | P1 (HIGH) — see also state-management.md § GetX |

Do not mix routing frameworks. If a project already uses GetX or auto_route, treat the
go_router sections as informational only.
```

Then find the GetX Navigation section header (or the line that marks it P0 CRITICAL) and
demote it to **P1 (HIGH)**, adding a note:
> "P1 for existing GetX projects. New projects should use go_router (P0 above)."

---

### Step B — `state-management.md`: Prefer Union BLoC state pattern

Find the `### Templates` section. It contains four subsections: `#### Freezed State (Union)`,
`#### Freezed State (Flat)`, `#### Event`, `#### BLoC`, and `#### Equatable Alternative`.
Make the following three targeted changes:

1. Rename `#### Freezed State (Union)` → `#### Freezed State (Union) ✅ PREFERRED`
2. Rename `#### Freezed State (Flat)` → `#### Freezed State (Flat) ⚠️ LIMITED USE`
3. Rename `#### Equatable Alternative` → `#### Equatable Alternative ⚠️ LEGACY`

Then insert the following guidance block **between** `#### Freezed State (Union)` and
`#### Freezed State (Flat)` (after the Union code block, before the Flat heading):

```
**Which to use:**
- **Union (preferred):** One named constructor is active at a time — impossible combinations
  like `isLoading=true` alongside `data!=null` cannot exist. Use this by default.
- **Flat:** Use only when multiple fields are genuinely orthogonal (e.g., a `searchTerm`
  string and an `isLoading` bool that coexist independently). Requires a `status` enum
  if states need disambiguation.
- **Equatable Alternative:** No code generation required. Use only when `build_runner` is
  unavailable. Prefer Freezed Union for all new code.
```

---

### Step C — `architecture.md`: Add "When to Use" decision table

Insert a **"Which Architecture to Use"** `##` section at the **top of the file**, before
`## Feature-Based Clean Architecture`. Insert it once — do not add it under each
pattern heading.

```
## Which Architecture to Use

| Criterion | Feature-Based | Layer-Based |
|---|---|---|
| Team size | Small–medium | Large |
| Feature ownership | Isolated, per-team | Shared across teams |
| Domain logic sharing | Minimal cross-feature sharing | Rich shared domain |
| Onboarding speed | Faster (locality of reference) | Slower (more abstraction) |
| Codebase scale | Up to ~30 features | 30+ features or complex domain |

**Default for new projects:** Feature-Based Clean Architecture.
Switch to Layer-Based when shared domain logic grows significantly across feature
boundaries or when a strict separation-of-concerns policy is required.
```

Both patterns remain P0 — the table guides the choice, not a hard rule.

---

### Step D — `design-system.md`: Add spacing idiom note

Find the **Spacing** section (the one with `VSpacing.*` tokens). At the end of that
section, before the next `##` heading, add:

````
**Idiomatic spacing (Flutter 3.10+):**
Prefer the `spacing` parameter on `Row`/`Column` over inserting gap widgets between
children:

```dart
// ✅ Preferred
Row(spacing: VSpacing.md, children: [...])

// ⚠️ Fallback — use only when `spacing` cannot express the layout
Row(children: [
  ChildA(),
  SizedBox(width: VSpacing.md),
  ChildB(),
])
```

See SKILL.md § P1 Idiomatic Flutter for the full preference hierarchy.
````

---

### Step E — `security.md`: Add DI module for FlutterSecureStorage

Find the **Secure Storage** section (where `const FlutterSecureStorage()` appears).
Directly after the raw instantiation example, add:

```dart
// Preferred: register via DI module so it can be injected and mocked
@module
abstract class SecurityModule {
  @lazySingleton
  FlutterSecureStorage get secureStorage => const FlutterSecureStorage();
}

// Inject it via constructor (never call getIt<FlutterSecureStorage>() inline)
class AuthLocalDataSource {
  AuthLocalDataSource(this._storage);
  final FlutterSecureStorage _storage;
}
```

Add a cross-reference note:
> "See `refs/dependency-injection.md § Third-Party Modules` for the full module
> registration pattern."

---

### Step F — `error-handling.md`: Add cross-reference to networking.md

Find the **Repository Error Mapping** section (the one with `DioException → ApiFailure`
or the repository `try/catch` pattern). At the start of that section, add a scoping note:

```
> **Scope:** This section covers domain-specific failure mapping at the repository layer.
> For global HTTP concerns (token refresh, 401 handling, auth headers), see
> `refs/networking.md § Token Refresh Pattern` — those belong in an interceptor, not here.
```

---

## 3. Success Criteria

### Step A — navigation.md
- [ ] A "Router Decision Rule" block exists at the top of `navigation.md`, before `## go_router`
- [ ] The decision table has rows for go_router (P0), auto_route (P1), and GetX (P1)
- [ ] GetX Navigation section is marked P1 (HIGH) (not P0)
- [ ] The go_router section remains P0 (CRITICAL)
- [ ] The GetX row directs readers to `state-management.md § GetX`

### Step B — state-management.md
- [ ] `#### Freezed State (Union)` heading includes `✅ PREFERRED`
- [ ] `#### Freezed State (Flat)` heading includes `⚠️ LIMITED USE`
- [ ] `#### Equatable Alternative` heading includes `⚠️ LEGACY`
- [ ] A guidance block sits between the Union and Flat subsections covering all three options
- [ ] The guidance names the Equatable condition: use only when `build_runner` is unavailable

### Step C — architecture.md
- [ ] A `## Which Architecture to Use` section exists at the top of the file, before `## Feature-Based Clean Architecture`
- [ ] The section appears exactly once (not duplicated under each pattern)
- [ ] The table includes at least 4 decision criteria (team size, ownership, domain sharing, scale)
- [ ] "Default for new projects: Feature-Based" is stated explicitly
- [ ] Both patterns remain P0 — the table guides, does not mandate

### Step D — design-system.md
- [ ] The Spacing section contains a note on `Row(spacing: VSpacing.md)`
- [ ] A `// ✅ Preferred` / `// ⚠️ Fallback` code example is present
- [ ] A cross-reference to `SKILL.md § P1 Idiomatic Flutter` is present

### Step E — security.md
- [ ] A `SecurityModule` DI snippet follows the raw `FlutterSecureStorage()` example
- [ ] The snippet shows constructor injection (not inline `getIt<>()` call)
- [ ] A cross-reference to `refs/dependency-injection.md § Third-Party Modules` is present

### Step F — error-handling.md
- [ ] A scoping note at the start of the Repository Error Mapping section is present
- [ ] The note names `refs/networking.md § Token Refresh Pattern` explicitly
- [ ] The note clarifies that interceptors handle global concerns, repositories handle domain mapping

### No regressions
- [ ] No other sections of any ref file were modified beyond those listed above
- [ ] `SKILL.md`, `_INDEX.md`, and all other refs (`cicd`, `concurrency`, `localization`,
      `navigation` [go_router rules], `notifications`, `testing`) are unchanged
- [ ] `archive/flutter/` is untouched
- [ ] `CHANGELOG.md` updated

---

## 4. Verification Notes for the Executing Agent

1. **Do not restructure files.** Every change is an insertion into an existing section —
   find the anchor point described in §2 and insert there. No sections are renamed,
   reordered, or removed.

2. **Steps A and B have rename-sensitive changes.** In `navigation.md`, the GetX priority
   label must change from P0 to P1. In `state-management.md`, three subsection headings
   must be renamed in-place. Confirm each with a read after editing — do not assume edits
   succeeded.

3. **Steps B–F are additive only.** If the guidance note or cross-reference already
   exists (from a prior run), skip that step and mark it complete — do not duplicate.

4. **Run in order A → B → C → D → E → F**, then read each modified file in full to
   confirm the insertions are coherent with surrounding content (no formatting breaks,
   no mid-paragraph injections).

5. Update `CHANGELOG.md` last, after all 6 steps are confirmed complete.
