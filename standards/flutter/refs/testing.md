# Flutter Testing Standards

**Priority: P0 (CRITICAL)**

## Core Rules

1. **Test Pyramid**: Unit > Widget > Integration.
2. **Naming**: `should <behavior> when <condition>`.
3. **AAA**: Arrange, Act, Assert in all tests.
4. **Shared Mocks**: `test/shared/` only — no local mocks.
5. **File Placement**: `_integration_test.dart` ONLY in `integration_test/`.
6. **Robot-First**: ALL UI assertions/interactions via Robot pattern (e.g., `CheckoutRobot`) — never raw `find.*`/`expect()` in test body.

---

## Unit Testing

Unit tests verify the smallest parts (functions, methods, classes) in isolation.

### Core Rules

1. **Isolation**: External dependencies (API, Database, SharedPreferences) **must** be mocked.
2. **Scope**: One test file per source file (`user_repository.dart` → `user_repository_test.dart`).
3. **AAA**: Arrange-Act-Assert structure strictly.
4. **Explicit Matching**: FORBIDDEN: `any()` and `registerFallbackValue()`. Always use explicit values.

### Test Data Builders

Avoid hardcoding large objects in every test. Use a Builder pattern.

```dart
class UserBuilder {
  String _id = '1';
  String _name = 'Default User';

  UserBuilder withId(String id) {
    _id = id;
    return this;
  }

  User build() => User(id: _id, name: _name);
}

// Usage in test
final user = UserBuilder().withId('99').build();
```

### Mocking with Mocktail

```dart
import 'package:mocktail/mocktail.dart';
import 'package:test/test.dart';

class MockUserRepository extends Mock implements UserRepository {}

void main() {
  late MockUserRepository mockRepo;
  late GetUserProfileUseCase useCase;

  setUp(() {
    mockRepo = MockUserRepository();
    useCase = GetUserProfileUseCase(mockRepo);
  });

  group('GetUserProfileUseCase', () {
    test('should return User when repository succeeds', () async {
      final user = UserBuilder().build();
      when(() => mockRepo.getUser('1')).thenAnswer((_) async => Right(user));

      final result = await useCase('1');

      expect(result, Right(user));
      verify(() => mockRepo.getUser('1')).called(1);
    });

    test('should return Failure when repository fails', () async {
      when(() => mockRepo.getUser('1')).thenThrow(ServerException());
      final call = useCase('1');
      expect(call, throwsA(isA<ServerException>()));
    });
  });
}
```

### Best Practices (DCM)

```dart
// ❌ BAD: No assertion — passes even if logic is broken
test('fetchUser runs', () async {
  await repo.fetchUser();
});

// ✅ GOOD: Always verify result
test('fetchUser returns data', () async {
  final result = await repo.fetchUser();
  expect(result, isNotNull);
});

// ✅ GOOD: Specific matchers for better error messages
expect(list, hasLength(1));  // NOT: expect(list.length, 1)

// ✅ GOOD: Streams — use expectLater
await expectLater(stream, emits(1));

// ❌ BAD: Unsafe matchers
registerFallbackValue(User.empty());
when(() => mockRepo.updateUser(any())).thenAnswer((_) async => Right(user));

// ✅ GOOD: Explicit matching
final userToUpdate = UserBuilder().withId('123').build();
when(() => mockRepo.updateUser(userToUpdate)).thenAnswer((_) async => Right(userToUpdate));
```

---

## Widget Testing

Verify UI and interactions in a headless simulated environment.

### Core Rules

1. **Wrapper**: Always use `TestWrapper.init()` + `tester.pumpLocalizedWidget(...)`.
2. **Pump**: `pump()` = one frame; `pumpAndSettle()` = wait for all animations; `settle: false` + manual `pump()` for loading states or `whenListen`.
3. **Finders**: Use semantic finders (`find.text`, `find.byKey`, `find.byType`).
4. **Imports**: Always import `package:flutter/material.dart` when tests reference Material widgets.

### TestWrapper Setup Pattern

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:bloc_test/bloc_test.dart';
import 'package:mocktail/mocktail.dart';

import '../../shared/mock_blocs.dart';
import '../../shared/widgets/test_wrapper.dart';
import '../../robots/<feature>/<screen>_robot.dart';

