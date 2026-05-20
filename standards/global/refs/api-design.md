# API Design

## HTTP Verb Semantics

- `GET` read-only, idempotent — never mutates state.
- `POST` creates or triggers. `PUT` fully replaces. `PATCH` partially updates. `DELETE` removes.
- Non-CRUD actions as sub-resources: `POST /orders/:id/cancel`, not `POST /cancelOrder`.

## Status Codes

| Scenario | Code |
| --- | --- |
| Successful read | 200 |
| Resource created (add `Location` header) | 201 |
| Action with no response body | 204 |
| Malformed request or validation failure | 400 |
| Missing or invalid auth token | 401 |
| Valid token, lacking permission | 403 |
| Resource not found | 404 |
| Duplicate or already exists | 409 |
| Business rule violation | 422 |
| Rate limit exceeded (add `Retry-After`) | 429 |
| Unhandled server error | 500 |

Never return 200 with `{ "success": false }` — broken monitoring and observability.

## URL Design

- Lowercase, kebab-case: `/user-profiles`, not `/UserProfiles` or `/user_profiles`.
- Plural nouns: `/orders`, `/products`. Not `/order`, `/getProducts`.
- No verbs in base paths. Action sub-resources only: `/orders/:id/cancel`.
- Nesting max 2 levels: `/users/:id/orders`. Deeper nesting is hard to version, document, and cache.

## Versioning

- Default: URL path versioning — `/v1/users`, `/v2/users`.
- Header versioning (`Api-Version: 2`) acceptable for internal APIs.
- Never mix versions in the same controller module.
- Support the previous major version for at least 6 months after a new release.
- Signal retirement with `Deprecation: true` and `Sunset: <date>` headers.

```http
HTTP/1.1 200 OK
Deprecation: true
Sunset: Sat, 31 Dec 2025 23:59:59 GMT
Link: </v2/orders>; rel="successor-version"
```

## Pagination

- Prefer cursor-based (`cursor` + `limit`) for large or live datasets.
- Use offset pagination only for small, static datasets.
- Default `limit: 20`, max `100`. Reject requests exceeding max.

```json
{
  "data": [{ "id": "...", "status": "pending" }],
  "pagination": {
    "nextCursor": "eyJpZCI6MTB9",
    "hasNextPage": true,
    "limit": 20
  }
}
```

## OpenAPI Contract

- Generate from code annotations — not hand-written YAML.
- Every public API needs an OpenAPI 3.1 spec.
- Include: request/response schemas, error shapes, auth requirements, worked examples.
- Review spec in PR. Breaking changes require a version bump.

## URL and Error Examples

```text
GET    /v1/orders              # list (paginated)
POST   /v1/orders              # create → 201 + Location header
GET    /v1/orders/:id          # single resource
PATCH  /v1/orders/:id          # partial update
DELETE /v1/orders/:id          # remove → 204
POST   /v1/orders/:id/cancel   # action sub-resource
```

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "traceId": "4bf92f3577b34da6a3ce929d0e0e4736",
    "details": [{ "field": "email", "message": "Must be a valid email address" }]
  }
}
```

## Anti-Patterns

- `GET` mutations — search engines and CDNs cache GET requests
- `200` response for errors — breaks monitoring and alerting
- Deeply nested URLs beyond two levels
- Breaking changes (field removal, rename, status code change) without a version bump
- Verb-based URL paths (`/getUser`, `/createOrder`)
