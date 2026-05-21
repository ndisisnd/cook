<!-- AUTO-GENERATED from SKILL.md frontmatter - do not edit manually -->
# nextjs Skills Index

## File Match (auto-check against the file you are editing)

| Skill | File pattern | Keywords |
| ----- | ------------ | -------- |
| **nextjs** | `app/**/*.tsx`, `src/app/**/*.tsx`, `app/**/*.jsx`, `src/app/**/*.jsx` | Server Component, Client Component, use client, hydration, App Router |
| nextjs -> app-router ref | `app/**/page.tsx`, `app/**/layout.tsx`, `app/**/loading.tsx`, `app/**/error.tsx`, `app/**/route.ts` | App Router, Layout, Route Group, parallel routes, intercepting routes, async params |
| nextjs -> pages-router ref | `pages/**/*.tsx`, `pages/**/*.ts` | Pages Router, getServerSideProps, getStaticProps, _app, _document, useRouter |
| nextjs -> server-components ref | `app/**/*.tsx`, `src/app/**/*.tsx`, `app/**/*.jsx`, `src/app/**/*.jsx` | use client, Server Component, Client Component, RSC, serialization, hydration |
| nextjs -> data-fetching ref | `**/service.ts`, `**/lib/data.ts`, `**/services/*.ts`, `**/dal/**` | fetch, revalidate, no-store, force-cache, DAL, Data Access Layer, DTO, server-only |
| nextjs -> rendering-and-caching ref | `**/page.tsx`, `**/layout.tsx`, `**/actions.ts` | generateStaticParams, dynamic, dynamicParams, PPR, streaming, cache, revalidateTag, Data Cache, Router Cache |
| nextjs -> server-actions ref | `app/**/actions.ts`, `src/app/**/actions.ts`, `app/**/*.tsx`, `src/app/**/*.tsx` | use server, Server Action, revalidatePath, useFormStatus, useActionState |
| nextjs -> security ref | `middleware.ts`, `app/**/actions.ts`, `**/auth.ts`, `**/login/page.tsx` | auth, cookie, jwt, session, localstorage, action, boundary, sanitize, jose, CSP, CSRF |
| nextjs -> state-management ref | `**/hooks/*.ts`, `**/store.ts`, `**/components/*.tsx` | useState, useContext, zustand, redux, URL state, TanStack Query, SWR |
| nextjs -> styling-and-optimization ref | `**/*.css`, `tailwind.config.ts`, `**/components/ui/*.tsx`, `**/layout.tsx`, `**/page.tsx` | tailwind, css modules, styled-components, clsx, cn, metadata, next/image, next/font, Core Web Vitals |
| nextjs -> testing ref | `**/*.test.{ts,tsx}`, `**/*.spec.{ts,tsx}`, `cypress/**`, `tests/**`, `jest.config.*`, `vitest.config.*`, `playwright.config.*` | vitest, playwright, msw, testing-library, userEvent |
| nextjs -> architecture ref | `src/features/**`, `src/entities/**`, `src/widgets/**` | FSD, Feature Sliced Design, slices, segments, RSC boundaries, runtime, bundling |
| nextjs -> i18n ref | `middleware.ts`, `app/[lang]/**`, `pages/[locale]/**`, `messages/*.json`, `next.config.js` | i18n, locale, translation, next-intl, react-intl, next-translate, hreflang |
| nextjs -> tooling ref | `next.config.js`, `package.json`, `Dockerfile`, `.github/workflows/**` | Dockerfile, turbopack, output, standalone, lint, telemetry, codemod, next upgrade |

## Loading Instructions

> Load `<SKILLS>/nextjs/SKILL.md` for any matched Next.js file or keyword. It covers the always-on App Router defaults: RSC boundaries, data fetching, App Router conventions, security/auth, rendering/cache strategy, and Server Actions.
>
> Load `<SKILLS>/nextjs/refs/pages-router.md` instead of applying App Router rules when the project uses `pages/`.
>
> Load the listed `refs/*.md` files only when their file pattern or keyword matches the current task.

## Archived

The 18 sub-skill folders that previously lived under `standards/nextjs/` have been moved to `archive/nextjs/` at the repo root. They are preserved verbatim - each original `SKILL.md`, `refs/`, and `evals/` directory is intact under its original `nextjs-<name>/` path.

Their content has been merged into `SKILL.md` and the `refs/` files above. The table below traces each source to its destination so a reviewer can verify no rules were lost.

