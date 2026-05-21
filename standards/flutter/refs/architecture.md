# Flutter Architecture

## Feature-Based Clean Architecture

**Priority: P0 (CRITICAL)**

### Structure

Every feature lives in `lib/features/` with **3-layer separation** (domain/data/presentation):

- `domain/` — Entities, failures, and Repository interfaces.
- `data/` — DTOs, DataSource, and Repository implementations.
- `presentation/` — BLoC/Cubit, pages, and widgets.

### Implementation Workflow

1. **Create feature directory** — Add new folder under `lib/features/` (e.g., `lib/features/promotions/`).
2. **Define domain layer** — Add entities, failures, and repository interfaces with zero external dependencies.
3. **Implement data layer** — Add DTOs, data sources, and repository implementations that depend only on Domain.
4. **Build presentation layer** — Add BLoC/Cubit, pages, and widgets that depend only on Domain.
5. **Enforce dependency rule** — `Presentation -> Domain <- Data`. Domain must have zero external dependencies.
6. **Share cross-cutting logic** — Move reusable utilities to `lib/shared/` or `lib/core/`.

### Feature Directory Blueprint

```text
lib/features/authentication/
├── domain/
│   ├── entities/
│   │   └── auth_user.dart
│   ├── repositories/
│   │   └── i_auth_repository.dart
│   └── use_cases/
│       └── login_use_case.dart
├── data/
│   ├── data_sources/
│   │   ├── auth_remote_data_source.dart
│   │   └── auth_local_data_source.dart
│   ├── dtos/
│   │   └── user_dto.dart
│   └── repositories/
│       └── auth_repository_impl.dart
└── presentation/
    ├── blocs/
    │   └── auth/
    ├── pages/
    │   ├── login_page.dart
    │   └── profile_page.dart
    └── widgets/
        └── auth_form.dart
```

```text
lib/features/orders/
├── domain/
│   ├── entities/order.dart
│   ├── failures/order_failure.dart
│   └── repositories/i_order_repository.dart
├── data/
│   ├── models/order_dto.dart
│   ├── data_sources/order_remote_data_source.dart
│   └── repositories/order_repository_impl.dart
└── presentation/
    ├── bloc/order_bloc.dart
    └── pages/order_list_page.dart
```

### Key Constraints

1. **Barrel Files**: Use `authentication.dart` at the feature root to export ONLY the domain layer.
2. **Sub-directories**: Do not create more levels than shown above unless the feature has 20+ files.
3. **Mappers**: Keep in the `data/` layer, typically as extensions on DTOs.

### Cross-Feature Import Rule

```dart
// CORRECT: Import only domain types from another feature
import 'package:app/features/auth/domain/entities/user.dart';

// WRONG: Never import data or presentation from another feature
// import 'package:app/features/auth/data/models/user_dto.dart';
```

### Anti-Patterns

- **No cross-feature data imports**: Only import Domain types across features.
- **No UI/Data in Domain layer**: Never put UI or Data classes inside `domain/`.
- **No nested features**: Keep `lib/features/` flat with no sub-feature directories.
- **No direct repository calls from UI**: Use specific BLoCs or use-cases instead.

---

## Layer-Based Clean Architecture

**Priority: P0 (CRITICAL)**

### Structure

```text
lib/
├── domain/         # Pure Dart: entities (@freezed), failures, repository interfaces
├── infrastructure/ # Implementation: DTOs, data sources, mappers, repo impls
├── application/    # Orchestration: BLoCs / Cubits
└── presentation/   # UI: Screens, reusable components
```

### Workflow: Add New Feature Across Layers

1. Define domain entity with `@freezed` in `lib/domain/entities/`
2. Define repository interface in `lib/domain/repositories/`
3. Create DTO in `lib/infrastructure/dtos/` with `fromJson`/`toEntity` mapper
4. Implement repository in `lib/infrastructure/repositories/`
5. Wire BLoC/Cubit in `lib/application/` consuming repository interface
6. Register bindings in `get_it` injection container
7. Build screen in `lib/presentation/` using `BlocBuilder`

### Implementation Guidelines

- **Dependency Flow**: `Presentation -> Application -> Domain <- Infrastructure`. Dependencies point inward.
- **Pure Domain**: No Flutter (Material/Store) or Infrastructure (Dio/Hive) dependencies in `Domain`.
- **Functional Error Handling**: Repositories must return `Either<Failure, Success>`.
- **Always Map**: Infrastructure must map DTOs to Domain Entities; never leak DTOs to UI.
- **Immutability**: Use `@freezed` for all entities and failures.
- **Logic Placement**: No business logic in UI; widgets only display state and emit events.
- **Inversion of Control**: Use `get_it` to inject repository implementations into BLoCs.

### Anti-Patterns

- **No DTOs in UI**: Never import `.g.dart` or Data class directly in Widget.
- **No Material in Domain**: Never import `package:flutter/material.dart` in the `domain` layer.
- **No SharedPrefs in Repo**: Never use `shared_preferences` directly in Repository; use Data Source.

### DTO-to-Entity Mapping

```dart
// lib/infrastructure/dtos/user_dto.dart
class UserDto {
  final String id;
  final String name;

  factory UserDto.fromJson(Map<String, dynamic> json) =>
      UserDto(id: json['id'], name: json['name']);

  UserEntity toEntity() => UserEntity(id: id, name: name);
}
```

### Full Layer Implementation

#### 1. Domain Layer (Entity)

```dart
@freezed
class Bank with _$Bank {
  const factory Bank({
    required String id,
    required String name,
    required String branchCode,
  }) = _Bank;

  factory Bank.fromJson(Map<String, dynamic> json) => _$BankFromJson(json);
}
```

#### 2. Infrastructure Layer (DTO & Mapper)

```dart
@freezed
class BankDto with _$BankDto {
  const BankDto._();

  const factory BankDto({
    @JsonKey(name: 'bank_id') required String id,
    @JsonKey(name: 'bank_name') required String name,
    @JsonKey(name: 'code') required String branchCode,
  }) = _BankDto;

  factory BankDto.fromJson(Map<String, dynamic> json) => _$BankDtoFromJson(json);

  Bank toDomain() => Bank(
    id: id,
    name: name,
    branchCode: branchCode,
  );
}
```

#### Repository Implementation

```dart
class BankRepository implements IBankRepository {
  final BankRemoteDataSource remoteDataSource;

  BankRepository(this.remoteDataSource);

  @override
  Future<Either<ApiFailure, List<Bank>>> fetchBanks() async {
    try {
      final dtoList = await remoteDataSource.getBanks();
      return right(dtoList.map((dto) => dto.toDomain()).toList());
    } catch (e) {
      return left(ApiFailure.fromException(e));
    }
  }
}
```

#### 3. Application Layer (BLoC)

```dart
class BankBloc extends Bloc<BankEvent, BankState> {
  final IBankRepository repository;

  BankBloc(this.repository) : super(const BankState.initial()) {
    on<_Fetch>(_onFetch);
  }

  Future<void> _onFetch(_Fetch event, Emitter<BankState> emit) async {
    emit(const BankState.loading());
    final failureOrBanks = await repository.fetchBanks();
    emit(failureOrBanks.fold(
      (f) => BankState.error(f.message),
      (banks) => BankState.loaded(banks),
    ));
  }
}
```

