---
last_reviewed: 2026-10-23
---
# React Testing

Verified 2026-10 (npm): `@testing-library/react` 16.x (needs `@testing-library/dom` 10 as a peer), `@testing-library/user-event` 14.x, `msw` 3.x (ESM-only, Node 22+), Vitest 5.x (Node 22+, Vite 6.4+).

## Principles

- Test behaviour, not implementation. Assert what the user sees, not state or props.
- Query priority: `getByRole` (with `name`) > `getByLabelText` > `getByPlaceholderText` > `getByText` > `getByDisplayValue` > `getByAltText`/`getByTitle` > `getByTestId` (last resort).
- Use `userEvent.setup()` before `render`, then `await user.click/type`. Do not use `fireEvent` or the sync v13 API.
- Use `findBy*` for elements that appear later; `waitFor` only for non-DOM assertions. Keep side effects out of `waitFor`; it can run the callback many times.
- Use `queryBy*` only to assert absence. Use `getBy*` for anything that must exist.
- Do not wrap RTL calls in manual `act()`. Use it only for code RTL cannot observe.
- No shallow rendering. Render the real tree with real providers and a real router (`MemoryRouter`).
- Use AAA structure. Cover 100% of P0 user flows. Snapshots only for small, stable presentational components.
- Mock animation, chart, map, and asset libraries at the module boundary (`vi.mock`); do not mock app infrastructure.
- Put repeated providers in one `renderWithProviders(ui)` helper that passes a `wrapper` to `render`. Create a fresh `QueryClient` per test with `retry: false`.

## Network: MSW

- Mock every network call with MSW. Never hit real APIs.
- Handlers use `http.get(path, resolver)` and `HttpResponse.json(...)`. Do not use the removed `rest` API.
- Lifecycle: `server.listen()` in `beforeAll`, `server.resetHandlers()` in `afterEach`, `server.close()` in `afterAll`. Override per test with `server.use(...)`.
- MSW 3: the option is `onUnhandledFrame` (was `onUnhandledRequest`). It no longer patches `setTimeout`, so advance fake timers yourself. `msw/native` is gone; use `@msw/react-native`. Cookies are no longer managed in Node; use the `cookies` resolver argument.
- Test error states by returning `new HttpResponse(null, { status: 500 })`.

## Fake Timers

Pair them with `userEvent`: `userEvent.setup({ advanceTimers: vi.advanceTimersByTime })`. Restore with `vi.useRealTimers()` in `afterEach`.

## Accessibility

Run an axe check on key views (`vitest-axe` or `jest-axe`). Axe cannot replace keyboard and screen-reader checks.