| Source (under `archive/nextjs/`) | Destination |
|---|---|
| `nextjs-server-components/SKILL.md` | `SKILL.md` P0 Server & Client Components |
| `nextjs-server-components/refs/example.md` | `refs/server-components.md` |
| `nextjs-server-components/refs/composition-security.md` | `refs/server-components.md` |
| `nextjs-architecture/refs/RSC_BOUNDARIES.md` | `refs/server-components.md` - single RSC boundary home |
| `nextjs-data-fetching/SKILL.md` | `SKILL.md` P0 Data Fetching & Access + `refs/data-fetching.md` |
| `nextjs-data-fetching/refs/usage-examples.md` | `refs/data-fetching.md` |
| `nextjs-data-access-layer/SKILL.md` | `SKILL.md` P0 Data Fetching & Access + `refs/data-fetching.md` |
| `nextjs-data-access-layer/refs/implementation.md` | `refs/data-fetching.md` DAL section |
| `nextjs-data-access-layer/refs/patterns.md` | `refs/data-fetching.md` DAL patterns - previously orphaned, carried |
| `nextjs-app-router/SKILL.md` | `SKILL.md` P0 App Router Conventions + `refs/app-router.md` |
| `nextjs-app-router/refs/implementation.md` | `refs/app-router.md` |
| `nextjs-app-router/refs/SELF_HOSTING.md` | `refs/app-router.md` Self-Hosting section |
| `nextjs-rendering/SKILL.md` | `SKILL.md` P1 Rendering & Caching + `refs/rendering-and-caching.md` |
| `nextjs-rendering/refs/strategy-matrix.md` | `refs/rendering-and-caching.md` Strategy Matrix |
| `nextjs-rendering/refs/implementation.md` | `refs/rendering-and-caching.md` Strategy Guide |
| `nextjs-rendering/refs/implementation-details.md` | `refs/rendering-and-caching.md` Strategy Guide |
| `nextjs-rendering/refs/scaling-patterns.md` | `refs/rendering-and-caching.md` Static Shell / Waterfalls / ISR + Streaming |
| `nextjs-rendering/refs/SUSPENSE_BAILOUT.md` | `refs/rendering-and-caching.md` Suspense Bailout Rules - previously orphaned, carried |
| `nextjs-caching/SKILL.md` | `SKILL.md` P1 Rendering & Caching + `refs/rendering-and-caching.md` |
| `nextjs-caching/refs/implementation.md` | `refs/rendering-and-caching.md` Cache Layers / Invalidation |
| `nextjs-caching/refs/CACHE_COMPONENTS.md` | `refs/rendering-and-caching.md` Cache Components / PPR |
| `nextjs-authentication/SKILL.md` | `SKILL.md` P0 Security & Auth + `refs/security.md` |
| `nextjs-authentication/refs/implementation.md` | `refs/security.md` Token Storage / Middleware |
| `nextjs-authentication/refs/auth-implementation.md` | `refs/security.md` Token Storage / Session Reads / Middleware |
| `nextjs-security/SKILL.md` | `SKILL.md` P0 Security & Auth + `refs/security.md` |
| `nextjs-security/refs/implementation.md` | `refs/security.md` Server Action Validation / Data Boundary |
| `nextjs-pages-router/SKILL.md` | `refs/pages-router.md` |
| `nextjs-pages-router/refs/implementation.md` | `refs/pages-router.md` |
| `nextjs-pages-router/refs/server-side-props.md` | `refs/pages-router.md` |
| `nextjs-pages-router/refs/feature-sliced-design-pages.md` | `refs/pages-router.md` Feature-Sliced Design section - previously orphaned, carried |
| `nextjs-server-actions/SKILL.md` | `SKILL.md` P1 Server Actions + `refs/server-actions.md` |
| `nextjs-server-actions/refs/secure-actions.md` | `refs/server-actions.md` + cross-reference to `refs/security.md` |
| `nextjs-optimization/SKILL.md` | `refs/styling-and-optimization.md` Optimization sections |
| `nextjs-optimization/refs/example.md` | `refs/styling-and-optimization.md` Image / Font / Metadata examples |
| `nextjs-styling/SKILL.md` | `refs/styling-and-optimization.md` Styling sections |
| `nextjs-styling/refs/implementation.md` | `refs/styling-and-optimization.md` Tailwind `cn()` section |
| `nextjs-styling/refs/scss.md` | `refs/styling-and-optimization.md` SCSS Modules section |
| `nextjs-styling/refs/ant-design.md` | `refs/styling-and-optimization.md` Ant Design section |
| `nextjs-styling/refs/tailwind.md` | `refs/styling-and-optimization.md` Tailwind / Font section |
| `nextjs-testing/SKILL.md` | `refs/testing.md` |
| `nextjs-testing/refs/implementation.md` | `refs/testing.md` |
| `nextjs-architecture/SKILL.md` | `refs/architecture.md` |
| `nextjs-architecture/refs/implementation.md` | `refs/architecture.md` |
| `nextjs-architecture/refs/fsd-structure.md` | `refs/architecture.md` FSD Structure |
| `nextjs-architecture/refs/BUNDLING.md` | `refs/architecture.md` Bundling section |
| `nextjs-architecture/refs/RUNTIME_SELECTION.md` | `refs/architecture.md` Runtime Selection section |
| `nextjs-architecture/refs/DEBUG_TRICKS.md` | `refs/architecture.md` Debugging section |
| `nextjs-i18n/SKILL.md` | `refs/i18n.md` |
| `nextjs-i18n/refs/implementation.md` | `refs/i18n.md` Routing / Middleware |
| `nextjs-i18n/refs/next-intl.md` | `refs/i18n.md` next-intl section |
| `nextjs-i18n/refs/react-intl.md` | `refs/i18n.md` react-intl section |
| `nextjs-state-management/SKILL.md` | `refs/state-management.md` |
| `nextjs-state-management/refs/implementation.md` | `refs/state-management.md` URL / Server / Zustand examples |
| `nextjs-state-management/refs/redux.md` | `refs/state-management.md` Redux sections |
| `nextjs-state-management/refs/zustand.md` | `refs/state-management.md` Zustand sections |
| `nextjs-state-management/refs/url-state.md` | `refs/state-management.md` URL State sections |
| `nextjs-tooling/SKILL.md` | `refs/tooling.md` |
| `nextjs-tooling/refs/implementation.md` | `refs/tooling.md` Build / Docker / Env sections |
| `nextjs-upgrade/SKILL.md` | `refs/tooling.md` Upgrade Protocol |
| `nextjs-upgrade/refs/example.md` | `refs/tooling.md` Upgrade dependency commands |
| All 18 `nextjs-*/evals/evals.json` | No content carried - eval artifacts preserved verbatim in `archive/nextjs/` |
