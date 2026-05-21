# Flutter Design System

**Priority: P0 (CRITICAL)**

## Context Discovery (Mandatory)

Before any UI work, investigate the root configuration:

```dart
// Check main.dart
MaterialApp(
  theme: VThemeData.light().toThemeData(), // ← Theme-Driven: use theme.textTheme
  ...
)
```

Determine the project's DLS pattern:
- **Theme-Driven (Adaptive)**: `VThemeData(...).toThemeData()` → use `Theme.of(context).textTheme`
- **Token-Driven (Static)**: Use static tokens (`VTypography.*`) only when no global theme bridge exists, or when defining the theme itself.

## Mandatory Token Usage

### Colors

```dart
// ❌ Forbidden
Color(0xFF2196F3)
Colors.blue

// ✅ Enforced
VColors.primary      // Modular DLS
AppColors.primary    // Monolithic DLS
context.theme.primaryColor
```

### Spacing

```dart
// ❌ Forbidden
SizedBox(height: 16)
EdgeInsets.all(24)

// ✅ Enforced
SizedBox(height: VSpacing.md)
EdgeInsets.all(VSpacing.lg)
```

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

### Typography

```dart
// ❌ Forbidden
TextStyle(fontSize: 20, fontWeight: FontWeight.bold)

// ✅ Preferred (adaptive Dark/Light mode support)
final theme = Theme.of(context);
Text('Title', style: theme.textTheme.headlineSmall)
Text('Body', style: theme.textTheme.bodyMedium)

// ⚠️ Static tokens — use only when context unavailable or defining the theme
VTypography.heading6
```

### Borders

```dart
// ❌ Forbidden
BorderRadius.circular(8)

// ✅ Enforced
VBorders.radiusMd
AppTheme.borderRadius
```

### Component Preference

```dart
// ❌ Avoid
ElevatedButton(...)

// ✅ Preferred (if DLS component exists)
VButton.primary(...)
```

## Anti-Patterns

- **No hex colors**: `Color(0xFF...)` strictly forbidden.
- **No color enums**: `Colors.blue` forbidden in UI code.
- **No magic spacing**: `SizedBox(height: 10)` forbidden.
- **No inline styles**: `TextStyle(fontSize: 14)` forbidden.
- **No raw widgets**: Don't use `ElevatedButton` when `VButton` exists.

---

## Modular DLS Pattern (V DLS — Ideal Architecture)

The gold standard for Flutter DLS architecture in large teams.

### Package Structure

```text
packages/v_dls/
├── lib/
│   ├── v_dls.dart (main export)
│   └── src/
│       ├── foundation/
│       │   ├── colors.dart        # 148 tokens
│       │   ├── spacing.dart       # 13 tokens
│       │   ├── typography.dart    # 20+ styles
│       │   ├── borders.dart
│       │   ├── shadows.dart
│       │   ├── animations.dart
│       │   └── breakpoints.dart
│       ├── components/
│       │   ├── buttons/v_button.dart
│       │   ├── inputs/v_text_field.dart
│       │   ├── layout/v_card.dart
│       │   └── ... (34 components)
│       ├── theme/
│       │   └── v_theme_data.dart
│       └── utils/
│           └── accessibility.dart
└── test/
```

### Foundation Token Reference

**Colors — `VColors`** (148 tokens):
```dart
VColors.primary50 through primary900  // Material Design scale
VColors.success, VColors.error, VColors.warning, VColors.info
VColors.gray50 through gray900
VColors.background, VColors.surface, VColors.surfaceVariant
VColors.darkBackground, VColors.darkSurface
```

**Spacing — `VSpacing`** (13 levels):
```dart
VSpacing.none     // 0px
VSpacing.xxs      // 2px
VSpacing.xs       // 4px
VSpacing.sm       // 8px
VSpacing.smMd     // 12px
VSpacing.md       // 16px  ← Base unit
VSpacing.mdLg     // 20px
VSpacing.lg       // 24px
VSpacing.xl       // 32px
VSpacing.xxl      // 40px
VSpacing.xxxl     // 48px
VSpacing.huge     // 64px
VSpacing.massive  // 128px
```

