# Server Actions

Use this ref when implementing mutations, forms, RPC-style calls, optimistic updates, or secure action validation in App Router.

## Core Rules

- Server Actions handle mutations without creating API endpoints.
- Add `'use server'` at the top of the file or inside the action function.
- Export async mutation functions from `actions.ts` or another server-only module.
- Define actions outside components to avoid hidden closure encryption overhead and serialization bugs.
- Validate all inputs, verify auth inside the action, mutate, then call `revalidatePath()` or `revalidateTag()`.

## Forms And Pending State

- Use `<form action={createPost}>` for progressive enhancement.
- Use `useFormStatus()` in a component rendered inside the form for submit-button pending state.
- Use `useActionState` for React 19 / Next.js 15 form state and validation errors.
- Use `useTransition` for non-form triggers so mutation UI does not block input.
- Use `useOptimistic` to show expected state before the server confirms.

## Secure Action Example

Always validate `FormData` with a schema library such as Zod and check authorization in the action. See `refs/security.md` for broader Server Action and CSRF rules.

```tsx
// actions.ts
'use server';
import { z } from 'zod';
import { revalidatePath } from 'next/cache';

const schema = z.object({
  email: z.string().email(),
  content: z.string().min(10),
});

export async function submitFeedback(prevState: any, formData: FormData) {
  const validated = schema.safeParse({
    email: formData.get('email'),
    content: formData.get('content'),
  });

  if (!validated.success) {
    return { errors: validated.error.flatten().fieldErrors };
  }

  const session = await auth();
  if (!session) throw new Error('Unauthorized');

  await db.feedback.create({ data: validated.data });
  revalidatePath('/feedback');
  return { success: true };
}
```

## `useActionState`

```tsx
// FeedbackForm.tsx
'use client';
import { useActionState } from 'react';
import { submitFeedback } from './actions';

export function FeedbackForm() {
  const [state, action, isPending] = useActionState(submitFeedback, null);

  return (
    <form action={action}>
      <input name="email" type="email" />
      {state?.errors?.email && <span>{state.errors.email}</span>}
      <button disabled={isPending}>Submit</button>
    </form>
  );
}
```

## Data Refresh

After successful mutation, refresh relevant cached views.

- `revalidatePath('/')` updates a route path.
- `revalidateTag('tag-name')` updates reads tagged by cache key.
- `updateTag('tag-name')` can provide immediate same-request invalidation in Cache Components.

## Redirects

Use `redirect()` for success navigation. It throws a framework-handled exception, so do not wrap it in a `try/catch` that swallows the redirect.

## Cross-Reference

Security owns validation, auth, CSRF, and taint depth; this file owns mutation workflow and action-specific React APIs.

## Anti-Patterns

- Unvalidated Server Action inputs.
- Auth checks skipped because middleware already ran.
- Actions defined inside components.
- `redirect()` inside a caught `try/catch`.
- File uploads without size and MIME limits.
