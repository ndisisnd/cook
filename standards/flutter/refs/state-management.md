# Flutter State Management

## BLoC / Cubit

**Priority: P0 (CRITICAL)**

Role: Design predictable, testable state flows.

### State Design Workflow

1. **Define Events** — What happens? (`UserTap`, `ApiSuccess`). Use `@freezed`.
2. **Define States** — What needs to show? (`Initial`, `Loading`, `Data`, `Error`).
3. **Implement BLoC** — Map Events to States using `on<Event>`.
4. **Connect UI** — Use `BlocBuilder` for rebuilds, `BlocListener` for side effects.

### Implementation Guidelines

- **States & Events**: Use `@freezed` for union types (`Initial`, `Loading`, `Success`, `Failure` states).
- **Error Handling**: Emit `Failure` states for UI-critical errors. For silent/background events, either let exceptions propagate to global `onError` interceptor (`AppBlocObserver`), or catch and call `addError(e, st)` without emitting an error state.
- **Async Data**: Use `emit.forEach` for streams or `await` with `emit`.
- **Concurrency**: Use `transformer: restartable()` from `bloc_concurrency` for search/typeahead to debounce and cancel previous requests.
- **UI Connectivity**: Use `BlocBuilder` for UI rebuilds and `BlocListener` for side effects (navigation, snackbars).
- **Testing**: Use `blocTest` for ALL states and verify sequence of emitted states.

### Verification Checklist

- [ ] Initial state defined and tested?
- [ ] `blocTest` used for ALL states?
- [ ] No complex calculation in `BlocBuilder`?
- [ ] Side effects (navigation, snackbars) in `BlocListener`, not `BlocBuilder`?
- [ ] Heavy `BlocBuilder` widgets declare `buildWhen`.

### Anti-Patterns

- **No `.then()`**: Use `await` or `emit.forEach()` to emit.
- **No BLoC-to-BLoC direct refs**: Use `StreamSubscription` or `BlocListener`.
- **No logic in `BlocBuilder`**: Move valid logic to BLoC.
- **No `BlocBuilder` without `buildWhen`**: Heavy subtrees must declare a `buildWhen` predicate.

### Templates

#### Freezed State (Union) ✅ PREFERRED

```dart
part of 'feature_bloc.dart';

@freezed
abstract class FeatureState with _$FeatureState {
  const factory FeatureState.initial() = _Initial;
  const factory FeatureState.loading() = _Loading;
  const factory FeatureState.success(List<Data> data) = _Success;
  const factory FeatureState.failure(Failure failure) = _Failure;
}
```

**Which to use:**
- **Union (preferred):** One named constructor is active at a time — impossible combinations
  like `isLoading=true` alongside `data!=null` cannot exist. Use this by default.
- **Flat:** Use only when multiple fields are genuinely orthogonal (e.g., a `searchTerm`
  string and an `isLoading` bool that coexist independently). Requires a `status` enum
  if states need disambiguation.
- **Equatable Alternative:** No code generation required. Use only when `build_runner` is
  unavailable. Prefer Freezed Union for all new code.

#### Freezed State (Flat) ⚠️ LIMITED USE

```dart
part of 'feature_bloc.dart';

@freezed
abstract class FeatureState with _$FeatureState {
  const factory FeatureState({
    required List<Data> data,
    required Failure failure,
    required bool isLoading,
  }) = _FeatureState_;
}
```

#### Event

```dart
part of 'feature_bloc.dart';

@freezed
abstract class FeatureEvent with _$FeatureEvent {
  const factory FeatureEvent.started() = _Started;
  const factory FeatureEvent.refreshRequested() = _RefreshRequested;
}
```

#### BLoC

```dart
@injectable
class FeatureBloc extends Bloc<FeatureEvent, FeatureState> {
  final FeatureRepository _repository;

  FeatureBloc(this._repository) : super(const FeatureState.initial()) {
    on<_Started>(_onStarted);
  }

  Future<void> _onStarted(_Started event, Emitter<FeatureState> emit) async {
    emit(const FeatureState.loading());
    final result = await _repository.getData();
    result.fold(
      (failure) => emit(FeatureState.failure(failure)),
      (data) => emit(FeatureState.success(data)),
    );
  }
}
```

