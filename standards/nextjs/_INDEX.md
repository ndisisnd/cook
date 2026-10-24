<!-- Hand-maintained routing index. Keep in sync with SKILL.md frontmatter. -->
# nextjs Skills Index

## File Match (auto-check against the file you are editing)

| Skill | File pattern | Keywords |
| ----- | ------------ | -------- |
| **nextjs** | `app/**/*.tsx`, `src/app/**/*.tsx`, `app/**/*.jsx`, `src/app/**/*.jsx`, `proxy.ts`, `next.config.ts` | App Router, Server Component, Client Component, use client, hydration, middleware |
| nextjs → app-router ref | `app/**/page.tsx`, `app/**/layout.tsx`, `app/**/loading.tsx`, `proxy.ts` | App Router, layout.tsx, root layout, nested layout, Route Group, parallel routes, intercepting routes, async params, proxy.ts, forbidden(), unauthorized(), after() |
| nextjs → pages-router ref | `pages/**/*.tsx`, `pages/**/*.ts` | Pages Router, getServerSideProps, getStaticProps, _app, _document |
| nextjs → server-components ref | — | Server Component, Client Component, RSC, serialization, server-only |
| nextjs → data-fetching ref | `**/service.ts`, `**/lib/data.ts`, `**/services/*.ts`, `**/dal/**` | revalidate, no-store, force-cache, DAL, Data Access Layer, DTO |
| nextjs → rendering-and-caching ref | — | generateStaticParams, PPR, streaming, revalidateTag, Data Cache, Router Cache |
| nextjs → server-actions ref | `app/**/actions.ts`, `src/app/**/actions.ts` | use server, Server Action, revalidatePath, useFormStatus, useActionState |
| nextjs → security ref | `proxy.ts`, `middleware.ts`, `**/auth.ts`, `**/login/page.tsx` | auth, cookie, jwt, session, jose, CSP, CSRF, middleware |
| nextjs → state-management ref | — | URL state, zustand, redux |
| nextjs → styling-and-optimization ref | `**/*.css`, `tailwind.config.ts`, `**/components/ui/*.tsx` | tailwind, css modules, styled-components, clsx, next/image, next/font, Core Web Vitals |
| nextjs → testing ref | `**/*.test.{ts,tsx}`, `cypress/**`, `tests/**`, `jest.config.*`, `content:@testing-library`, `content:@playwright/test`, `content:msw` | vitest, playwright, msw, testing-library |
| nextjs → architecture ref | — | FSD, Feature Sliced Design, feature slices, bundling |
| nextjs → i18n ref | `messages/*.json` | i18n, locale, translation, next-intl, react-intl, hreflang |
| nextjs → tooling ref | `next.config.js`, `next.config.ts`, `package.json` | turbopack, standalone, codemod, next upgrade |

> Load `<SKILLS>/nextjs/SKILL.md` for any matched Next.js file or keyword. It covers the always-on App Router defaults: cache-model decision, RSC boundaries, data access, App Router conventions, security, rendering, and Server Actions.
>
> Load `<SKILLS>/nextjs/refs/pages-router.md` instead of applying App Router rules when the project uses `pages/` only.
>
> Load a `refs/*.md` file only when its keyword (or its narrow file pattern) matches the current task. Rows marked `—` route by keyword only.
