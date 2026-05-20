# TypeScript Testing Patterns

## Type-Safe Mocking

Use `satisfies jest.Mocked<T>` when constructing a mock object — it fails at compile time if any required member is missing:

```typescript
import { jest } from '@jest/globals';
import type { UserRepository } from '../user.repository';

const mockRepo = {
  findById: jest.fn(),
  save:     jest.fn(),
  delete:   jest.fn(),
} satisfies jest.Mocked<UserRepository>;

const service = new UserService(mockRepo as unknown as UserRepository);
```

For complex partial mocks where you cannot satisfy every member, use `as unknown as T` — never cast directly `as T` without going through `unknown`, as the direct cast hides real incompatibilities.

## Mocking Async Methods

```typescript
mockRepo.findById.mockResolvedValue({ id: '1', name: 'Alice' });
mockRepo.findById.mockRejectedValue(new Error('not found'));

// Assert async behaviour
await expect(service.getUser('missing')).rejects.toThrow('not found');
```

## Organising Tests

- Mirror `src/` under `test/`: `src/user/user.service.ts` → `test/user/user.service.test.ts`.
- Use `describe()` to group related cases. `beforeEach()` / `afterEach()` for per-test setup and teardown — never share mutable state across tests without resetting in `beforeEach`.
- Write test names as sentences describing observable behaviour: `'returns null when user not found'` not `'test getUser null case'`.
- One focused assertion per test where practical — isolates failure signals.

## Common Failure Patterns

### Method mismatch
**Symptom**: Test stubs a method that the implementation never calls, or misses one it does.
**Fix**: Read the service implementation before writing mocks. Mock what the code actually calls.

### Error message mismatch
**Symptom**: `rejects.toThrow('...')` fails despite the error being thrown.
**Fix**: Import error message constants from the source module — never hardcode strings in tests.

### Incomplete mock object
**Symptom**: TypeScript error — mock doesn't satisfy the interface.
**Fix**: Add missing members, or use `satisfies jest.Mocked<T>` to surface the gap at compile time rather than runtime.

### Enum values in test data
**Symptom**: Test passes string literals where enum-typed values are expected; narrowing fails at runtime.
**Fix**: Import and use the enum values directly (`Status.ACTIVE`, not `'active'`).

## Anti-Patterns

- Hardcoded error message strings in assertions — import from the source constant
- Testing private methods or internal state — test observable behaviour only
- Shared mutable mock state across tests without `beforeEach` reset — tests become order-dependent
- String literals in place of enum values in test data
