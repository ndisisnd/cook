# Flutter Dependency Injection (get_it + injectable)

**Priority: P1 (HIGH)**

## Structure

```text
core/injection/
├── injection.dart   # Initialization & setup
└── modules/         # Third-party dependency modules (Dio, Storage)
```

## Implementation Workflow

1. **Annotate classes** — Use `@injectable` annotations; avoid manual registry calls.
2. **Choose scope** — Default to `@LazySingleton` for repositories, services, and data sources (init on demand).
3. **Register BLoCs as factories** — Use `@injectable` (Factory) for BLoCs to ensure state resets per instance. Never use `@Singleton()` for BLoCs.
4. **Inject abstractions** — Always register implementations as abstract interfaces (`as: IService`).
5. **Register third-party deps** — Use `@module` for external instances (Dio, Hive, SharedPreferences).
6. **Prefer constructor injection** — Use mandatory constructor parameters; `injectable` resolves them automatically.

## Anti-Patterns

- **No inline `getIt` calls**: Inject via constructor instead of calling `GetIt` in UI `build()`.
- **No `@Singleton` BLoCs**: Always use `@injectable` (Factory) to ensure state resets.
- **No concrete class injection**: Always inject abstract interface (e.g., `IOrderRepository`).
- **No manual registration**: Use `@injectable` annotations instead of manual `getIt.register` calls in production code.

## Registration Example

```dart
@module
abstract class NetworkModule {
  @lazySingleton
  Dio get dio => Dio(BaseOptions(baseUrl: 'https://api.example.com'));
}

@LazySingleton(as: IOrderRepository)
class OrderRepositoryImpl implements IOrderRepository {
  final Dio _dio;
  OrderRepositoryImpl(this._dio);
}
```

## Third-Party Modules

Since you cannot annotate third-party classes (like `Dio` or `SharedPreferences`) directly, use a `@module`.

```dart
@module
abstract class NetworkingModule {
  @lazySingleton
  Dio get dio => Dio(BaseOptions(baseUrl: 'https://api.example.com'));

  @preResolve // Waits for this before finishing injection setup
  Future<SharedPreferences> get prefs => SharedPreferences.getInstance();
}
```

### Named Injection

Use for multiple instances of the same type:

```dart
@module
abstract class ServiceModule {
  @Named("AuthDio")
  Dio get authDio => Dio();

  @Named("PublicDio")
  Dio get publicDio => Dio();
}

// Consumption: Repo(@Named("AuthDio") Dio dio)
```

## Test Mock Swap

```dart
setUp(() {
  getIt.unregister<IOrderRepository>();
  getIt.registerLazySingleton<IOrderRepository>(() => MockOrderRepository());
});
```
