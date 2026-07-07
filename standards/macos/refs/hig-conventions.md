# macOS HIG Conventions — Appearance, Undo, Pasteboard & Intents

HIG conventions that don't belong to a more specific ref: Liquid Glass appearance, color/iconography rules, drag & drop, undo, pasteboard, and App Intents. Window/menu/document conventions live in `refs/windows-and-scenes.md`; accessibility conventions in `refs/performance-accessibility.md`.

## Appearance (Liquid Glass)

- Standard controls adopt Liquid Glass automatically on the current SDK; custom-drawn chrome does not — audit every screen after an SDK bump. AppKit: content goes inside `NSGlassEffectView.contentView`, never behind glass as a sibling.
- Colors from the asset catalog with dark-mode and increased-contrast variants; semantic system colors for standard chrome; SF Symbols for iconography; no hardcoded pixel sizes.
- Drag & drop wherever content moves (`draggable`/`dropDestination` + `Transferable`).

## Undo, Pasteboard & Intents

- Content-mutating user actions register undo (`NSUndoManager` scoped per document/window, weak targets); ⌘Z/⇧⌘Z must work.
- Copy/paste for any selectable content, via the same `Transferable` types as drag & drop.
- Expose key app actions as App Intents — Shortcuts, Spotlight, and Apple Intelligence surface through them.