**Typography — `VTypography`**:
```dart
VTypography.heading1 to heading6
VTypography.bodyLarge, bodyMedium, bodySmall
VTypography.buttonLarge, buttonMedium, buttonSmall
VTypography.labelLarge, labelMedium, labelSmall
VTypography.caption, overline, code
```

**Borders — `VBorders`**:
```dart
VBorders.radiusMd, radiusLg, radiusXl, radiusFull
VBorders.widthThin, widthMedium, widthThick
VBorders.rectangleMd, rectangleLg, rectangleXl
VBorders.inputDefault, inputFocused, inputError, inputDisabled
```

### Perfect Component Example (ZERO hardcoded values)

```dart
class VButton extends StatelessWidget {
  final VButtonVariant variant;
  final VButtonSize size;

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      style: ElevatedButton.styleFrom(
        backgroundColor: theme.colorScheme.primary,     // ✅ Color from theme
        foregroundColor: theme.colorScheme.onPrimary,
        padding: EdgeInsets.symmetric(
          horizontal: VSpacing.lg,   // ✅ Spacing from tokens (24px)
          vertical: VSpacing.smMd,   // ✅ (12px)
        ),
        shape: VBorders.rectangleMd, // ✅ Border from tokens (8px radius)
        textStyle: VTypography.buttonMedium, // ✅ Typography (in DLS Package)
      ),
      child: content,
    );
  }
}
```

### When to Use Modular Pattern

- Large teams (multiple developers need consistent design)
- Design system exists (Figma/design tokens to implement)
- Planning for 50+ screens
- Multi-app (sharing DLS across multiple apps)

### Key Principles

1. **Modular Separation**: Each foundation aspect in its own file.
2. **Semantic Naming**: `primary500`, not `blue600`.
3. **Scale Coverage**: Complete 50-900 scales for colors.
4. **Component Encapsulation**: All DLS logic in components, not in app code.
5. **Zero Hardcoding**: Components must contain zero magic numbers.

---

## Monolithic DLS Pattern (Growing Projects)

A pragmatic, monolithic approach suitable for small/medium teams and MVPs.

### Structure

```text
lib/presentation/theme/
├── app_theme.dart   # 482 lines
└── app_colors.dart  # 218 lines
```

### Characteristics

**Pros:** Simple, all tokens in 2 files, easy to start.
**Cons:** Limited spacing tokens (only 3), growing file size, typography mixed with theme config.

### Token Examples

**Colors — `AppColors`**:
```dart
AppColors.primary       // #234455
AppColors.secondary     // #E5EBB1
AppColors.error
AppColors.warning
AppColors.success
AppColors.darkGray
AppColors.lightGray
```

**Spacing — `AppTheme`** (only 3 — expand to 8-10 levels as the app grows):
```dart
AppTheme.kPadding6   // 6px
AppTheme.kPadding12  // 12px
AppTheme.kPadding24  // 24px
```

**Typography**:
```dart
// ✅ PREFERRED: Use theme context for adaptive support
Text(
  'Title',
  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
    fontWeight: FontWeight.bold,
  ),
)
// ❌ AVOID: Raw token compositing in UI
// style: GoogleFonts.notoSans(fontSize: AppTheme.kTextH1, ...)
```

### When to Use Monolithic Pattern

- Small/medium teams (1-5 developers)
- MVP/Prototype (quick iteration needed)
- Simple apps (<30 screens)
- Starting DLS (growing into full design system)

### Evolution Path

1. Expand spacing tokens to 8-10 levels
2. Extract typography to dedicated class
3. Add borders/shadows as dedicated tokens
4. Migrate to modular package (V DLS style) when team grows

---

## Migration: Monolithic → Modular

1. Create `packages/your_dls/` structure
2. Move colors to `foundation/colors.dart`
3. Expand spacing from 3 → 13 tokens (follow VSpacing scale)
4. Extract typography to `foundation/typography.dart`
5. Create component wrappers (`YourButton` extends `ElevatedButton`)
