# App Router

Use this ref when creating App Router routes, layouts, loading/error states, dynamic segments, route groups, parallel/intercepting routes, Route Handlers, or self-hosting-sensitive App Router features.

## File Conventions

| File | Role |
|---|---|
| `page.tsx` | UI for a route segment |
| `layout.tsx` | Shared UI wrapping children; persists across navigation |
| `loading.tsx` | Route-level Suspense fallback |
| `error.tsx` | Error boundary; must be a Client Component |
| `not-found.tsx` | Not-found UI for segment |
| `route.ts` | Server-side endpoint |

Only the root `app/layout.tsx` should include `<html>` and `<body>` tags.

## Add A New Route

1. Create `app/dashboard/page.tsx` as a Server Component by default.
2. Add `app/dashboard/layout.tsx` only when the segment needs shared UI.
3. Add `app/dashboard/loading.tsx` for route-level Suspense.
4. Add `app/dashboard/error.tsx` with `'use client'` and a `reset` prop for local recovery.
5. In Next.js 15+, `await params`, `searchParams`, `cookies()`, and `headers()`.

```tsx
// app/(auth)/login/page.tsx - URL is /login, not /auth/login
export default function LoginPage() {
  return <LoginForm />;
}

// app/dashboard/error.tsx
'use client';

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  return <button onClick={() => reset()}>Retry</button>;
}
```

## Routing Structure

- Route Groups: use `(auth)` to organize without affecting the URL path.
- Private Folders: use `_lib` to colocate files excluded from routing.
- Dynamic Routes: use `[slug]` or `[...slug]`; use `generateStaticParams` for pre-rendered paths.
- Parallel Routes: use `@modal` and pass the slot to the parent layout; provide `default.tsx` fallback.
- Intercepting Routes: use `(.)route` or `(..)route` for advanced flows such as modals inside dashboards.
- Colocation: keep route-specific components, styles, tests, and private helpers inside the route folder when they are not reused elsewhere.

## Data And Functions

- Default to Server Components; use `'use client'` only at interactive leaves.
- Await async APIs in Next.js 15+: `params`, `searchParams`, `cookies()`, and `headers()`.
- Use `middleware.ts` for edge-side authentication and redirects.
- Secure every `route.ts` handler with appropriate auth, validation, and rate limiting.
- Keep pages thin; call widgets, features, DAL functions, or Server Actions rather than embedding business logic.

## Self-Hosting

Use these rules when hosting Next.js outside Vercel.

### Standalone Output

Mandatory for production containers.

```js
// next.config.js
module.exports = { output: 'standalone' };
```

Manually copy `public/` and `.next/static/` into the standalone directory's corresponding folders so assets are served correctly.

### Distributed ISR Cache

Filesystem cache breaks in multi-instance deployments. Use a shared Cache Handler.

```js
// next.config.js
module.exports = {
  cacheHandler: require.resolve('./cache-handler.js'),
  cacheMaxMemorySize: 0,
};
```

Storage options:

- Redis: recommended for most apps.
- S3: useful for high-volume static assets.

### Environment Variables

- `NEXT_PUBLIC_*` values are baked into the JavaScript bundle at build time.
- Server-only values are loaded at runtime from the environment.

### Image Optimization

- Built-in image optimization works in Docker but requires `sharp`.
- External loaders such as Cloudinary, Imgix, or Akamai are recommended at scale.

```js
// next.config.js
module.exports = { images: { loader: 'custom' } };
```

## Cross-References

- RSC serialization rules live in `refs/server-components.md`.
- Rendering, ISR, and PPR strategy lives in `refs/rendering-and-caching.md`.
- Docker and CI details live in `refs/tooling.md`.

## Anti-Patterns

- Unawaited async route APIs in Next.js 15+.
- `'use client'` at the tree root instead of leaves.
- `<html>` or `<body>` in nested layouts.
- Missing `error.tsx` for segments that need local recovery.
- Route Handlers without auth, validation, and rate limiting.
