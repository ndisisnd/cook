---
last_reviewed: 2026-10-23
---

# Server Actions

Use this ref when implementing mutations, forms, optimistic updates, or post-mutation cache refresh in App Router. Auth, CSRF, and taint depth live in `refs/security.md`.

## Core Rules

- Put actions in `actions.ts` files that start with `'use server'`. Avoid inline actions that close over component scope.
- Every exported action is a public POST endpoint. Validate, authenticate, and authorize inside it (`refs/security.md`).
- Flow: validate -> auth -> mutate -> refresh cache -> return a minimal result or `redirect()`.
- Return only what the UI needs; return values are serialized to the client.

## Forms And State

- `<form action={fn}>` works before hydration (progressive enhancement).
- Actions used with `useActionState` take `(prevState, formData)`. Return validation errors as state instead of throwing.
- `useActionState`, `useFormStatus`, and `useOptimistic` rules: `react/SKILL.md` (React 19 APIs).
- Call an action outside a form inside `startTransition`.

```ts
// app/feedback/actions.ts
'use server';
import { updateTag } from 'next/cache';

export async function submitFeedback(_prev: State, formData: FormData): Promise<State> {
  const parsed = schema.safeParse(Object.fromEntries(formData));
  if (!parsed.success) return { errors: parsed.error.flatten().fieldErrors };
  // auth + authorization here: see refs/security.md
  await db.feedback.create({ data: parsed.data });
  updateTag('feedback');
  return { success: true };
}
```

## Cache Refresh After Mutation

| API | Use when |
|---|---|
| `updateTag(tag)` | The user must see their own change on the next read (Server Actions only) |
| `revalidateTag(tag, 'max')` | Brief staleness is acceptable; the second argument is required |
| `revalidatePath(path)` | The affected data is untagged |
| `refresh()` | Re-render the current client router view without touching tags (Server Actions only) |

All four import from `next/cache`.

## Redirects

`redirect()` throws a framework-handled exception. Call it after the `try/catch` block, never inside a `catch` that swallows it.

## Anti-Patterns

- Actions without `'use server'`.
- Actions that return full DB records.
- `revalidateTag(tag)` with one argument.
- `redirect()` inside a caught `try/catch`.
