# Node.js Async Errors

Use this ref for Node-specific promise rejection lifecycle, callback/timer/event-boundary throws, global process handlers, and runtime timeout/cancellation mechanics. Error envelopes and domain error taxonomy live in `global/refs/error-handling.md`.

## Promise Rejections

- Await, return, or catch every promise. A floating promise can become an unhandled process-level rejection outside the caller's control. Signal: promise-returning call on its own line with no `await`, `return`, `.catch`, or documented fire-and-forget helper.
- `void promise` is not a rejection handler. It is acceptable only when the callee attaches `.catch()` or routes through a helper that logs and owns failures.
- Prefer one local error boundary per unit of work. Do not depend on `process.on('unhandledRejection')` for normal behaviour.

```js
function fireAndForget(promise, context) {
  promise.catch((error) => logger.error({ error, context }, 'background task failed'));
}
```

## Callback And Event Boundaries

- A `throw` inside `setTimeout`, `setImmediate`, an `EventEmitter` callback, or a stream callback is not caught by the original async call site. Catch locally and reject, emit `'error'`, or pass the error to the callback convention. Signal: bare `throw` inside one of those callbacks.
- For EventEmitters, always register an `'error'` listener when the emitter can emit errors. Signal: custom emitter or stream instance with success listeners only.
- Convert callback APIs to promises with `util.promisify` or a small wrapper when it makes error flow explicit.

## Global Process Handlers

- `unhandledRejection` and `uncaughtException` handlers are for logging, draining, and exiting. They are not retry loops, fallback handlers, or response paths.
- Never resume normal operation after `uncaughtException`; the process may be in an unknown state.
- Keep handler code minimal and defensive. Avoid async work that can hang forever unless guarded by the shutdown deadline from `refs/runtime-safety.md`.

```js
process.on('uncaughtException', (error) => {
  logger.fatal({ error }, 'uncaught exception');
  initiateShutdown('uncaughtException');
});
```

## Timeouts And Cancellation

- Bound outbound `fetch` calls with `AbortController`/`AbortSignal.timeout()` where supported.
- Use driver-native timeout settings when libraries do not support abort signals: request timeout, query timeout, statement timeout, connection acquisition timeout, or SDK-specific cancellation.
- Propagate cancellation into downstream work where the client disconnected or the deadline has expired. Signal: external I/O in handlers with no timeout or abort path.

```js
const signal = AbortSignal.timeout(5_000);
const response = await fetch(url, { signal });
```

## Anti-Patterns

- Floating promises
- `void` without `.catch()` or a rejection-owning helper
- Business logic in process-level exception handlers
- Continuing after `uncaughtException`
- Bare `throw` inside timer, event, or stream callbacks
- Outbound I/O with no deadline
