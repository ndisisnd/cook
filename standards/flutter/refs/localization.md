# Flutter Localization (easy_localization)

**Priority: P1 (STANDARD)**

## Format Selection

- **CSV** (Recommended for teams with translators): Google Sheets compatibility via `sheet_loader_localization`. Store in `assets/langs/`.
- **JSON** (Developer-friendly): Nested structure support with IDE validation. Store in `assets/translations/`.

## Structure

```text
# CSV Format (Google Sheets workflow)
assets/langs/langs.csv

# OR JSON Format (nested keys)
assets/translations/
├── en.json
└── vi.json
```

## Implementation Workflow

1. **Initialize** — Call `await EasyLocalization.ensureInitialized()` before `runApp`.
2. **Wrap root** — Wrap app with `EasyLocalization` widget specifying supported locales and path.
3. **Translate strings** — Use `.tr()` extension on keys (e.g., `'welcome'.tr()`).
4. **Switch locale** — Change via `context.setLocale(Locale('vi'))`.
5. **Handle plurals** — Use `plural()` for quantity-dependent strings.
6. **Sync translations** — Use `sheet_loader_localization` to auto-generate CSV/JSON from Google Sheets.

## Anti-Patterns

- **No hardcoded strings**: Always use translation keys from assets.
- **No manual localization calls**: Use `easy_localization` `.tr()` extension.
- **No mismatched keys**: Ensure keys are identical across all locale-specific files.

## Bootstrap Example

```dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await EasyLocalization.ensureInitialized();
  runApp(
    EasyLocalization(
      supportedLocales: const [Locale('en'), Locale('vi')],
      path: 'assets/translations',
      child: const MyApp(),
    ),
  );
}
```

## Usage

```dart
Text('welcome'.tr());                       // Simple lookup
Text('greeting'.tr(args: [userName]));      // With parameters
Text(plural('items_count', itemCount));     // Pluralization
```

## Google Sheets Loader

Automating translation updates from Google Sheets using `sheet_loader_localization`.

### Configuration (`pubspec.yaml`)

```yaml
dev_dependencies:
  sheet_loader_localization: ^0.1.0

sheet_loader_localization:
  doc_id: 'your_google_sheet_id_here'
  sheet_id: '0'                # Usually 0 for first sheet
  output_path: 'assets/langs' # For CSV format
  output_format: 'csv'        # Use 'json' for JSON format
```

### Sheet Format

| key            | en            | vi         |
| :------------- | :------------ | :--------- |
| welcome        | Welcome!      | Chào mừng! |
| login.button   | Login         | Đăng nhập  |
| errors.network | Network Error | Lỗi mạng   |

### Sync Command

```bash
flutter pub run sheet_loader_localization:main
```
