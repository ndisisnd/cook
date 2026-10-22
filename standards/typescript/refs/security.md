---
last_reviewed: 2026-10-18
---

# TypeScript Security Patterns

Examples use Zod 4. Express middleware hardening (security headers, body limits, CORS, duplicate parameters) lives in `standards/nodejs/refs/runtime-safety.md`. Secret policy lives in `global/refs/security.md`.

## Input Validation (Zod)

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

**Query string type coercion risk**: identical parameter names parse differently depending on repetition and bracket syntax (`?foo=bar` → string, `?foo=bar&foo=baz` → array, `?foo[bar]=baz` → object). Validate and coerce types explicitly — never assume a query param is a string.

## Validated Environment

Parse secrets once at boot. Never read `process.env.X!` at the point of use.

```typescript
// env.ts
import { z } from 'zod';

export const env = z.object({
  JWT_SECRET: z.string().min(32),
}).parse(process.env);
```

## JWT Authentication

```typescript
import jwt from 'jsonwebtoken';
import { z } from 'zod';
import { env } from './env.ts';

const JWTPayload = z.object({ userId: z.string(), role: z.enum(['user', 'admin']) });
type JWTPayload = z.infer<typeof JWTPayload>;

export class AuthService {
  readonly #secret: string;

  constructor(secret: string = env.JWT_SECRET) {
    this.#secret = secret;
  }

  generateToken(payload: JWTPayload): string {
    return jwt.sign(payload, this.#secret, {
      expiresIn: '1h',
      algorithm: 'HS256',
      issuer: 'your-app',
      audience: 'your-api',
    });
  }

  verifyToken(token: string): JWTPayload {
    try {
      // Pin algorithm, issuer, and audience — defense-in-depth against algorithm confusion
      const decoded = jwt.verify(token, this.#secret, {
        algorithms: ['HS256'],
        issuer: 'your-app',
        audience: 'your-api',
      });
      return JWTPayload.parse(decoded);
    } catch {
      throw new Error('Invalid or expired token');
    }
  }
}
```

> **RS256 (multi-service):** Sign with a PEM RSA private key and verify with the matching public key. `HS256` with a shared secret fits a single service; `RS256` fits when verifiers must not be able to sign.

## Secure Cookie Options

```typescript
const cookieOpts = {
  httpOnly: true,
  secure: process.env.NODE_ENV === 'production',
  sameSite: 'strict',
  maxAge: 60 * 60 * 1000, // 1 hour
} as const;
// Verify your environment's NODE_ENV convention ('prod' vs 'production') before deploying.
```

## Role-Based Access Control

```typescript
type Role       = 'admin' | 'user' | 'guest';
type Permission = 'read'  | 'write' | 'delete';

const rolePermissions = {
  admin: ['read', 'write', 'delete'],
  user:  ['read', 'write'],
  guest: ['read'],
} as const satisfies Record<Role, readonly Permission[]>;

export function can(role: Role, permission: Permission): boolean {
  return (rolePermissions[role] as readonly Permission[]).includes(permission);
}
```

Call `can()` from the framework's auth middleware or handler. Deny by default when the role is missing or unknown.

## Child Process Safety

`child_process.exec()` forwards the command string to `/bin/sh` — any shell metacharacter in a dynamic value becomes a command injection vector. Use `execFile` with a static command and a separate args array; no shell is involved:

```typescript
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';

const execFileAsync = promisify(execFile);

// Safe — shell is never invoked
const { stdout } = await execFileAsync('git', ['log', '--oneline', commitHash]);
```

This applies to both `exec`/`execSync` (shell) and `spawn` with `shell: true`. Use `execFile`/`execFileSync` or `spawn` with `shell: false` (the default).

## ReDoS Prevention

Nested quantifiers on overlapping character classes cause exponential backtracking. A single crafted input string can hang the event loop:

```typescript
// Dangerous — catastrophic backtracking
const bad = /^(([a-z])+.)+[A-Z]([a-z])+$/;

// Safe — linear, anchored, no overlapping repetition
const email = /^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/;
```

Lint regexes with `eslint-plugin-regexp` (`regexp/no-super-linear-backtracking`) and cap input length before matching.

## Anti-Patterns

- `process.env.X!` read at the point of use — parse a validated env object at boot
- `jwt.verify()` without an explicit `algorithms` option, or a decoded payload cast with `as` instead of parsed
- Deprecated Zod 3 APIs in new code (`z.string().email()`, `err.flatten()`)
- Nested quantifiers on overlapping character classes in regex
- Stack traces or internal error details returned in API responses
