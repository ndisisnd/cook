# Error Handling

## Error Architecture

Three-layer model — each layer has one job:

| Layer | Responsibility |
| --- | --- |
| API layer | Map domain errors to HTTP responses globally, not per-handler |
| Domain layer | Throw pure business errors — no HTTP status codes here |
| Infrastructure layer | Wrap third-party exceptions — never leak raw DB or driver errors upward |

## Error Mechanics

- Wrap errors with context when propagating: `fmt.Errorf("process payment: %w", err)`, `new Error('process payment', { cause })`.
- Replace the original only when it leaks internal details (stack trace, DB schema, internal path).
- Use `SCREAMING_SNAKE_CASE` error codes tied to domain operations: `ORDER_PAYMENT_FAILED`, `USER_NOT_FOUND`.
- Never swallow: every caught error must be handled, logged, or re-thrown with context.

## Standard Response Envelope

```json
{
  "error": {
    "code": "ORDER_PAYMENT_FAILED",
    "message": "Payment method declined",
    "traceId": "4bf92f3577b34da6a3ce929d0e0e4736",
    "details": []
  }
}
```

For validation failures, populate `details[]` with per-field errors:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "traceId": "...",
    "details": [{ "field": "email", "message": "Must be a valid email address" }]
  }
}
```

## Error Classification

| Condition | HTTP code | Notes |
| --- | --- | --- |
| Validation failure | 400 | Return `details[]` with field paths |
| Missing or invalid auth | 401 | Generic message — never expose the specific reason |
| Valid token, lacking permission | 403 | |
| Resource not found | 404 | Distinguish from 403 to avoid leaking existence |
| Conflict or duplicate | 409 | Include the conflicting resource ID |
| Business rule violation | 422 | |
| Unhandled server error | 500 | Log full detail server-side; return generic code to client |

## Anti-Patterns

- Swallowing errors: `catch(e) {}` with no logging or re-throw
- Stack traces in API responses
- Using `500` for validation errors that should be `400`
- Domain layer returning HTTP status codes
- Leaking raw DB error messages to the API response