void main() {
  late MockFeatureBloc mockBloc;

  setUpAll(() async {
    await TestWrapper.init();
  });

  setUp(() {
    mockBloc = MockFeatureBloc();
    // ⚠️ ALWAYS stub initial state — prevents null errors
    when(() => mockBloc.state).thenReturn(const FeatureState.initial());
    when(() => mockBloc.stream).thenAnswer((_) => Stream.empty());
  });

  group('FeatureScreen', () {
    testWidgets('renders initial state', (tester) async {
      final robot = FeatureRobot(tester);
      await robot.pumpScreen(featureBloc: mockBloc);
      robot.expectScreenVisible();
    });
  });

  group('Edge cases', () {
    testWidgets('handles error state', (tester) async {
      when(() => mockBloc.state).thenReturn(
        const FeatureState(status: AppStatus.error, error: 'Network error'),
      );
      final robot = FeatureRobot(tester);
      await robot.pumpScreen(featureBloc: mockBloc);
      robot.expectTextVisible('Network error');
    });
  });
}
```

### GetIt Registration

Use when widget creates blocs via `getIt<MyBloc>()` internally:

```dart
setUpAll(() async {
  await TestWrapper.init();
  getIt.registerFactory<AdBloc>(() => mockAdBloc);
});

tearDownAll(() {
  getIt.reset();
});
```

**Rule:** Constructor param → `pumpScreen(bloc: mockBloc)`. Internal `getIt<>()` → register in GetIt.

### State Transitions with whenListen

```dart
testWidgets('shows snackbar on error', (tester) async {
  whenListen(
    mockBloc,
    Stream.fromIterable([
      const FeatureState(status: AppStatus.loading),
      const FeatureState(status: AppStatus.error, error: 'Failed'),
    ]),
    initialState: const FeatureState(),
  );

  final robot = FeatureRobot(tester);
  await robot.pumpScreen(featureBloc: mockBloc, settle: false);
  robot.expectSnackbarVisible();
});
```

### Common Pitfalls

- **Text casing mismatch**: Check widget source for `.toUpperCase()`, `.tr()`, `.capitalize()`.
- **Missing Material import**: Required when tests reference `Scaffold`, `Switch`, `Icon`, `Icons`.
- **Overflow in tests**: Default test surface is 800×600 — resize if needed: `tester.view.physicalSize = const Size(1080, 1920)`.
- **Null state errors**: Always stub `mockBloc.state` and `mockBloc.stream` in `setUp`.
- **Loading state timeout**: `pumpAndSettle()` hangs on infinite animations — use `settle: false` + manual `pump()`.

---

## Integration Testing

Expert strategies for Patrol integration tests with Robot Pattern enforcement.

### File Placement

`*_integration_test.dart` belongs **ONLY** in `integration_test/`. Never in `test/`.

### Robot Pattern (MANDATORY)

All assertions and interactions must go in robot classes.

**Allowed in test body:** `$.native.*`, navigation helper calls returning `bool`, robot instantiation and method calls.

**NOT allowed in test body:** `find.byType(...)`, `expect(find.*, ...)`, `$.tester.tap(find.*)`.

### Integration Test File Structure

```dart
import 'package:patrol/patrol.dart';
import '../../test/robots/<feature>/<robot>.dart';
import '../helpers/auth_helper.dart';

void main() {
  Future<bool> navigateToFeature(PatrolIntegrationTester $) async {
    app.main();
    await $.pumpAndSettle(timeout: const Duration(seconds: 10));
    final loggedIn = await IntegrationAuthHelper.loginOrSkip($);
    if (!loggedIn) return false;
    await IntegrationAuthHelper.waitForDashboard($);
    return true;
  }

  patrolTest('screen renders with app bar', ($) async {
    final ok = await navigateToFeature($);
    if (!ok) return;
    final robot = FeatureRobot($.tester);
    robot.expectVAppBarVisible();
    robot.expectContentVisible();
  });
}
```

### Auth Helper Pattern

```dart
class IntegrationAuthHelper {
  IntegrationAuthHelper._();
  static const _testEmail = String.fromEnvironment('TEST_EMAIL', defaultValue: '');
  static const _testPassword = String.fromEnvironment('TEST_PASSWORD', defaultValue: '');
  static bool get hasCredentials => _testEmail.isNotEmpty && _testPassword.isNotEmpty;

