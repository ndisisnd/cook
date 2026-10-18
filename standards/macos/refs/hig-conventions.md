---
last_reviewed: 2026-10-18
---

# macOS HIG Conventions — Appearance, Layout, Undo, Pasteboard & Intents

HIG conventions that don't belong to a more specific ref. Window/menu/document conventions live in `refs/windows-and-scenes.md`; accessibility in `refs/performance-accessibility.md`.

## Appearance (Liquid Glass, macOS 26+)

- Standard controls, toolbars, and sidebars adopt Liquid Glass automatically on the current SDK; custom-drawn chrome does not — audit every screen after an SDK bump.
- Custom glass in SwiftUI: `.glassEffect()` (optionally `.glassEffect(.regular, in: .capsule)`); group neighbouring glass elements in a `GlassEffectContainer` so they render and morph together. Glass is for the navigation/control layer floating above content — never on content itself, and never glass stacked on glass.
- AppKit: content goes inside `NSGlassEffectView.contentView`, never behind glass as a sibling.
- Gate glass APIs with `#available(macOS 26, *)` on a lower floor and fall back to materials.
- Colors from the asset catalog with dark-mode and increased-contrast variants; semantic system colors for standard chrome; SF Symbols for iconography; no hardcoded pixel sizes.

## Window Layout

- **Sidebar**: `NavigationSplitView` (two or three columns) for source-list apps; let the sidebar list take the system sidebar style. Set widths with `.navigationSplitViewColumnWidth(min:ideal:max:)`; keep the sidebar collapsible and the toggle in the toolbar.
- **Toolbar**: `.toolbar { ToolbarItem(placement:) { … } }` with semantic placements (`.primaryAction`, `.navigation`, `.principal`) rather than manual spacing. Every toolbar action also exists in the menu bar. Allow customization (`.toolbar(id:)`) for toolbars with many items.
- **Table**: `Table(rows, selection: $selection, sortOrder: $sortOrder)` for multi-column data — sortable columns, multi-select, and a `.contextMenu(forSelectionType:)` acting on the selection. Not a `List` of hand-laid `HStack`s.
- **Settings**: the `Settings` scene with a `TabView` of panes; open it with `SettingsLink` or `@Environment(\.openSettings)`. Changes apply immediately — no OK/Apply buttons. Store values in `@AppStorage`.

## Drag & Drop, Undo, Pasteboard & Intents

- Drag & drop wherever content moves (`draggable`/`dropDestination` + `Transferable`).
- Content-mutating user actions register undo (`NSUndoManager` scoped per document/window, weak targets); ⌘Z/⇧⌘Z must work.
- Copy/paste for any selectable content, via the same `Transferable` types as drag & drop.
- Expose key app actions as App Intents — Shortcuts, Spotlight, and Apple Intelligence surface through them.
