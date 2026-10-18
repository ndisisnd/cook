---
last_reviewed: 2026-10-18
---

# TypeScript Testing Patterns

Examples use Vitest (default for new projects). Jest equivalents: `jest.fn` and `jest.mocked` from `@jest/globals`.

## Type-Safe Mocking

Type each mock function with the member it replaces, then check the object with `satisfies`. A missing or mistyped member fails at compile time, and no cast is needed:

```typescript
import { vi } from 'vitest';
import type { UserRepository } from './user.repository.ts';

const mockRepo = {
  findById: vi.fn<UserRepository['findById']>(),
  save:     vi.fn<UserRepository['save']>(),
  delete:   vi.fn<UserRepository['delete']>(),
} satisfies UserRepository;

const service = new UserService(mockRepo);
```

For a partial mock where you cannot satisfy every member, cast through `unknown` (`as unknown as T`) — never cast directly `as T`, which hides real incompatibilities. For module mocks, wrap the import with `vi.mocked(fn)` to get typed mock methods.

## Mocking Async Methods

```typescript
mockRepo.findById.mockResolvedValue({ id: '1', name: 'Alice' });
mockRepo.findById.mockRejectedValue(new Error('not found'));

// Assert async behaviour — always await the assertion
await expect(service.getUser('missing')).rejects.toThrow('not found');
```

## Organising Tests

- Co-locate tests with the source: `src/user/user.service.ts` → `src/user/user.service.test.ts`. The runner config in `refs/tooling.md` matches `src/**/*.test.ts`.
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
**Symptom**: TypeScript error — mock does not satisfy the interface.
**Fix**: Add missing members, or use the `satisfies` pattern above to surface the gap at compile time rather than runtime.

### Loosely typed test data
**Symptom**: A fixture typed as `string` or `object` is passed where a literal union is expected; the compiler rejects it, or a cast hides a wrong value.
**Fix**: Annotate fixtures with the domain type or `satisfies`, or use the source `as const` object (`Status.Active`).

## Anti-Patterns

- Hardcoded error message strings in assertions — import from the source constant
- Testing private methods or internal state — test observable behaviour only
- Shared mutable mock state across tests without `beforeEach` reset — tests become order-dependent
- Fixtures cast with `as T` instead of typed with the domain type or `satisfies`
- Un-awaited `expect(...).rejects` / `.resolves` assertions
