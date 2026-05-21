# Flutter Security (OWASP Mobile)

**Priority: P0 (CRITICAL)**

## Implementation Workflow

1. **Store secrets securely** — Use `flutter_secure_storage` for tokens/PII. Never use `shared_preferences` for sensitive data.
2. **Externalize secrets** — Never store API keys in Dart code. Use `--dart-define` or `.env` files.
3. **Obfuscate releases** — Build `--obfuscate --split-debug-info=./symbols`. Deterrent only — move sensitive logic to backend.
4. **Pin certificates** — Use `dio_certificate_pinning` for high-security apps to prevent MITM.
5. **Root detection** — Use `flutter_jailbreak_detection` for root/jailbreak checks in financial/sensitive apps.
6. **Mask PII** — Redact PII (email, phone) from all logs and analytics.

## Anti-Patterns

- **No secrets in SharedPreferences**: Use `flutter_secure_storage` for tokens and PII.
- **No hardcoded API keys**: Use `--dart-define` or secure vaults for all secrets.
- **No unobfuscated releases**: Always build with `--obfuscate --split-debug-info`.
- **No PII in logs**: Mask or omit sensitive data from all logs and analytics events.

## Secure Storage

```dart
final secureStorage = const FlutterSecureStorage();

// Store token securely
await secureStorage.write(key: 'auth_token', value: token);

// Read token
final token = await secureStorage.read(key: 'auth_token');
```

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

> See `refs/dependency-injection.md § Third-Party Modules` for the full module
> registration pattern.

## Release Build Command

```bash
flutter build appbundle \
  --obfuscate \
  --split-debug-info=build/debug-info \
  --dart-define=API_URL=$API_URL
```

## SSL Pinning with Dio

```dart
import 'package:dio/dio.dart';
import 'package:dio_certificate_pinning/dio_certificate_pinning.dart';

final dio = Dio();
dio.interceptors.add(CertificatePinningInterceptor(
  allowedSHAFingerprints: [
    "70:99:27:8B:54:4A:40:F5:30:DB:73:E3:64:36:0F:70:3D:09:A6:49",
  ],
));
```

## Security Headers Interceptor

```dart
class SecurityInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    options.headers['X-Content-Type-Options'] = 'nosniff';
    options.headers['X-Frame-Options'] = 'DENY';
    super.onRequest(options, handler);
  }
}
```