#### Equatable Alternative ⚠️ LEGACY

```dart
sealed class FeatureState extends Equatable {
  const FeatureState();
  @override
  List<Object?> get props => [];
}

final class FeatureInitial extends FeatureState {}
final class FeatureLoading extends FeatureState {}

final class FeatureSuccess extends FeatureState {
  final List<Data> data;
  const FeatureSuccess(this.data);
  @override
  List<Object?> get props => [data];
}
```

---

## Riverpod

**Priority: P0 (CRITICAL)**

### Structure

```text
lib/
├── providers/           # Global providers and services
└── features/user/
    ├── providers/       # Feature-specific providers
    └── models/          # @freezed domain models
```

### Implementation Guidelines

- **Generator First**: Use `@riverpod` annotations. Avoid manual `Provider` definitions.
- **Immutability**: Use `Freezed` for all state models.
- **`ref.watch()`**: Inside `build()` to rebuild on changes.
- **`ref.listen()`**: Inside `build()` for side-effects (navigation, dialogs). Never in provider init.
- **`ref.read()`**: ONLY in callbacks (`onPressed`).
- **Testing**: Override providers with `ProviderScope(overrides: [provider.overrideWithValue(Mock())])`.
- **Linting**: Enable `riverpod_lint` and `custom_lint` for cycle detection.

### Anti-Patterns

- **No side-effects in provider init**: Use `ref.listen()` in widgets instead.
- **No BuildContext in Notifiers**: Never pass `BuildContext` into Notifier/Provider.
- **No local provider instantiation**: Keep providers global; avoid dynamic creation.

### Provider Definition (Generator-First)

```dart
// products_provider.dart — use @riverpod annotation
@riverpod
class ProductsNotifier extends _$ProductsNotifier {
  @override
  Future<List<Product>> build() async {
    return ref.watch(productRepositoryProvider).getProducts();
  }

  Future<void> addProduct(Product product) async {
    await ref.read(productRepositoryProvider).create(product);
    ref.invalidateSelf(); // Refetch after mutation
  }
}
```

### Consuming Providers

```dart
// products_screen.dart — ConsumerWidget usage
class ProductsScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final productsAsync = ref.watch(productsNotifierProvider);

    return productsAsync.when(
      data: (products) => ListView.builder(
        itemCount: products.length,
        itemBuilder: (_, i) => ProductTile(products[i]),
      ),
      loading: () => const CircularProgressIndicator(),
      error: (err, stack) => Text('Error: $err'),
    );
  }
}
```

---

## GetX State Management

**Priority: P0 (CRITICAL)**

### Structure

```text
lib/app/modules/home/
├── controllers/
│   └── home_controller.dart
├── bindings/
│   └── home_binding.dart
└── views/
    └── home_view.dart
```

### Implementation Guidelines

- **Controllers**: Extend `GetxController`. Store logic and state variables here.
- **Reactivity**:
  - Use `.obs` for observable variables (e.g., `final count = 0.obs;`).
  - Wrap UI in `Obx(() => ...)` to listen for changes.
  - For simple state, use `update()` in controller and `GetBuilder` in UI.
- **Dependency Injection**:
  - Use `Bindings` class to decouple DI from UI.
  - Prefer `Get.lazyPut(() => Controller())` in Bindings.
  - Let GetX handle disposal. Avoid `permanent: true`.
- **Hooks**: Use `onInit()`, `onReady()`, `onClose()` instead of `initState`/`dispose`.
- **Architecture**: Use `get_cli` for modular MVVM (data, models, modules).

### Anti-Patterns

- **No BuildContext in controllers**: Pass no `BuildContext` to controllers.
- **No inline DI**: Avoid `Get.put()` in widgets; use Bindings + `Get.find`.
- **No fat views**: Keep views pure UI; delegate all logic to controller.

### Controller + View Pattern

```dart
class UserController extends GetxController {
  final name = "User".obs;
  void updateName(String val) => name.value = val;
}

class UserView extends GetView<UserController> {
  @override
  Widget build(ctx) => Scaffold(
    body: Obx(() => Text(controller.name.value)),
    floatingActionButton: FloatingActionButton(
      onPressed: () => controller.updateName("New"),
    ),
  );
}
```
