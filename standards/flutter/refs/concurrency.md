# Flutter Concurrency (Isolates & compute)

**Priority: P1**

## Core Concepts

Dart uses a single-threaded event loop. All Flutter code runs on the Main Isolate by default. Blocking it causes jank.

- **async/await**: For non-blocking I/O (network, file). The event loop continues while waiting.
- **Isolates**: Dart's lightweight threads with isolated memory. Communicate via message passing only.

## Decision Matrix

| Condition | Approach |
|-----------|----------|
| I/O bound (HTTP, database) | `async`/`await` on Main Isolate |
| CPU-bound, < 16ms | `async`/`await` on Main Isolate |
| CPU-bound, one-off heavy task | `Isolate.run()` |
| Continuous background processing | `Isolate.spawn()` with ports |

## Workflow: Offloading Heavy Computation

- [ ] 1. Identify the CPU-bound operation blocking the UI.
- [ ] 2. Extract computation into a standalone top-level or static function.
- [ ] 3. Ensure the function accepts exactly one argument (Isolate constraint).
- [ ] 4. Call `Isolate.run(() => myFunction(data))`.
- [ ] 5. `await` the result on the Main Isolate.

## Workflow: Long-Lived Worker Isolate

- [ ] 1. Create a `ReceivePort` on the Main Isolate.
- [ ] 2. Spawn worker with `Isolate.spawn(entryPoint, mainPort.sendPort)`.
- [ ] 3. In worker, create its own `ReceivePort` and send its `SendPort` back.
- [ ] 4. Store worker's `SendPort` for bidirectional communication.
- [ ] 5. Close ports and kill isolate on dispose.

## Anti-Patterns

- **No JSON parsing on Main Isolate**: Large JSON decoding (>1MB) blocks frames. Use `Isolate.run`.
- **No shared mutable state**: Isolates cannot share memory. Pass data via messages.
- **No `FutureBuilder` in build without caching**: `FutureBuilder` re-fires on every rebuild if the future is created inline.

## Verification

- [ ] No frame drops during heavy computation (check with DevTools).
- [ ] Worker isolates are disposed when no longer needed.
- [ ] `flutter test` passes.

## One-Off Heavy Computation (Isolate.run)

```dart
import 'dart:convert';
import 'dart:isolate';

// Top-level function — required for Isolate.run
List<dynamic> _decodeJson(String jsonString) {
  return jsonDecode(jsonString) as List<dynamic>;
}

// Usage in ViewModel/Repository
Future<List<dynamic>> processLargeJson(String rawJson) async {
  // Spawns isolate, runs computation, returns result, exits automatically
  return await Isolate.run(() => _decodeJson(rawJson));
}
```

## Long-Lived Worker Isolate

```dart
import 'dart:isolate';

class ImageProcessor {
  late SendPort _workerSendPort;
  final ReceivePort _mainPort = ReceivePort();
  Isolate? _isolate;

  Future<void> initialize() async {
    _isolate = await Isolate.spawn(_workerEntry, _mainPort.sendPort);

    _mainPort.listen((message) {
      if (message is SendPort) {
        _workerSendPort = message;
      } else {
        print('Processed: $message');
      }
    });
  }

  void processImage(String path) {
    _workerSendPort.send(path);
  }

  static void _workerEntry(SendPort mainSendPort) {
    final workerPort = ReceivePort();
    mainSendPort.send(workerPort.sendPort);

    workerPort.listen((message) {
      final result = 'Processed image: $message';
      mainSendPort.send(result);
    });
  }

  void dispose() {
    _mainPort.close();
    _isolate?.kill();
  }
}
```

## FutureBuilder Caching

```dart
// ✅ RIGHT — cache the future to prevent re-firing on rebuild
class _MyWidgetState extends State<MyWidget> {
  late final Future<String> _dataFuture;

  @override
  void initState() {
    super.initState();
    _dataFuture = fetchData(); // Created once
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<String>(
      future: _dataFuture, // Same instance every rebuild
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const CircularProgressIndicator();
        }
        return Text(snapshot.data ?? 'No data');
      },
    );
  }
}

// ❌ WRONG — future re-created on every build
class MyWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return FutureBuilder<String>(
      future: fetchData(), // <-- New future every rebuild!
      builder: (context, snapshot) {
        return Text(snapshot.data ?? 'Loading...');
      },
    );
  }
}
```
