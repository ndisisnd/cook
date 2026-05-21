# Flutter Error Handling

**Priority: P0 (CRITICAL)**

## Implementation Workflow

1. **Define failures** — Create domain-specific failures using `@freezed` unions (e.g., `UnauthorizedFailure`, `OutOfStockFailure`).
2. **Return Either** — Repositories return `Either<Failure, T>`. No exceptions in UI/BLoC.
3. **Catch in Infrastructure only** — Infrastructure catches exceptions (e.g., `DioException`) and returns `Left(Failure)`. Never rethrow to UI.
4. **Fold in BLoC** — Use `.fold(failure, success)` in BLoC to emit corresponding states. Remove try/catch from BLoC.
5. **Localize messages** — Use `failure.failureMessage` (returns `TRObject` or localized string) for UI-safe text.
6. **Log with stable templates** — Use low-cardinality message templates; pass variable data via metadata/context.
7. **No silent catch** — Never swallow errors without logging or documented retry.
8. **Crashlytics routing** — All UI/BLoC `catch` blocks MUST route errors via `AppLogger.error(AppException.fromException(e).message, error: e, stackTrace: st)` for observability and type-safe UI messages.

## Anti-Patterns

- **No try-catch in BLoC**: BLoC receives `Either` and `folds`; try/catch belongs in Infrastructure.
- **No plain string failures**: Define typed `@freezed` Failure subclasses instead of `Left('Something went wrong')`.
- **No empty catch blocks**: Always log and propagate; never swallow errors silently.
- **No repositories throwing exceptions**: Return `Left(Failure)` instead of throwing `Exception`.
- **No missing log registration**: Use `AppLogger.error` in BLoC/UI `catch` to ensure Crashlytics tracking and type-safe UI messages.

## Global Failures

```dart
@freezed
class ApiFailure with _$ApiFailure {
  const factory ApiFailure.serverError() = _ServerError;
  const factory ApiFailure.networkError() = _NetworkError;
  const factory ApiFailure.unauthenticated() = _Unauthenticated;
  const factory ApiFailure.badRequest(String message) = _BadRequest;
}
```

## Infrastructure: DioException → Failure

```dart
extension DioErrorX on DioException {
  ApiFailure toFailure() {
    switch (type) {
      case DioExceptionType.connectionTimeout:
        return const ApiFailure.networkError();
      case DioExceptionType.badResponse:
        if (response?.statusCode == 401) return const ApiFailure.unauthenticated();
        return const ApiFailure.serverError();
      default:
        return const ApiFailure.serverError();
    }
  }
}
```

## Repository Error Mapping

> **Scope:** This section covers domain-specific failure mapping at the repository layer.
> For global HTTP concerns (token refresh, 401 handling, auth headers), see
> `refs/networking.md § Token Refresh Pattern` — those belong in an interceptor, not here.

```dart
@override
Future<Either<Failure, Order>> getOrder(String id) async {
  try {
    final dto = await _remoteDataSource.fetchOrder(id);
    return right(dto.toDomain());
  } on DioException catch (e) {
    return left(ServerFailure(message: e.message ?? 'Unknown error'));
  }
}
```

## BLoC Consumption

```dart
final result = await _getOrderUseCase(orderId);
result.fold(
  (failure) => emit(OrderError(failure.failureMessage)),
  (order) => emit(OrderLoaded(order)),
);
```
