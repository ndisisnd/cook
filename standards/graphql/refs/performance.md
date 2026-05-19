# GraphQL Performance

> Source: [N+1 with DataLoader – graphql-js.org](https://www.graphql-js.org/docs/n1-dataloader/) · [Handling N+1 – Apollo](https://www.apollographql.com/docs/graphos/schema-design/guides/handling-n-plus-one) · [Caching – graphql.org](https://graphql.org/learn/caching/) · [Performance – graphql.org](https://graphql.org/learn/performance/)

## The N+1 Problem

When a resolver fetches a related entity for each item in a list, it triggers one database query per item. A query for 100 posts and their authors fires 101 queries — 1 for the list, then 1 per post ([graphql-js.org](https://www.graphql-js.org/docs/n1-dataloader/)):

```typescript
// BAD — N+1: one query per post
const resolvers = {
  Post: {
    author: (post) => db.users.findById(post.authorId), // called N times
  },
};
```

Use **DataLoader** to batch and deduplicate these loads within a single request.

---

## DataLoader

DataLoader collects all `.load(key)` calls made during a single event-loop tick and batches them into one `batchLoadFn(keys)` call ([graphql-js.org](https://www.graphql-js.org/docs/n1-dataloader/)):

```typescript
import DataLoader from 'dataloader';

// Batch function — receives all keys collected in one tick
const userLoader = new DataLoader(async (userIds: readonly string[]) => {
  const users = await db.users.findMany({ where: { id: { in: [...userIds] } } });
  // Result must be in the same order as userIds (DataLoader contract)
  const userMap = new Map(users.map(u => [u.id, u]));
  return userIds.map(id => userMap.get(id) ?? null);
});
```

### Attach Loaders to Request Context

Create a **new DataLoader instance per request** — never share a loader across requests (it would leak data across users):

```typescript
// context.ts
export function createContext({ req }: { req: Request }) {
  return {
    user: req.user,
    loaders: {
      user: new DataLoader(batchLoadUsers),
      product: new DataLoader(batchLoadProducts),
      category: new DataLoader(batchLoadCategories),
    },
  };
}

// resolver
const resolvers = {
  Post: {
    author: (post, _, { loaders }) => loaders.user.load(post.authorId),
  },
  OrderItem: {
    product: (item, _, { loaders }) => loaders.product.load(item.productId),
  },
};
```

### DataLoader Rules

- **Always return results in the same order as input keys.** DataLoader maps result[i] to keys[i] — wrong order corrupts data silently.
- **Batch functions must return one result per key**, using `null` for missing entries (not a shorter array).
- Use `.load(id)` in field resolvers — not `.loadMany()` — since `.load()` already batches all calls in the same tick.
- Each loader should handle **one specific data access pattern**; don't combine unrelated fetches in one batch function.
- Use `.prime(key, value)` to pre-populate the cache when you already have data, avoiding redundant lookups.

```typescript
// .prime() — if you fetched a list, pre-populate the cache
async function getUsers(filter: UserFilter, loaders: Loaders) {
  const users = await db.users.findMany(filter);
  users.forEach(u => loaders.user.prime(u.id, u)); // warm the cache
  return users;
}
```

---

## HTTP Caching

GraphQL typically uses POST, which is not cached by browsers or CDNs. To enable HTTP caching for read operations ([graphql.org](https://graphql.org/learn/caching/)):

- Use **GET requests** for queries (not mutations). GET is cacheable by default; POST is not.
- Include cache-control headers (`Cache-Control: max-age=60, public`) on cacheable query responses.
- Use **persisted queries** to make GET-based caching practical — short hashes fit in a URL; full query strings do not.

```
# GET-based query with persisted query hash
GET /graphql?operationName=GetUser&variables={"id":"123"}&extensions={"persistedQuery":{"sha256Hash":"abc..."}}
```

### Apollo Client Normalized Cache

Apollo Client normalizes cached objects by `__typename` + `id`. To leverage this:

- Always request `id` (and `__typename`) on every entity type.
- Mutation payloads that return the modified entity automatically update all related cache entries.

```graphql
# Always include id so Apollo can normalize
query GetPost($id: ID!) {
  post(id: $id) {
    id          # required for normalization
    __typename  # returned automatically but explicit is fine
    title
    author {
      id
      displayName
    }
  }
}
```

---

## Response Compression

Enable gzip/brotli compression on the HTTP layer — GraphQL JSON responses compress extremely well ([graphql.org](https://graphql.org/learn/best-practices/#json-with-gzip)):

```typescript
import compression from 'compression';
app.use(compression());
```

---

## Query Execution Performance

- **Avoid `SELECT *`** in resolvers — resolve only the fields that were requested. Use the `info` argument to inspect the selection set if needed.
- **Avoid deeply nested resolver chains** — resolve parent and child in one query when the relationship is always required.
- **Cache at the resolver level** for expensive computations that don't vary per user (use `@cacheControl` directives with Apollo):

```graphql
type Query {
  popularProducts: [Product!]! @cacheControl(maxAge: 300)  # 5 min TTL
}
```

---

## Anti-Patterns

- Fetching related entities in field resolvers without DataLoader
- Sharing a DataLoader instance across requests (data leak between users)
- Returning results from a batch function in a different order than the input keys
- Using `.loadMany()` in field resolvers instead of `.load()` (defeats batching)
- Using POST for all operations — prevents HTTP caching for queries
- Resolving large lists without pagination (unbounded queries)
- `SELECT *` in resolvers regardless of which fields were requested
- No `id` field on entities — prevents Apollo Client cache normalization
