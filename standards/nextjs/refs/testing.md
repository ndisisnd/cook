---
last_reviewed: 2026-10-23
---

# Testing

Use this ref for Next.js-specific test setup. Generic React rules (RTL queries, `userEvent`, MSW lifecycle, AAA) live in `react/refs/testing.md`.

## Runner

- Unit/component: Vitest (new projects) or Jest via `next/jest` (existing stacks). Vitest needs `@vitejs/plugin-react`, `jsdom`, `@testing-library/react`, `@testing-library/dom`, `vite-tsconfig-paths`, and `environment: 'jsdom'`. Vitest 5 needs Node 22+; use Node 24 LTS.
- Jest: wrap config with `nextJest({ dir: './' })` from `next/jest.js`. It handles SWC transform, CSS/image/`next/font` mocks, and `.env` loading. Do not hand-roll `babel-jest`.
- E2E: Playwright for anything that crosses the server/client boundary.

## Next-Specific Rules

- Vitest and Jest cannot render `async` Server Components. Unit-test synchronous Server/Client Components only. Test `async` ones with Playwright, or extract their logic into plain functions and test those.
- Test Server Actions as plain async functions. Mock `next/cache` (`revalidatePath`, `updateTag`, `revalidateTag`) and `next/navigation` (`redirect`, `notFound`) at the module boundary. `redirect` and `notFound` throw; assert the throw.
- Mock `next/navigation` hooks (`useRouter`, `usePathname`, `useSearchParams`) with `vi.mock`. Mock `next/headers` (`cookies`, `headers`) as async functions; they return promises in 16.
- Run Playwright against a production build (`next build && next start`) or a `webServer` entry; production behavior differs from dev.
- With Cache Components, assert instant navigation shells with `instant()` from `@next/playwright`.
- Mock network with MSW 3 (ESM-only, Node 22+; option `onUnhandledFrame`, not `onUnhandledRequest`). Server Component fetches run in the Node process, so only Playwright with a mock server or MSW in the Next server covers them.

## Anti-Patterns

- Unit-testing `async` Server Components with RTL.
- Real network or real cache in tests.
- Heavy E2E for unit logic.
