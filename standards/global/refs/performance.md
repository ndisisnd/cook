# Performance

## Workflow

1. **Baseline** — profile before changing anything. Measure CPU, memory, and latency.
2. **Identify** — find the top bottleneck: N+1 query, hot loop, or memory leak.
3. **Fix** — apply a targeted optimization from the patterns below.
4. **Verify** — re-profile to confirm improvement and check for regressions.

Never optimize without a measurement. Fix proven bottlenecks only.

## Memory

- Explicit cleanup of listeners, observers, subscriptions, and streams.
- Use `Set` for lookups, arrays for iteration — pick the right structure for the access pattern.
- Initialize expensive objects lazily, only when first needed.

## CPU

- Target O(1) or O(n) for critical paths. Avoid O(n²).
- Offload heavy computations to background threads, workers, or isolates.
- Memoize pure, expensive functions when inputs repeat.

```typescript
// Memoization — avoid recomputing expensive transforms
const cache = new Map<string, Result>();
function getExpensiveResult(key: string): Result {
  if (!cache.has(key)) {
    cache.set(key, computeExpensive(key));
  }
  return cache.get(key)!;
}
```

## Network and I/O

- Always use async I/O. Never block the main thread on file or network access.
- Batch multiple small requests into single bulk operations.

```python
# Batching — avoid N+1 API calls
# Bad:  [fetch(f"/users/{id}") for id in ids]
# Good:
results = fetch("/users", params={"ids": ",".join(ids)})
```

- Apply multi-level caching (memory → storage → network) with appropriate TTL and invalidation strategy.
- Use efficient serialization (Protobuf, compressed JSON) and enable compression (gzip/br) for large payloads.

## UI

- Avoid unnecessary re-renders: memoize stable callbacks and computed values only when there is a measured reason.
- Avoid data waterfalls: fetch in parallel at the highest appropriate boundary.
- Offload animation and interaction work off the main thread.
- Virtualize long lists — never render unbounded item counts into the DOM or widget tree.
- Tree-shake unused code and dependencies at build time.

## Database

- No N+1 queries. Batch or join data access.
- Index every foreign key and filter column used in hot queries.

## Monitoring

- Define SLIs (latency, throughput, error rate) and SLOs before shipping a new service.
- Write micro-benchmarks for performance-critical functions.
- Load test under peak and stress conditions before release.
