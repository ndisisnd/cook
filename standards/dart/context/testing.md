# Dart Testing

> For Flutter-specific testing (widget tests, golden tests, integration tests, robot pattern), see the `flutter-testing` skill.

## Package Structure

- Use `package:test` for pure Dart; `package:flutter_test` for Flutter.
- Mirror `lib/` under `test/`: `lib/src/user.dart` → `test/src/user_test.dart`.
- File convention: `*_test.dart`.

## Unit Tests

Use `group()` to organise related cases. Use `setUp()` / `tearDown()` for shared state.

```dart
import 'package:test/test.dart';

void main() {
  group('UserRepository', () {
    late MockUserDataSource dataSource;
    late UserRepository repo;

    setUp(() {
      dataSource = MockUserDataSource();
      repo = UserRepository(dataSource);
    });

    test('returns null when user not found', () async {
      when(() => dataSource.fetchUser(any())).thenAnswer((_) async => null);
      expect(await repo.getUser('123'), isNull);
    });

    test('throws StateError on network failure', () async {
      when(() => dataSource.fetchUser(any())).thenThrow(Exception('timeout'));
      expect(() => repo.getUser('123'), throwsA(isA<StateError>()));
    });
  });
}
```

Write test names as sentences describing observable behaviour, not implementation: `'returns null when user not found'` not `'test getUser null case'`.

## Mocking with mocktail

Prefer `mocktail` over `mockito` — no code generation required.

```dart
import 'package:mocktail/mocktail.dart';

class MockUserDataSource extends Mock implements UserDataSource {}

// Register fallback values for custom types passed to any()
setUpAll(() {
  registerFallbackValue(const UserId('fallback'));
});
```

Key mocktail APIs:
- `when(() => mock.method()).thenReturn(value)` — stub return value
- `when(() => mock.method()).thenAnswer((_) async => value)` — stub async
- `when(() => mock.method()).thenThrow(exception)` — stub exception
- `verify(() => mock.method()).called(1)` — verify interaction
- `verifyNever(() => mock.method())` — assert never called

## Testing Streams

Use `emitsInOrder`, `emits`, and `emitsDone` matchers from `package:test`:

```dart
test('emits loading then data', () {
  expect(
    repo.userStream('123'),
    emitsInOrder([isA<Loading>(), isA<Success>()]),
  );
});
```

## Testing with fake_async

Use `package:fake_async` for time-dependent code instead of `Future.delayed` or `sleep`:

```dart
import 'package:fake_async/fake_async.dart';

test('debounce fires after 300ms', () {
  fakeAsync((async) {
    var fired = false;
    debounce(() => fired = true, const Duration(milliseconds: 300));
    async.elapse(const Duration(milliseconds: 299));
    expect(fired, isFalse);
    async.elapse(const Duration(milliseconds: 1));
    expect(fired, isTrue);
  });
});
```

## Anti-Patterns

- `mockito` with `@GenerateMocks` for new code — use `mocktail` instead
- Testing implementation details — test observable behaviour only
- `Future.delayed` or `sleep` in tests — use `fake_async`
- Bare `expect(result, anything)` — always assert the actual value or type
- Shared mutable state between tests without `setUp` reset
