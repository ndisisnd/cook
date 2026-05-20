# GraphQL Testing

> Source: [Testing – Apollo Server docs](https://www.apollographql.com/docs/apollo-server/testing/testing/) · [Jest](https://jestjs.io/) · [graphql-js executeOperation](https://graphql.org/graphql-js/execution/)

## Unit Testing Resolvers

Test individual resolver functions by calling them directly with a mocked context. This isolates the resolver from the HTTP layer and from real services, making tests fast and deterministic.

```typescript
// users.resolver.test.ts
import { resolvers } from './users.resolver';

const mockServices = {
  user: {
    findById: jest.fn(),
    create: jest.fn(),
  },
};

const mockLoaders = {
  user: { load: jest.fn() },
};

function makeContext(overrides = {}) {
  return {
    user: { id: 'user-1', role: 'USER' },
    services: mockServices,
    loaders: mockLoaders,
    ...overrides,
  };
}

beforeEach(() => jest.resetAllMocks());

describe('Query.user', () => {
  it('returns the user from the service', async () => {
    const expected = { id: 'user-1', firstName: 'Ada' };
    mockServices.user.findById.mockResolvedValue(expected);

    const result = await resolvers.Query.user({}, { id: 'user-1' }, makeContext(), {} as any);

    expect(mockServices.user.findById).toHaveBeenCalledWith('user-1');
    expect(result).toEqual(expected);
  });

  it('returns null when the user is not found', async () => {
    mockServices.user.findById.mockResolvedValue(null);
    const result = await resolvers.Query.user({}, { id: 'missing' }, makeContext(), {} as any);
    expect(result).toBeNull();
  });
});

describe('Post.author', () => {
  it('loads the author via DataLoader, not direct DB', async () => {
    const author = { id: 'user-1', firstName: 'Ada' };
    mockLoaders.user.load.mockResolvedValue(author);

    const post = { id: 'post-1', authorId: 'user-1' };
    const result = await resolvers.Post.author(post, {}, makeContext(), {} as any);

    expect(mockLoaders.user.load).toHaveBeenCalledWith('user-1');
    expect(result).toEqual(author);
  });
});
```

---

## Integration Testing with executeOperation

Spin up a real Apollo Server instance (without HTTP) and execute operations using `executeOperation`. This tests the full resolver chain — including context creation, middleware, and error formatting — without the complexity of HTTP.

```typescript
// server.integration.test.ts
import { ApolloServer } from '@apollo/server';
import { schema } from '../schema';
import { createContext } from '../context';

let server: ApolloServer;

beforeAll(async () => {
  server = new ApolloServer({ schema });
  await server.start();
});

afterAll(async () => {
  await server.stop();
});

it('returns a user by id', async () => {
  const response = await server.executeOperation(
    {
      query: `query GetUser($id: ID!) {
        user(id: $id) {
          id
          firstName
          email
        }
      }`,
      variables: { id: 'user-1' },
    },
    {
      contextValue: createContext({ req: { user: { id: 'user-1', role: 'USER' } } }),
    },
  );

  expect(response.body.kind).toBe('single');
  const data = (response.body as any).singleResult.data;
  expect(data.user).toMatchObject({ id: 'user-1', firstName: 'Ada' });
  expect((response.body as any).singleResult.errors).toBeUndefined();
});
```

---

## Testing Mutations and userErrors

Assert on both the success path (entity returned, `userErrors` empty) and the failure path (entity null, `userErrors` populated). Never assume a mutation succeeded without checking `userErrors`.

```typescript
it('returns userErrors when the email is already taken', async () => {
  const response = await server.executeOperation(
    {
      query: `mutation CreateUser($input: CreateUserInput!) {
        createUser(input: $input) {
          user { id }
          userErrors { field message code }
        }
      }`,
      variables: {
        input: { firstName: 'Ada', lastName: 'L', email: 'taken@example.com', role: 'USER' },
      },
    },
    { contextValue: makeContext() },
  );

  const { data } = (response.body as any).singleResult;
  expect(data.createUser.user).toBeNull();
  expect(data.createUser.userErrors).toHaveLength(1);
  expect(data.createUser.userErrors[0]).toMatchObject({
    field: ['email'],
    code: 'DUPLICATE',
  });
});
```

---

## Schema Snapshot Testing

Print the SDL of the schema and diff it against a stored snapshot on every CI run. Catches accidental breaking changes (renamed fields, removed types, changed nullability) before they reach clients.

```typescript
// schema.snapshot.test.ts
import { printSchema } from 'graphql';
import { schema } from '../schema';

it('schema SDL matches snapshot', () => {
  expect(printSchema(schema)).toMatchSnapshot();
});
```

When a deliberate schema change is made, update the snapshot explicitly (`jest --updateSnapshot`) and review the diff in the PR. A snapshot diff is the cheapest form of a breaking-change check.

---

## Testing DataLoader Batch Functions

Test the batch function directly, not through a resolver. Verify ordering (DataLoader maps `result[i]` to `keys[i]`), null handling for missing entries, and that the underlying query is batched correctly.

```typescript
// user.loader.test.ts
import { batchLoadUsers } from './user.loader';

it('returns users in the same order as input keys', async () => {
  // DB returns users in a different order than requested
  jest.spyOn(db.users, 'findMany').mockResolvedValue([
    { id: 'b', name: 'B' },
    { id: 'a', name: 'A' },
  ]);

  const result = await batchLoadUsers(['a', 'b', 'c']);

  expect(result[0]).toMatchObject({ id: 'a' }); // key[0] → result[0]
  expect(result[1]).toMatchObject({ id: 'b' }); // key[1] → result[1]
  expect(result[2]).toBeNull();                  // missing key → null, not missing
});

it('makes a single batched DB call for all keys', async () => {
  const spy = jest.spyOn(db.users, 'findMany').mockResolvedValue([]);
  await batchLoadUsers(['a', 'b', 'c']);
  expect(spy).toHaveBeenCalledTimes(1);
  expect(spy).toHaveBeenCalledWith({ where: { id: { in: ['a', 'b', 'c'] } } });
});
```

---

## Testing Error Paths

Test that GraphQL-level errors (not `userErrors`) are only thrown for unexpected/server-side failures, not for business logic failures.

```typescript
it('throws a GraphQL error on unexpected service failure', async () => {
  mockServices.user.findById.mockRejectedValue(new Error('DB connection lost'));

  const response = await server.executeOperation(
    { query: `query { user(id: "1") { id } }` },
    { contextValue: makeContext() },
  );

  const { errors } = (response.body as any).singleResult;
  expect(errors).toHaveLength(1);
  // In production, stack traces must be stripped — assert the message is safe
  expect(errors[0].message).not.toMatch(/DB connection/);
});
```

---

## Anti-Patterns

- Mocking at the HTTP layer (supertest) instead of using `executeOperation` — hides resolver-level errors behind HTTP status codes
- Sharing a server instance across test files without resetting mocks — causes flaky tests from state leakage
- Not resetting mocks between tests (`jest.resetAllMocks()` in `beforeEach`) — earlier test outcomes bleed into later ones
- Testing only the happy path and ignoring `userErrors` — mutations with partial failures silently pass
- Hardcoding context values (e.g., `user: null`) in helpers without making them overridable — impossible to test auth-dependent behavior
- Testing resolvers through HTTP (`fetch`) — slow, couples tests to port availability, and tests the wrong layer
- Not asserting on `errors` being `undefined` when testing successful operations — response can have both `data` and `errors` simultaneously
