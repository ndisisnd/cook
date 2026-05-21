# Pages Router

Use this ref for legacy projects that use the `pages/` directory. Do not apply App Router-only features to Pages Router projects.

## Core Rules

- Use `pages/` filesystem routing with `_app.tsx` for global state/layouts and `_document.tsx` for custom HTML attributes.
- Use `[id].tsx` and `[...slug].tsx` for dynamic and catch-all routes.
- Use `getServerSideProps` for request-time SSR.
- Use `getStaticProps` with `getStaticPaths` for build-time static generation.
- Import service or database logic directly from server-side hooks; never fetch your own `/api` routes from `getServerSideProps` or `getStaticProps`.
- Use `InferGetServerSidePropsType<typeof getServerSideProps>` or equivalent typed props.
- Use `useRouter()` from `next/router` for navigation and query params.
- Implement API Routes under `pages/api/` for webhooks and server-only endpoints.
- Standardize API Route responses with appropriate HTTP status codes and consistent JSON error shapes.
- Scope global CSS to `_app.tsx`; otherwise use CSS Modules, SCSS modules, or Tailwind.

## SSR Example

```tsx
// pages/posts/[id].tsx
import type { GetServerSideProps, InferGetServerSidePropsType } from 'next';

export const getServerSideProps: GetServerSideProps = async ({ params }) => {
  const post = await postService.findById(params!.id as string);
  if (!post) return { notFound: true };
  return { props: { post } };
};

export default function PostPage({ post }: InferGetServerSidePropsType<typeof getServerSideProps>) {
  return <article>{post.title}</article>;
}
```

```tsx
export const getServerSideProps: GetServerSideProps = async (context) => {
  const data = await getPostData(context.params?.id);
  return { props: { data } };
};
```

## Feature-Sliced Design For Pages Router

Large Pages Router monoliths should keep page files thin and move UI mapping and business logic into feature slices.

```text
pages/
`-- cart.tsx                    <-- thin route

src/
|-- features/
|   `-- cart/
|       |-- components/         <-- UI only (CartItem, OrderSummary)
|       |-- services/           <-- pure logic (API calls)
|       `-- CartFeature.tsx     <-- assembles UI and handles main state
`-- shared/
    |-- ui/                     <-- global UI (Button, Modal)
    `-- utils/                  <-- globally shared utilities
```

Execution rules:

1. `pages/cart.tsx` should return `<CartFeature />` and export `getServerSideProps` only when SEO or auth requires SSR.
2. `<CartFeature />` ties hooks and presentation components together.
3. Extract complex Redux subscriptions or `useEffect` chains into custom hooks such as `src/features/cart/hooks/useCartData.ts`.
4. Avoid direct Redux imports inside low-level presentation components. Pass data via props or keep Redux hooks localized to the feature wrapper/custom hooks.

## Migration Caution

Next.js 15+ compatibility work should ensure all `getServerSideProps` and `getStaticProps` returns match expected `PageProps`. Do not convert Pages Router page components to `async` default exports.

## Anti-Patterns

- Fetching own `/api` routes from SSR/SSG hooks.
- Global CSS outside `_app.tsx`.
- App Router features in Pages Router projects.
- Async default page components in Pages Router.
- Giant page files that mix route, UI, state, and business logic.
