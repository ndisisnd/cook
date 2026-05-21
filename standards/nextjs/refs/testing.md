# Testing

Use this ref when writing or reviewing Next.js component, unit, integration, API, or E2E tests.

## Test Runner Decision

- Existing Pages Router or legacy stacks: use Jest (`jest@29`, `babel-jest`, `jest-environment-jsdom`) unless the project has already migrated.
- New App Router projects: use Vitest for speed and native ESM support.
- Use Playwright for critical end-to-end flows such as login, checkout, and signup.

## Workflow

1. Write unit/component tests with Jest or Vitest plus React Testing Library.
2. Follow Arrange-Act-Assert.
3. Mock internal and external network boundaries with MSW.
4. Use async `userEvent` for clicks, typing, and submissions.
5. Add Playwright tests for critical user flows.
6. Generate JSON coverage reports in CI and aim for 80%+ on core libraries.

## Component Tests

```tsx
// tests/components/Button.test.tsx
import { render, screen } from '@testing-library/react';
import { Button } from '@/components/Button';

test('renders correctly', () => {
  render(<Button>Click me</Button>);
  expect(screen.getByText('Click me')).toBeDefined();
});
```

```tsx
// tests/unit/post-card.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { PostCard } from '@/components/post-card';

test('calls onLike when heart button is clicked', async () => {
  const onLike = vi.fn();
  render(<PostCard title="Hello" onLike={onLike} />);
  await userEvent.click(screen.getByRole('button', { name: /like/i }));
  expect(onLike).toHaveBeenCalledOnce();
});
```

## Playwright

```ts
// tests/e2e/home.spec.ts
import { test, expect } from '@playwright/test';

test('homepage has title', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/My App/);
});
```

## MSW

```ts
// tests/mocks/handlers.ts
export const handlers = [
  http.get('/api/user', () => {
    return HttpResponse.json({ id: '1', name: 'Hoang' });
  }),
];
```

## Selectors And Environment

- Prefer `getByRole` and `findByRole` to test accessible behavior.
- Use `data-testid` only when role/name selection is not practical.
- Configure Jest with `jest-environment-jsdom`.
- Configure Vitest with `jsdom` or `happy-dom`.
- Reset MSW handlers and mocks after each test.

## Suggested Layout

```text
tests/
|-- unit/               # Vitest/Jest + RTL
|-- e2e/                # Playwright
`-- mocks/              # MSW handlers
```

## Anti-Patterns

- Real network usage in tests.
- Testing implementation details instead of user behavior.
- Heavy E2E tests for unit logic.
- Global mock/server state leaking between tests.
