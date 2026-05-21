# Flutter Notifications (FCM + flutter_local_notifications)

**Priority: P1 (OPERATIONAL)**

## Implementation Workflow

1. **Set up packages** — Add `firebase_messaging` (Push) and `flutter_local_notifications` (Local/Foreground).
2. **Request permission** — Prime users with a custom dialog explaining benefits _before_ the system prompt.
3. **Handle all lifecycle states** — Implement handlers for Foreground, Background, and Terminated states.
4. **Validate payloads** — Strictly validate notification data before navigating to screens.
5. **Clear badges** — Manually clear iOS app badges when visiting relevant screens.

## Anti-Patterns

- **No early permission popups**: Show a primer dialog explaining value first.
- **No missing `getInitialMessage()`**: Always handle "open from terminated" startup state.
- **No uncleared badges**: Manually clear notification badges upon related screen visits.
- **No unvalidated payloads**: Validate all JSON data before navigating on click.

## Setup

```yaml
dependencies:
  firebase_messaging: ^14.7.0
  flutter_local_notifications: ^16.3.0
```

## Lifecycle Handlers (Quick Reference)

```dart
// Foreground
FirebaseMessaging.onMessage.listen((message) {
  _showLocalNotification(message);
});

// Background (app open but not in foreground)
FirebaseMessaging.onMessageOpenedApp.listen((message) {
  _handleNavigation(message.data);
});

// Terminated (cold start from notification tap)
final initialMessage = await FirebaseMessaging.instance.getInitialMessage();
if (initialMessage != null) _handleNavigation(initialMessage.data);
```

## Initialization & Permission

```dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();

  final messaging = FirebaseMessaging.instance;
  await messaging.requestPermission(
    alert: true, badge: true, sound: true,
  );

  final token = await messaging.getToken();
  runApp(MyApp());
}
```

## Notification Service

```dart
class NotificationService {
  final FirebaseMessaging _messaging = FirebaseMessaging.instance;
  final FlutterLocalNotificationsPlugin _local = FlutterLocalNotificationsPlugin();

  Future<void> initialize() async {
    // 1. Init Local Notifications
    await _local.initialize(
      InitializationSettings(
        android: AndroidInitializationSettings('@mipmap/ic_launcher'),
        iOS: DarwinInitializationSettings(),
      ),
      onDidReceiveNotificationResponse: _onTap,
    );

    // 2. Foreground Stream
    FirebaseMessaging.onMessage.listen(_showLocal);

    // 3. Background/Terminated -> Opened
    FirebaseMessaging.onMessageOpenedApp.listen(_handleTap);

    // 4. Terminated -> Launched
    final initialMsg = await _messaging.getInitialMessage();
    if (initialMsg != null) _handleTap(initialMsg);
  }

  void _showLocal(RemoteMessage msg) {
    _local.show(
      msg.hashCode,
      msg.notification?.title,
      msg.notification?.body,
      NotificationDetails(
        android: AndroidNotificationDetails('default', 'Default',
            importance: Importance.max, priority: Priority.high),
        iOS: DarwinNotificationDetails(),
      ),
      payload: jsonEncode(msg.data),
    );
  }

  void _handleTap(RemoteMessage msg) {
    // Navigate based on payload
  }
}
```

## Permission Priming (Recommended)

Explain benefits before system dialog:

```dart
Future<void> requestPermission(BuildContext context) async {
  final userAgreed = await showDialog<bool>(...); // Show explanation dialog
  if (userAgreed == true) {
    await FirebaseMessaging.instance.requestPermission();
  }
}
```

## iOS Badge Management

```dart
_local.resolvePlatformSpecificImplementation<IOSFlutterLocalNotificationsPlugin>()
    ?.setApplicationIconBadgeNumber(0); // Clear badge
```