  static Future<bool> loginOrSkip(PatrolIntegrationTester $) async {
    if (!hasCredentials) return false;
    final robot = LoginRobot($.tester);
    try { robot.verifyLoginScreenVisible(); } catch (_) { return true; }
    await robot.loginWith(email: _testEmail, password: _testPassword);
    return true;
  }

  static Future<void> waitForDashboard(PatrolIntegrationTester $) async {
    await $.pumpAndSettle(timeout: const Duration(seconds: 15));
  }
}
```

### Running with Credentials

```bash
patrol test \
  --target integration_test/app_test.dart \
  --dart-define=TEST_EMAIL=user@staging.com \
  --dart-define=TEST_PASSWORD=StrongPass1!
```

### Coverage Checklist

- [ ] Screen renders (app bar, content, or empty state)
- [ ] Primary action works (FAB, submit button, etc.)
- [ ] Back navigation returns to previous screen
- [ ] Auth-protected: uses `IntegrationAuthHelper.loginOrSkip($)`
- [ ] All assertions via robot — zero raw `find.*` in test body

---

## Robot Pattern

Decouple UI interactions from test assertions. One robot shared by widget + Patrol tests.

### Directory

```text
test/
  robots/<feature>/<screen>_robot.dart   ← shared robot
  features/<feature>/                    ← widget tests (*_test.dart ONLY)
integration_test/<feature>/              ← patrol tests
```

### Robot Class Pattern

```dart
class LoginRobot {
  final WidgetTester tester;
  const LoginRobot(this.tester);

  Future<void> enterEmail(String email) async {
    await tester.enterText(find.byKey(LoginWidgetKeys.emailField), email);
    await tester.pump();
  }

  Future<void> tapLoginButton() async {
    await tester.ensureVisible(find.byKey(LoginWidgetKeys.submitButton));
    await tester.tap(find.byKey(LoginWidgetKeys.submitButton));
    await tester.pump();
  }

  Future<void> loginWith({required String email, required String password}) async {
    await enterEmail(email);
    await enterPassword(password);
    await tapLoginButton();
  }

  Future<void> pumpScreen({required MockAuthBloc authBloc, bool settle = true}) async {
    await tester.pumpWidget(
      BlocProvider<AuthBloc>.value(
        value: authBloc,
        child: const LoginScreen(),
      ),
    );
    if (settle) await tester.pumpAndSettle();
  }

  void verifyLoginScreenVisible() =>
      expect(find.byKey(LoginWidgetKeys.submitButton), findsOne);
}
```

### Symmetric Assertions (REQUIRED)

```dart
// ✅ GOOD: Symmetric pair
void expectContentVisible(String text) => expect(find.text(text), findsOne);
void expectContentNotVisible(String text) => expect(find.text(text), findsNothing);
```

### BaseRobot Centralization

Extract standard methods into a common `BaseRobot`:
- `scrollDown`, `scrollToEnd`
- `expectScreenVisible`, `expectScreenNotVisible`

### Common Integration Robot Methods

Every robot used in integration tests should include:

| Method | Purpose |
| :--- | :--- |
| `expectVAppBarVisible()` | Screen has app bar (confirms navigation) |
| `expectContentVisible()` | Screen shows list/content (not blank) |
| `tapBackButton()` | Navigate back from screen |
| `expectLoadingIndicator()` | Loading state verification |
| Feature-specific actions | `tapFab()`, `tapHistoryTab()`, etc. |
| Feature-specific asserts | `expectFabVisible()`, `expectTabBarVisible()` |

---

## Mocking Standards

### Rules

1. **No local mocks for shared components**: Never define `MockMyBloc` in individual test files.
2. **Shared mock files**: Define all mocks in `test/shared/`.

| Component Type | Shared Mock File |
| :--- | :--- |
| **Blocs** | `test/shared/mock_blocs.dart` |
| **Data Sources** | `test/shared/mock_datasources.dart` |
| **Repositories** | `test/shared/mock_repositories.dart` |
| **Services** | `test/shared/mock_services.dart` |
| **External** | `test/shared/mock_external_services.dart` |

3. **Check before creating**: Check `test/shared/` before adding a new mock.

### Bloc State Stubbing (CRITICAL)

Mock blocs return `null` for `.state` by default → widget crashes. **Always** stub in `setUp`:

```dart
setUp(() {
  mockBloc = MockFeatureBloc();
  // ⚠️ Without these, widget tests crash with null errors
  when(() => mockBloc.state).thenReturn(const FeatureState.initial());
  when(() => mockBloc.stream).thenAnswer((_) => Stream.empty());
});
```

### Safe Argument Matching

```dart
// ❌ BAD: Unsafe matchers
when(() => repository.fetchData(any())).thenAnswer(...);

