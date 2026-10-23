---
last_reviewed: 2026-10-23
---

# TypeScript Security Patterns

Examples use Zod 4. Generic rules: `global/refs/security.md`, `global/refs/auth.md`. Express hardening (headers, body limits, CORS, duplicate parameters) lives in `standards/nodejs/refs/runtime-safety.md`.

## Input Validation (Zod)

Treat every boundary value (`req.body`, `req.query`, decoded tokens, `JSON.parse`, `process.env`) as `unknown`. Parse it, then use the parsed result. Never cast with `as`.

```typescript
import { z } from 'zod';

const CreateUserSchema = z.object({
  email: z.email(),
  name:  z.string().min(1).max(100),
  role:  z.enum(['user', 'admin']),
});

type CreateUserDto = z.infer<typeof CreateUserSchema>;

app.post('/users', (req, res) => {
  const result = CreateUserSchema.safeParse(req.body);
  if (!result.success) {
    return res.status(400).json({ errors: z.flattenError(result.error).fieldErrors });
  }
  return userService.create(result.data); // fully typed and validated
});
```

- Use the top-level format schemas (`z.email()`, `z.url()`, `z.uuid()`). The `z.string().email()` forms are deprecated in Zod 4.
- Use `z.flattenError(err)` for field errors. `err.flatten()` is deprecated.
- Query strings are not always strings: `?foo=bar` is a string, `?foo=bar&foo=baz` an array, `?foo[bar]=baz` an object. Schema-validate the type; never assume a string.

## Validated Environment

Parse the environment once at boot into a typed object. Never read `process.env.X!` at the point of use.

```typescript
// env.ts
import { z } from 'zod';

export const env = z.object({
  JWT_SECRET: z.string().min(32),
}).parse(process.env);
```

## JWT Payload Typing

`jwt.verify()` returns `string | JwtPayload`. Parse the result with a schema; do not cast it. Pin `algorithms`, `issuer`, and `audience` (rules: `global/refs/auth.md`).

```typescript
import jwt from 'jsonwebtoken';
import { z } from 'zod';

const JWTPayload = z.object({ userId: z.string(), role: z.enum(['user', 'admin']) });
type JWTPayload = z.infer<typeof JWTPayload>;

function verifyToken(token: string, secret: string): JWTPayload {
  try {
    const decoded = jwt.verify(token, secret, {
      algorithms: ['HS256'],
      issuer: 'your-app',
      audience: 'your-api',
    });
    return JWTPayload.parse(decoded);
  } catch {
    throw new Error('Invalid or expired token');
  }
}
```

## Role-Based Access Control

Type the role table with `as const satisfies`. The check must deny an unknown role at runtime: a role from a token or database is not guaranteed to match the type, and a plain index lookup throws on `'constructor'` or `'__proto__'`.

```typescript
type Role       = 'admin' | 'user' | 'guest';
type Permission = 'read'  | 'write' | 'delete';

const rolePermissions = {
  admin: ['read', 'write', 'delete'],
  user:  ['read', 'write'],
  guest: ['read'],
} as const satisfies Record<Role, readonly Permission[]>;

export function can(role: Role, permission: Permission): boolean {
  const allowed: readonly Permission[] | undefined =
    Object.hasOwn(rolePermissions, role) ? rolePermissions[role] : undefined;
  return allowed?.includes(permission) ?? false;
}
```

## Child Process Safety

`exec`/`execSync` and `spawn` with `shell: true` pass the string to `/bin/sh`, so a shell metacharacter in a dynamic value becomes command injection. Use `execFile`/`execFileSync`, or `spawn` with `shell: false` (the default), with a static command and an args array. Rule owner: `global/refs/security.md`.

## ReDoS Prevention

Lint regexes with `eslint-plugin-regexp` (`regexp/no-super-linear-backtracking`). Cap input length before matching.

## Anti-Patterns

- `process.env.X!` read at the point of use
- `jwt.verify()` without an explicit `algorithms` option, or a decoded payload cast with `as` instead of parsed
- Deprecated Zod 3 APIs in new code (`z.string().email()`, `err.flatten()`)
- Role or permission lookup by raw index without a deny-by-default fallback
