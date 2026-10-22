---
last_reviewed: 2026-10-23
---

# iOS UI & Accessibility

Scope: iPhone/iPad UI components, accessibility, input, and Liquid Glass. Strings and formatting → `<SKILLS>/macos/refs/localization.md` (platform-neutral).

## Dynamic Type

- Use text styles (`.font(.body)`, `.headline`) or `Font.custom(_:size:relativeTo:)`. Never fixed point sizes for text.
- Scale non-text metrics with `@ScaledMetric` (icon size, padding next to text).
- At accessibility sizes, switch horizontal layouts to vertical: `ViewThatFits`, or `@Environment(\.dynamicTypeSize)` with `.isAccessibilitySize`.
- No fixed frame heights around text. No `.lineLimit(1)` on body copy; truncation hides content at large sizes.
- Test at `AX5` (largest) and `xSmall`. Use the Xcode canvas variants or `dynamicTypeSize` previews.

## VoiceOver & Assistive Settings

- Icon-only buttons need `.accessibilityLabel`. Decorative images use `Image(decorative:)` or `.accessibilityHidden(true)`.
- Group a cell into one element with `.accessibilityElement(children: .combine)`; expose swipe actions and secondary buttons as `.accessibilityActions`.
- Custom controls declare traits (`.isButton`, `.isSelected`) and values (`.accessibilityValue`); adjustable controls implement `.accessibilityAdjustableAction`.
- Announce async results that change no focused element: `AccessibilityNotification.Announcement("Saved").post()`.
- Honour `accessibilityReduceMotion` (cross-fade instead of slide/zoom), `accessibilityReduceTransparency`, and `colorSchemeContrast == .increased`.
- Hit targets ≥ 44×44 pt; extend small visuals with `.contentShape(Rectangle())` and padding.
- Run `XCUIApplication().performAccessibilityAudit()` in UI tests → `refs/testing.md`.

## Liquid Glass (iOS 26+)

- System bars, tab bars, toolbars, sheets, and menus adopt glass automatically. Do not add backgrounds, blurs, or `toolbarBackground` colours that fight it.
- With the iOS 27 SDK, `UIDesignRequiresCompatibility` is ignored. There is no opt-out left.
- Custom floating controls: `.glassEffect()` (wrap neighbours in `GlassEffectContainer`), or `.buttonStyle(.glass)` / `.glassProminent`. Use glass for the navigation layer only, never for content cards or list rows.
- Content scrolls under bars; use `.safeAreaBar` / `.safeAreaInset` for custom bottom bars so scroll-edge effects work.
- Check every screen under Reduce Transparency and Increase Contrast; glass falls back to opaque there.

## Buttons & Actions

- One prominent action per screen (`.borderedProminent` or `.glassProminent`). Secondary actions use `.bordered` or plain.
- Destructive actions: `Button(role: .destructive)` plus `.confirmationDialog` when the loss is not undoable.
- Disable a button during its async work and show progress in place. Never allow a double submit.
- Toolbar items with `ToolbarItem(placement:)`; group with `ToolbarItemGroup`. Do not build custom nav bars.

## Bottom Sheets

- `.sheet` with `.presentationDetents([.medium, .large])` (or `.fraction` / `.height`) and `.presentationDragIndicator(.visible)` for multi-detent sheets.
- Keep the content behind interactive only when needed: `.presentationBackgroundInteraction(.enabled(upThrough: .medium))`.
- Do not override sheet backgrounds or corner radii on iOS 26+; partial-height sheets are glass by design.
- Content must scroll inside the smallest detent at the largest Dynamic Type size.
- Presentation rules (item-driven, one at a time, dismissal) → `refs/app-lifecycle-and-navigation.md`.

## Snackbars & Toasts

iOS has no native snackbar. When the product needs one:

- One host at the root: an `@Observable` `ToastCenter` injected with `.environment`, rendered with `.overlay(alignment: .bottom)` above the tab bar and inside the safe area.
- Queue messages; show one at a time; auto-dismiss after ≥ 4 s; pause on VoiceOver focus.
- Post an accessibility announcement for every toast.
- Toasts confirm; they never carry an error the user must act on. Actionable errors use inline messages or `.alert`.
- Undo toasts keep the action reversible until the toast closes.

## Lists & Input

- `List` or `LazyVStack` with stable IDs. `.refreshable` for pull-to-refresh, `.searchable` for search, `.swipeActions` for row actions (mirror them as accessibility actions).
- Forms: `@FocusState` to move between fields; `.submitLabel`; correct `keyboardType` and `textContentType` (`.oneTimeCode`, `.newPassword`, `.emailAddress`) so AutoFill works.
- `.scrollDismissesKeyboard(.interactively)` on scrolling forms. Never cover the focused field.
- Paste: use `PasteButton` instead of reading `UIPasteboard` programmatically, which shows a permission prompt.

## Haptics & Motion

- `.sensoryFeedback(.success, trigger:)` for meaningful state changes only: completion, error, selection change. Not on every tap.
- Animations respect Reduce Motion. Use `withAnimation` on state changes, not `.animation` without a value.

## Previews

- `#Preview` macro, never `PreviewProvider` in new code. Add variants for dark mode, the largest Dynamic Type size, and a right-to-left locale.
