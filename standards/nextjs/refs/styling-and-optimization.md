# Styling And Optimization

Use this ref when choosing styling libraries, creating `cn()`, configuring `next/font`, optimizing images/scripts/metadata, or diagnosing Core Web Vitals issues.

## Library Selection

| Library | Verdict | Reason |
|---|---|---|
| Tailwind / shadcn | Preferred | Zero-runtime, RSC-compatible, best fit for App Router |
| CSS Modules / SCSS Modules | Recommended | Scoped, zero-runtime, good for legacy projects |
| Ant Design | Supported | Use Client Component wrappers and registry for RSC compatibility |
| MUI / Chakra / runtime CSS-in-JS | Avoid by default | Forces `'use client'` widely and degrades RSC performance |

## Tailwind And `cn()`

Use `clsx` plus `tailwind-merge` for dynamic classes.

```ts
// lib/utils.ts
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

```tsx
// components/ui/button.tsx
export function Button({ className, variant, ...props }) {
  return (
    <button
      className={cn(
        'px-4 py-2 rounded font-medium transition-colors',
        variant === 'primary' && 'bg-blue-500 text-white',
        className,
      )}
      {...props}
    />
  );
}
```

## SCSS Modules

Use `.module.scss` to scope styles and prevent global namespace collisions.

- Centralize theme tokens in `styles/variables.scss` or `styles/mixins.scss`.
- Use global SCSS only for resets and root CSS variables in `app/globals.scss` or `pages/_app.tsx`.
- Avoid nesting more than three levels deep.
- Avoid component-level imports that produce global side effects.

```js
// next.config.js
const path = require('path');

module.exports = {
  sassOptions: {
    includePaths: [path.join(__dirname, 'styles')],
    prependData: `@import "variables.scss";`,
  },
};
```

## Ant Design

Ant Design and most runtime CSS-in-JS libraries need strict Client Component borders.

```tsx
// src/components/ui/AntdRegistry.tsx
'use client';

import React, { useState } from 'react';
import { createCache, extractStyle, StyleProvider } from '@ant-design/cssinjs';
import { useServerInsertedHTML } from 'next/navigation';

export default function AntdRegistry({ children }: { children: React.ReactNode }) {
  const [cache] = useState(() => createCache());
  useServerInsertedHTML(() => (
    <style id="antd" dangerouslySetInnerHTML={{ __html: extractStyle(cache, true) }} />
  ));
  return <StyleProvider cache={cache}>{children}</StyleProvider>;
}
```

Guidelines:

- Wrap AntD components in Client Components.
- Use `ConfigProvider` for global theme tokens.
- Ensure tree shaking is working.
- Use AntD `Form`, `Table`, and `Modal` patterns instead of rebuilding equivalent primitives inside an AntD app.
- Do not mix AntD with MUI or Bootstrap.

## Font Optimization

`next/font` is the single owner for font guidance in this domain. Use it instead of Google Fonts `<link>` tags to self-host fonts and reduce CLS.

```tsx
// app/layout.tsx
import { Inter } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
});

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={inter.className}>
      <body>{children}</body>
    </html>
  );
}
```

## Image Optimization

Use `next/image` to prevent CLS and enable automatic optimization. Always specify `width`/`height` or use `fill` with a stable parent size.

```tsx
import Image from 'next/image';

<Image
  src="/hero.jpg"
  alt="Hero"
  width={1200}
  height={600}
  priority
  sizes="(max-width: 768px) 100vw, 50vw"
  placeholder="blur"
  blurDataURL={blurHash}
/>;
```

## Metadata And Scripts

Use the metadata API, not `_document.tsx`, for SEO metadata.

```tsx
export const metadata: Metadata = { title: 'Dashboard', description: '...' };

export async function generateMetadata({ params }) {
  const product = await getProduct(params.id);
  return { title: product.name, openGraph: { images: [product.image] } };
}
```

Use `next/script` loading strategies deliberately:

- `beforeInteractive`: critical scripts such as polyfills.
- `afterInteractive`: analytics.
- `lazyOnload`: chat widgets and social embeds.

## Core Web Vitals And Bundle

- LCP target: under 2.5s.
- CLS target: under 0.1.
- INP target: under 200ms.
- Monitor with Chrome DevTools Performance, `next/speed-insights`, and React Profiler.
- Analyze bundles with `@next/bundle-analyzer` or built-in analyzer where available.
- Prune heavy libraries and prefer ESM tree-shakable dependencies.
- Use dynamic imports with Suspense for large non-initial components.
- Use PPR / Cache Components for static shell plus dynamic islands where supported.

## Anti-Patterns

- Runtime CSS-in-JS used broadly in RSC trees.
- `<img>` without dimensions.
- Google Fonts CDN `<link>` tags instead of `next/font`.
- Hardcoded conditional class strings instead of `cn()` for Tailwind variants.
- Metadata in `_document.tsx`.
- Third-party scripts manually inserted into `<head>` instead of `next/script`.
- Deep SCSS nesting or global side effects from component SCSS.
