# Flutter Navigation

## Router Decision Rule

Choose **one** routing framework per project. This file covers all three.

| Scenario | Framework | Priority in this file |
|---|---|---|
| New project | go_router | P0 (CRITICAL) |
| Existing auto_route project | auto_route | P1 (HIGH) |
| Existing GetX project | GetX Navigation | P1 (HIGH) — see also state-management.md § GetX |

Do not mix routing frameworks. If a project already uses GetX or auto_route, treat the
go_router sections as informational only.

---

## go_router

**Priority: P0 (CRITICAL)**

<!-- Restored to P0: source flutter-go-router-navigation/SKILL.md was P0. Auth redirect guards (missing → unauthenticated access) are stop-the-world violations. -->

Merged from `flutter-navigation` and `flutter-go-router-navigation`. Use go_router for all new projects requiring declarative routing.

### Structure

```text
core/router/
├── app_router.dart   # Router configuration
└── routes.dart       # Typed route definitions (GoRouteData)
```

### Implementation Guidelines

- **Typed Routes**: Always use `GoRouteData` and `@TypedGoRoute` from `go_router_builder`. Never use raw path strings.
- **Parameters**: Define strongly-typed parameters in route class (e.g., `class OrderDetailRoute extends GoRouteData { final String id; }`) with paths like `'/orders/:id'`.
- **Root Router**: One global `GoRouter` instance registered in DI.
- **Sub-Routes**: Nest related routes using `TypedGoRoute` and children lists.
- **Redirection**: Handle auth (login check) in the `redirect` callback of `GoRouter` config: `redirect: (context, state) => isLoggedIn ? null : '/login'`. Do NOT check auth inside a page widget.
- **Tabs**: Use `StatefulShellRoute` with branches for bottom tab bar so each tab maintains its own navigation stack.
- **Transitions**: Define standard transitions (Fade, Slide) in `buildPage`.
- **Navigation**: Use `MyRoute().go(context)` or `MyRoute().push(context)`. `OrderDetailRoute(id: id).go(context)` is the only allowed way to navigate.
- **Deep Links**: Set up `AndroidManifest.xml` and `Info.plist` for URL schemes. Validate parameters in `redirect` before navigation.
- **Preserve Tab State**: Use `StatefulShellRoute` or `IndexedStack` for bottom navigation.

### Anti-Patterns

- **No raw string paths**: Use typed `GoRouteData` classes (e.g., `OrderDetailRoute(id: 123).go(context)`) instead of `context.go('/orders/123')`.
- **No inline auth logic**: Redirect logic belongs in `GoRouter.redirect`, not UI's `build()` method.
- **No multiple routers**: Register one global `GoRouter` instance in DI.
- **No unvalidated IDs**: Always verify parameters exist in `redirect` before building route.
- **No manual URL parsing**: Use go_router built-in parsing instead of `Uri.parse(url)`.
- **No manual tab state management**: Use `IndexedStack` or `StatefulShellRoute`.
- **No hardcoded route strings**: Use constants (e.g., `Routes.orders`) or code-gen.

### Typed Routes + Redirect Example

```dart
// Route Definition
@TypedGoRoute<HomeRoute>(path: '/')
class HomeRoute extends GoRouteData {
  @override
  Widget build(context, state) => const HomePage();
}

// Router Config
final router = GoRouter(
  routes: $appRoutes,
  redirect: (context, state) {
    if (notAuthenticated) return '/login';
    return null;
  },
);
```

### Route Configuration with Parameter Validation

```dart
final router = GoRouter(
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const HomeScreen(),
    ),
    GoRoute(
      path: '/orders/:id',
      redirect: (context, state) {
        final id = state.pathParameters['id'];
        if (id == null || id.isEmpty) return '/';
        return null;
      },
      builder: (context, state) => OrderDetailScreen(
        id: state.pathParameters['id']!,
      ),
    ),
  ],
);
```

### Deep Linking Configuration

```xml
<!-- AndroidManifest.xml -->
<intent-filter android:autoVerify="true">
  <action android:name="android.intent.action.VIEW" />
  <category android:name="android.intent.category.DEFAULT" />
  <category android:name="android.intent.category.BROWSABLE" />
  <data android:scheme="myapp" />
  <data android:scheme="https" android:host="example.com" />
</intent-filter>
```

```xml
<!-- Info.plist -->
<key>CFBundleURLTypes</key>
<array>
  <dict>
    <key>CFBundleURLSchemes</key>
    <array>
      <string>myapp</string>
    </array>
  </dict>
</array>
```

### Tab Navigation (State Preservation)

