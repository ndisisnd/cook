# TypeScript Security Patterns

## Input Validation (Zod)

```typescript
import { z } from 'zod';

const CreateUserSchema = z.object({
  email: z.string().email(),
  name:  z.string().min(1).max(100),
  role:  z.enum(['user', 'admin']),
});

type CreateUserDto = z.infer<typeof CreateUserSchema>;

app.post('/users', (req, res) => {
  const result = CreateUserSchema.safeParse(req.body);
  if (!result.success) {
    return res.status(400).json({ errors: result.error.flatten().fieldErrors });
  }
  return userService.create(result.data); // fully typed and validated
});
```

**Query string type coercion risk**: identical parameter names parse differently depending on repetition and bracket syntax (`?foo=bar` → string, `?foo=bar&foo=baz` → array, `?foo[bar]=baz` → object). Validate and coerce types explicitly — never assume a query param is a string.

## JWT Authentication

```typescript
import jwt from 'jsonwebtoken';

interface JWTPayload { userId: string; role: string; }

export class AuthService {
  private readonly secret: string;

  constructor() {
    this.secret = process.env.JWT_SECRET!;
    if (!this.secret) throw new Error('JWT_SECRET environment variable is required');
  }

  generateToken(payload: JWTPayload): string {
    return jwt.sign(payload, this.secret, {
      expiresIn: '1h',
      algorithm: 'HS256',
      issuer: 'your-app',
      audience: 'your-api',
    });
  }

  verifyToken(token: string): JWTPayload {
    try {
      // Always pin the expected algorithm — defense-in-depth against algorithm confusion attacks
      return jwt.verify(token, this.secret, { algorithms: ['HS256'] }) as JWTPayload;
    } catch {
      throw new Error('Invalid or expired token');
    }
  }
}
```

> **RS256 (multi-service):** Use a PEM RSA private key to sign (`process.env.JWT_PRIVATE_KEY`) and the corresponding public key to verify (`process.env.JWT_PUBLIC_KEY`). `HS256` with a shared secret is correct for single-service deployments; `RS256` is correct when verifiers must not have signing capability.

## Secure Cookie Options

```typescript
const cookieOpts = {
  httpOnly: true,
  secure: process.env.NODE_ENV === 'production',
  sameSite: 'strict' as const,
  maxAge: 60 * 60 * 1000, // 1 hour
};
// Verify your environment's NODE_ENV convention ('prod' vs 'production') before deploying.
```

## Middleware Stack (Express)

```typescript
import express from 'express';
import helmet from 'helmet'; // sets 14 security headers automatically
import cors   from 'cors';
import hpp    from 'hpp';    // deduplicates repeated query/body params before handlers see them

const app = express();

app.use(helmet());
app.use(hpp());
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') ?? [],
  credentials: true,
}));
app.use(express.json({ limit: '10kb' })); // prevents memory exhaustion from large payloads
```

## Role-Based Access Control

```typescript
type Role       = 'admin' | 'user' | 'guest';
type Permission = 'read'  | 'write' | 'delete';

const rolePermissions: Record<Role, Permission[]> = {
  admin: ['read', 'write', 'delete'],
  user:  ['read', 'write'],
  guest: ['read'],
};

function requirePermission(permission: Permission) {
  return (req: Request, res: Response, next: NextFunction) => {
    const role = req.user?.role as Role | undefined;
    if (!role || !rolePermissions[role]?.includes(permission)) {
      return res.status(403).json({ error: 'Forbidden' });
    }
    next();
  };
}
```

## Child Process Safety

`child_process.exec()` forwards the command string to `/bin/sh` — any shell metacharacter in a dynamic value becomes a command injection vector. Use `execFile` with a static command and a separate args array; no shell is involved:

```typescript
import { execFile } from 'child_process';
import { promisify } from 'util';

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

Run `npx vuln-regex-detector` on any non-trivial regex before shipping.

## Anti-Patterns

- Missing `hpp()` middleware — duplicate query params can silently override validated values
- `express.json()` without a `limit` — accepts arbitrarily large payloads
- `jwt.verify()` without an explicit `algorithms` option — the library has key-type defaults, but pinning is standard defense-in-depth and makes intent explicit
- Nested quantifiers on overlapping character classes in regex
- Stack traces or internal error details returned in API responses
