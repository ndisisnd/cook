# React Testing

## Principles

- Test behaviour, not implementation. Assert what the user sees, not internal state or prop values.
- Prefer `getByRole` / `findByRole` — they exercise accessible semantics. Use `data-testid` only as a last resort.
- Use `userEvent` (async) rather than `fireEvent` — it more closely simulates real browser events (focus, pointer, keyboard sequencing).
- Follow Arrange–Act–Assert (AAA) structure in every test.
- Mock all network calls with MSW. Never call real APIs in unit or integration tests.
- Cover 100% of P0 user flows. Snapshot testing is acceptable only for small, stable presentational components.
- Do not use shallow rendering. Render the component tree the user interacts with, including real providers when practical.
- Mock expensive animation, charting, map, or asset libraries to keep tests fast and deterministic; prefer real router/context wrappers over mocking app infrastructure.
- Use `queryBy*` only for absence assertions. Do not use `getBy*` for elements that should not exist.
- Prefer RTL async utilities over manual `act()`. Reach for manual `act()` only when integrating with code RTL cannot observe.

## Basic Component Test

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginForm } from './LoginForm';

test('submits credentials and shows welcome message', async () => {
  const user = userEvent.setup();
  render(<LoginForm />);

  await user.type(screen.getByLabelText(/email/i), 'test@example.com');
  await user.type(screen.getByLabelText(/password/i), 'secret');
  await user.click(screen.getByRole('button', { name: /log in/i }));

  expect(await screen.findByText(/welcome/i)).toBeInTheDocument();
});

test('shows validation error when email is empty', async () => {
  const user = userEvent.setup();
  render(<LoginForm />);

  await user.click(screen.getByRole('button', { name: /log in/i }));

  expect(await screen.findByText(/email is required/i)).toBeInTheDocument();
});
```

## Mocking API Calls with MSW

```tsx
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { render, screen } from '@testing-library/react';
import { UserProfile } from './UserProfile';

const server = setupServer(
  http.get('/api/users/:id', ({ params }) =>
    HttpResponse.json({ id: params.id, name: 'Jane Doe' })
  )
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test('displays fetched user name', async () => {
  render(<UserProfile userId="1" />);
  expect(await screen.findByText('Jane Doe')).toBeInTheDocument();
});

test('shows error state on 500', async () => {
  server.use(http.get('/api/users/:id', () => new HttpResponse(null, { status: 500 })));
  render(<UserProfile userId="1" />);
  expect(await screen.findByText(/something went wrong/i)).toBeInTheDocument();
});
```

## Testing Context Providers

Wrap the component under test in the real provider (not a mock) whenever possible:

```tsx
import { AuthProvider } from './AuthContext';

test('shows username when authenticated', () => {
  render(
    <AuthProvider initialUser={{ id: '1', name: 'Alice' }}>
      <Navbar />
    </AuthProvider>
  );
  expect(screen.getByText('Alice')).toBeInTheDocument();
});
```

Create a reusable `renderWithProviders` wrapper for tests that always need the same set of providers:

```tsx
function renderWithProviders(ui: ReactElement, options?: RenderOptions) {
  return render(ui, { wrapper: ({ children }) => <AppProviders>{children}</AppProviders>, ...options });
}
```

## Testing with React Router

```tsx
import { MemoryRouter, Routes, Route } from 'react-router-dom';

test('renders dashboard at /dashboard', () => {
  render(
    <MemoryRouter initialEntries={['/dashboard']}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </MemoryRouter>
  );
  expect(screen.getByRole('heading', { name: /dashboard/i })).toBeInTheDocument();
});
```

## Mocking Heavy Dependencies

Mock slow or browser-specific libraries at the module boundary, but keep the component behaviour visible to the test:

```tsx
vi.mock('framer-motion', () => ({
  motion: { div: (props: React.HTMLAttributes<HTMLDivElement>) => <div {...props} /> },
}));
```

## Async Queries

Use `findBy*` (returns a promise) for elements that appear after an async operation. Use `waitFor` for assertions on non-element state:

```tsx
// findBy* — element appears after fetch
const heading = await screen.findByRole('heading', { name: /results/i });

// waitFor — assertion that is not about a DOM element
await waitFor(() => expect(mockOnSave).toHaveBeenCalledTimes(1));
```

Keep side effects out of `waitFor`; it may run the callback multiple times. Trigger events before `waitFor`, then assert inside it.

```tsx
expect(screen.queryByRole('alert')).not.toBeInTheDocument();
```

When using fake timers, configure `userEvent` so delayed interactions advance timers correctly:

```tsx
vi.useFakeTimers();
const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
```

## Accessibility Check

```tsx
import { axe, toHaveNoViolations } from 'jest-axe';
expect.extend(toHaveNoViolations);

test('has no accessibility violations', async () => {
  const { container } = render(<Form />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```
