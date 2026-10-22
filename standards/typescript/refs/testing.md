---
last_reviewed: 2026-10-18
---

# TypeScript Testing Patterns

Examples use Vitest (default for new projects). Jest equivalents: `jest.fn` and `jest.mocked` from `@jest/globals`.

## Type-Safe Mocking

Type each mock function with the member it replaces, then check the object with `satisfies`. A missing or mistyped member fails at compile time, with no cast:

```typescript
const mockRepo = {
  findById: vi.fn<UserRepository['findById']>(),
  save:     vi.fn<UserRepository['save']>(),
} satisfies UserRepository;
```

- Partial mock: cast through `unknown` (`as unknown as T`) — never `as T` directly, which hides real incompatibilities.
- Module mocks: wrap with `vi.mocked(fn)` for typed mock methods.
- Async: `mockResolvedValue` / `mockRejectedValue`; always `await expect(...).rejects.toThrow(...)`.

## Organising Tests

- Co-locate tests with source (`user.service.test.ts`); the runner config in `refs/tooling.md` matches `src/**/*.test.ts`.
- Reset mutable state in `beforeEach`; never share it across tests.
- Name tests as observable behaviour: `'returns null when user not found'`.
- Read the implementation before writing mocks; mock what the code actually calls.
- Import error message constants from the source; never hardcode message strings in assertions.
- Type fixtures with the domain type, `satisfies`, or the source `as const` object (`Status.Active`); never cast with `as T`.

## Anti-Patterns

- Testing private methods or internal state
- Shared mock state without `beforeEach` reset (order-dependent tests)
- Un-awaited `expect(...).rejects` / `.resolves`
