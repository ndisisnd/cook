# React Performance

## Eliminate Data Waterfalls (P0)

Fetch independent data in parallel. Sequential `await` chains are the most common cause of slow initial loads.

```tsx
// Bad — sequential, each waits for the previous
const user = await getUser();
const products = await getProducts();

// Good — parallel
const [user, products] = await Promise.all([getUser(), getProducts()]);
```

Start fetches before render using route loaders or event handlers:

```tsx
// React Router v6 loader
export async function loader() {
  return Promise.all([getUser(), getProducts()]);
}
```

Use Suspense boundaries to stream partial content so the page is not blank while slow data loads:

```tsx
function App() {
  return (
    <Suspense fallback={<PageSkeleton />}>
      <Dashboard />
    </Suspense>
  );
}
```

## Reduce Bundle Size (P0)

Lazy-load heavy components so they are not included in the initial bundle:

```tsx
const Chart = React.lazy(() => import('./Chart'));
const RichEditor = React.lazy(() => import('./RichEditor'));

function Page() {
  return (
    <Suspense fallback={<Skeleton />}>
      <Chart />
    </Suspense>
  );
}
```

### Native Image Lazy-Loading

Defer off-screen images with native browser attributes — no library required:

```tsx
<img src={src} alt={alt} loading="lazy" decoding="async" />
```

For Next.js projects, prefer `next/image` (automatic sizing, format negotiation, and
lazy-loading) — see the nextjs domain. In plain React, the native attributes above are
the baseline.

Avoid barrel files (`index.ts` that re-exports everything) — they prevent tree-shaking. Import directly from the source file.

Replace heavy libraries with lighter alternatives before shipping: `moment` → `dayjs`, `lodash` → native or `radash`.

Analyse the bundle before each significant release:

```bash
# Vite
npx vite-bundle-visualizer

# webpack
npx webpack-bundle-analyzer stats.json
```

## Minimize Re-renders (P1)

Move state as close to its consumer as possible. A state update re-renders the owner and all its descendants.

Memoize list items when the list is long and items are expensive to render:

```tsx
const Row = React.memo(function Row({ item }: { item: Item }) {
  return <tr><td>{item.name}</td></tr>;
});
```

Virtualize lists with 500+ items:

```tsx
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualList({ items }: { items: Item[] }) {
  const parentRef = useRef<HTMLDivElement>(null);
  const virtualizer = useVirtualizer({ count: items.length, getScrollElement: () => parentRef.current, estimateSize: () => 40 });

  return (
    <div ref={parentRef} style={{ height: 600, overflow: 'auto' }}>
      <div style={{ height: virtualizer.getTotalSize() }}>
        {virtualizer.getVirtualItems().map((vItem) => (
          <div key={vItem.key} style={{ transform: `translateY(${vItem.start}px)` }}>
            {items[vItem.index].name}
          </div>
        ))}
      </div>
    </div>
  );
}
```

Split Context into State and Dispatch to prevent consumers of dispatch-only from re-rendering on state changes (see state-management ref).

Use `startTransition` to mark non-urgent state updates so React can interrupt them for higher-priority input events:

```tsx
import { startTransition } from 'react';

function Search() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setQuery(e.target.value); // urgent — update input immediately
    startTransition(() => setResults(search(e.target.value))); // non-urgent
  }

  return <input value={query} onChange={handleChange} />;
}
```

## Move Heavy Computation Off the Main Thread (P1)

Use a Web Worker for encryption, image processing, or sorting large datasets:

```tsx
// worker.ts
self.addEventListener('message', (e: MessageEvent) => {
  self.postMessage(heavySort(e.data));
});

// component
function SortedTable({ data }: { data: Row[] }) {
  const [sorted, setSorted] = useState<Row[]>([]);

  useEffect(() => {
    const worker = new Worker(new URL('./worker.ts', import.meta.url), { type: 'module' });
    worker.postMessage(data);
    worker.onmessage = (e) => setSorted(e.data);
    return () => worker.terminate();
  }, [data]);

  return <Table rows={sorted} />;
}
```

## Profiling

Use the React DevTools Profiler to find which component commits are slow before optimising:

```tsx
import { Profiler } from 'react';

function onRender(id: string, phase: string, actualDuration: number) {
  if (actualDuration > 16) console.warn(`${id} (${phase}): ${actualDuration}ms`);
}

<Profiler id="Dashboard" onRender={onRender}>
  <Dashboard />
</Profiler>
```