// ✅ GOOD: Specific values
when(() => repository.fetchData(const MyParams(id: '123'))).thenAnswer(...);

// ✅ GOOD: Type-safe matchers
verify(() => service.performTask(
  id: isA<String>(),
  priority: isA<int>(),
)).called(1);

// ✅ GOOD: Handles multiple calls from widget rebuilds
verify(() => mockBloc.add(const FeatureEvent.init(isPremium: false)))
    .called(greaterThan(0));
```

---

## BLoC Testing

```dart
blocTest<AuthBloc, AuthState>(
  'emits [loading, authenticated] when login is successful',
  build: () {
    when(() => mockAuthRepo.login('test@email.com', 'pass123'))
        .thenAnswer((_) async => Right(mockUser));
    return AuthBloc(mockAuthRepo);
  },
  act: (bloc) => bloc.add(const AuthEvent.loginPressed('test@email.com', 'pass123')),
  expect: () => [
    const AuthState.loading(),
    AuthState.authenticated(mockUser),
  ],
  verify: (_) {
    verify(() => mockAuthRepo.login('test@email.com', 'pass123')).called(1);
  },
);
```

**Best Practices:**
- Do not mock based on State (unreliable — tracks emission count, not event trigger). Always verify the downstream Dependency/Service call in `verify`.
- Always verify initial state:

```dart
test('initial state is AuthState.initial', () {
  expect(AuthBloc(mockRepo).state, const AuthState.initial());
});
```

---

## Test Organization

### File Placement Rules

| Test Type | Location | Suffix | Runner | Framework |
| :--- | :--- | :--- | :--- | :--- |
| Unit tests | `test/features/<feature>/` | `_test.dart` | `flutter test` | flutter_test, mocktail |
| Widget tests | `test/features/<feature>/` | `_test.dart` | `flutter test` | flutter_test, mocktail, bloc_test |
| **Integration tests** | `integration_test/<feature>/` | `_integration_test.dart` | `patrol test` | patrol |

### Classification Guide

1. Does it use `patrolTest`, `$.native.*`, or require a real device? → **Integration test**
2. Does it render widgets and assert on UI? → **Widget test**
3. Does it test a class/function without rendering widgets? → **Unit test**

### Directory Structure

```text
test/
├── features/
│   ├── auth/
│   │   └── login_screen_test.dart
│   └── subscription/
│       └── subscription_screen_test.dart
├── robots/
│   └── auth/
│       └── login_robot.dart
├── shared/
│   ├── mock_blocs.dart
│   ├── mock_repositories.dart
│   ├── mock_services.dart
│   └── widgets/
│       └── test_wrapper.dart
└── core/
    └── utils/
        └── input_validator_test.dart

integration_test/
├── app_test.dart
├── auth/
│   └── login_integration_test.dart
└── helpers/
    └── test_helpers.dart
```

---

## Widget Keys

### File Layout

```text
lib/core/keys/
├── app_widget_keys.dart              ← single barrel; always import this
└── authenticate/
    └── login_widget_keys.dart        ← LoginWidgetKeys
```

### Adding Keys for a New Screen

1. Create `lib/core/keys/<feature>/<screen>_widget_keys.dart`
2. Add one `export` line in `app_widget_keys.dart`
3. No other changes needed.

### WidgetKeys Class Pattern

```dart
abstract final class LoginWidgetKeys {
  static const emailField           = Key('authenticate.login.emailField');
  static const passwordField        = Key('authenticate.login.passwordField');
  static const submitButton         = Key('authenticate.login.submitButton');
  static const forgotPasswordButton = Key('authenticate.login.forgotPasswordButton');
}
```

Key string format: `<feature>.<screen>.<element>` — readable in failure output.

### Usage

```dart
// ✅ In widget
EmailField(key: LoginWidgetKeys.emailField, ...)

// ✅ In robot / test
find.byKey(LoginWidgetKeys.emailField)

// ❌ Never inline
find.byKey(const Key('login_email_field'))
```
