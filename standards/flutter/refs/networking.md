# Flutter Networking (Retrofit & Dio)

**Priority: P0 (CRITICAL)**

## Structure

```text
infrastructure/
├── data_sources/
│   ├── remote/        # Retrofit abstract classes
│   └── local/         # Cache/Storage
└── network/
    ├── dio_client.dart     # Custom Dio setup
    └── interceptors/       # Auth, Logging, Cache
```

## Implementation Workflow

1. **Define Retrofit clients** — Create abstract classes with `@RestApi()` and HTTP annotations (`@GET`, `@POST`). Methods return `Future<DTO>`.
2. **Create DTOs** — Use `@freezed` and `@JsonSerializable` for all request/response bodies.
3. **Map to domain** — Data sources must map DTOs to Domain Entities (e.g., `userDto.toDomain()`).
4. **Guard enums** — Always use `@JsonKey(unknownEnumValue: Status.unknown)` to prevent crashes from new backend values.
5. **Add auth interceptor** — Inject `Authorization: Bearer <token>` in `onRequest`.
6. **Handle token refresh** — On 401, use `QueuedInterceptorsWrapper`, call `refreshToken()`, update stored token, retry via `dio.fetch(err.requestOptions)`.
7. **Map failures** — Convert `DioException` to typed `Failure` objects (`ServerFailure`, `NetworkFailure`).

## Anti-Patterns

- **No manual JSON parsing**: Use Retrofit's generated mappers instead of `jsonDecode`.
- **No global Dio instances**: Inject `Dio` through DI.
- **No inline try-catch in repositories**: The repository layer should handle all Retrofit exceptions.
- **No unguarded enums**: Always include `unknownEnumValue` to prevent crashes on new backend values.

## Retrofit Client

```dart
@RestApi()
abstract class OrderRemoteDataSource {
  factory OrderRemoteDataSource(Dio dio) = _OrderRemoteDataSource;

  @GET('/orders/{id}')
  Future<OrderDto> getOrder(@Path('id') String id);

  @POST('/orders/{id}/cancel')
  Future<void> cancelOrder(@Path('id') String id);
}
```

## Safe Enum DTO

```dart
@freezed
class OrderDto with _$OrderDto {
  const factory OrderDto({
    required String id,
    @JsonKey(unknownEnumValue: OrderStatus.unknown)
    required OrderStatus status,
  }) = _OrderDto;

  factory OrderDto.fromJson(Map<String, dynamic> json) =>
      _$OrderDtoFromJson(json);
}
```

## Token Refresh Pattern

When a `401 Unauthorized` error occurs, the networking layer should handle the refresh cycle transparently.

Using `QueuedInterceptorsWrapper` ensures that if multiple requests trigger a 401 at the same time, they are queued while the first one performs the token refresh, preventing multiple redundant refresh calls.

```dart
class AuthInterceptor extends QueuedInterceptorsWrapper {
  final Dio dio;
  final SecureStorage storage;

  AuthInterceptor(this.dio, this.storage);

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      // 1. Refresh the token
      final newToken = await _performRefresh();

      if (newToken != null) {
        // 2. Retry the original request with new token
        final options = err.requestOptions;
        options.headers['Authorization'] = 'Bearer $newToken';

        final response = await dio.fetch(options);
        return handler.resolve(response);
      }
    }
    return handler.next(err);
  }

  Future<String?> _performRefresh() async {
    // Logic to call refresh endpoint and update storage
  }
}
```
