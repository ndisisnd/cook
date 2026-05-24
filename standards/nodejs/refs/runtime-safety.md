# Node.js Runtime Safety

Use this ref when the task touches event-loop latency, streams, buffers, worker threads, process signals, or shutdown behaviour. Keep API contracts in `global/refs/api-design.md`, general performance strategy in `global/refs/performance.md`, and persistence rules in `standards/database/`.

## Event Loop Budget

- Treat the request path as latency-sensitive. Avoid sync filesystem, sync crypto, compression, image transforms, large JSON serialization/parsing, and tight CPU loops in handlers. Signal: `*Sync` APIs or CPU-heavy loops inside request, webhook, queue-consumer, or subscription handlers.
- Move CPU-heavy work to `worker_threads`, a job queue, or another process. Keep worker message payloads small enough that serialization does not become the new bottleneck. Signal: CPU-heavy work still runs inline after a worker/queue abstraction exists.
- Measure before tuning. Use Node profiler output, event-loop-delay metrics, or production traces for large changes; general profiling workflow lives in `global/refs/performance.md`.

## Streams And Backpressure

- Prefer `stream.pipeline()` or `stream/promises.pipeline()` for multi-stream flows. It wires error propagation and cleanup across the full chain. Signal: a manually chained stream flow where one stream error can leave another open.
- If using `.pipe()`, attach error handling and teardown for every stream in the chain. Signal: `readable.pipe(writable)` with no `'error'`, close, abort, or cleanup path.
- Check the return value of `writable.write()`. When it returns `false`, pause production and resume on `'drain'`. Signal: `.write()` inside a loop without a `false` branch.

```js
import { pipeline } from 'node:stream/promises';

await pipeline(source, transform, destination);
```

## Buffer Safety

- Use `Buffer.alloc(size)` when bytes may be observed before full overwrite.
- Use `Buffer.allocUnsafe(size)` only when code overwrites every byte before any read, log, response, persistence, crypto/compression input, or serialization. Signal: unsafe buffer data reaches an external sink without an obvious complete overwrite.
- Never reuse request buffers across tenants or users unless ownership and overwrite are explicit.

## Graceful Shutdown

- Trap `SIGTERM` and `SIGINT` for long-lived services. Stop accepting new work, fail readiness, drain in-flight work, close pools/listeners, then exit.
- Always set a hard deadline shorter than the orchestrator's kill timeout. Signal: a shutdown path that can wait forever on in-flight requests or database close.
- Never call `process.exit()` inside a request handler. Return an error or trip readiness and let the supervisor restart the process.

```js
const server = app.listen(port);
let shuttingDown = false;

async function shutdown(signal) {
  if (shuttingDown) return;
  shuttingDown = true;
  readiness.fail(signal);

  const deadline = setTimeout(() => process.exit(1), 25_000);
  deadline.unref();

  server.close(async () => {
    try {
      await Promise.all([db.end(), redis.quit()]);
      process.exit(0);
    } catch (error) {
      logger.error({ error }, 'shutdown cleanup failed');
      process.exit(1);
    }
  });
}

process.once('SIGTERM', shutdown);
process.once('SIGINT', shutdown);
```

## Anti-Patterns

- Sync fs/crypto/compression in handlers
- CPU-heavy transforms inline on the event loop
- Stream chains with no error cleanup
- Ignoring `write()` backpressure
- `Buffer.allocUnsafe` sent externally before complete overwrite
- Shutdown without readiness change or deadline