```dart
// Option A: IndexedStack
Scaffold(
  body: IndexedStack(
    index: _selectedIndex,
    children: [
      Navigator(onGenerateRoute: ...),
      Navigator(onGenerateRoute: ...),
    ],
  ),
  bottomNavigationBar: BottomNavigationBar(...),
);
```

---

## auto_route

**Priority: P1 (HIGH)**

### Structure

```text
core/router/
├── app_router.dart       # Router configuration
└── app_router.gr.dart    # Generated routes
```

### Implementation Workflow

1. **Annotate pages** — Mark all screen/page widgets with `@RoutePage()`.
2. **Configure router** — Extend `_$AppRouter` and annotate with `@AutoRouterConfig`.
3. **Navigate with types** — Use generated route classes (e.g., `HomeRoute()`). Never use strings.
4. **Add guards** — Implement `AutoRouteGuard` for authentication/authorization logic.
5. **Handle parameters** — Constructors of `@RoutePage` widgets automatically become route parameters.
6. **Prefer declarative calls** — Use `context.pushRoute()` or `context.replaceRoute()`.

### Anti-Patterns

- **No string-based navigation**: Use generated typed route classes (e.g., `OrderDetailRoute(id: 123)`).
- **No protected screen without `AutoRouteGuard`**: Every protected route must declare a guard; don't rely on UI-level checks.
- **No navigation calls from BLoC**: Emit state and let the Presentation layer navigate.

### Router Configuration

```dart
@AutoRouterConfig(replaceInRouteName: 'Page|Screen,Route')
class AppRouter extends _$AppRouter {
  @override
  List<AutoRoute> get routes => [
    // 1. Initial Route
    AutoRoute(page: SplashRoute.page, initial: true),

    // 2. Protected Routes (with Guards)
    AutoRoute(
      page: DashboardRoute.page,
      guards: [AuthGuard()],
    ),

    // 3. Nested Routes (Tabs)
    AutoRoute(
      page: HomeTabsRoute.page,
      children: [
        AutoRoute(page: PostsRoute.page),
        AutoRoute(page: SettingsRoute.page),
      ],
    ),
  ];
}
```

### Dynamic Tab Initialization

```dart
context.navigateTo(
  OrdersTabRoute(
    children: params.tab == OrderTab.orders()
        ? [const ViewByOrdersPageRoute()]
        : [const ViewByItemsPageRoute()],
  ),
);
```

### Typed Parameters

```dart
@RoutePage()
class UserProfilePage extends StatelessWidget {
  final String userId;
  const UserProfilePage({required this.userId});

  // Navigation: context.pushRoute(UserProfileRoute(userId: '123'));
}
```

---

## GetX Navigation

**Priority: P1 (HIGH)**

> P1 for existing GetX projects. New projects should use go_router (P0 above).

### Guidelines

- **Named Routes**: Use `Get.toNamed('/path')`. Define routes in `AppPages`.
- **Navigation APIs**:
  - `Get.to()`: Push new route.
  - `Get.off()`: Replace current route.
  - `Get.offAll()`: Clear stack and push.
  - `Get.back()`: Pop route/dialog/bottomSheet.
- **Bindings**: Link routes with `Bindings` for automated lifecycle.
- **Middleware**: Implement `GetMiddleware` for auth/permission guards.

### Anti-Patterns

- **No `Navigator.of(context)`** with GetX.
- **No hardcoded routes**: Use `Routes` constant class.
- **No direct dialogs**: Use `Get.dialog()` and `Get.snackbar()`.

### Centralized Route Management

```dart
// app_routes.dart
abstract class Routes {
  static const HOME = _Paths.HOME;
  static const LOGIN = _Paths.LOGIN;
}

abstract class _Paths {
  static const HOME = '/home';
  static const LOGIN = '/login';
}

// app_pages.dart
class AppPages {
  static const INITIAL = Routes.LOGIN;

  static final routes = [
    GetPage(
      name: _Paths.HOME,
      page: () => HomeView(),
      binding: HomeBinding(),
    ),
    GetPage(
      name: _Paths.LOGIN,
      page: () => LoginView(),
      binding: LoginBinding(),
    ),
  ];
}

// main.dart
GetMaterialApp(
  initialRoute: AppPages.INITIAL,
  getPages: AppPages.routes,
)
```

### Middleware (Auth Guard)

```dart
class AuthMiddleware extends GetMiddleware {
  @override
  int? get priority => 1;

  @override
  RouteSettings? redirect(String? route) {
    bool isAuthenticated = AuthService.to.isLoggedInValue;
    if (isAuthenticated) return null;
    return const RouteSettings(name: Routes.LOGIN);
  }
}

// Usage in AppPages
GetPage(
  name: Routes.PROFILE,
  page: () => ProfileView(),
  middlewares: [AuthMiddleware()],
)
```
