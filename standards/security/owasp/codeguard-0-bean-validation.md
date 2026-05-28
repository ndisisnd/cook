---
description: Java Bean Validation — centralized declarative input validation with Hibernate Validator
alwaysApply: false
---

# Bean Validation (Java / Jakarta)

## NEVER
- Scatter validation logic across the business layer — centralize on domain models
- Expose system internals or stack traces in validation error responses
- Use `@NotNull`/`@NotBlank` without accompanying `@Size` constraints on sensitive fields
- Trust client-supplied data without server-side constraint validation

## ALWAYS
- Define all validation constraints as annotations on domain model fields
- Combine `@NotNull`/`@NotBlank` with `@Size` on sensitive fields
- Use `@Valid` in controllers to trigger validation automatically
- Annotate nested objects with `@Valid @NotNull` to cascade validation
- Handle `BindingResult` errors: log the field errors, return `400 Bad Request`, never expose sensitive system info
- Create custom constraint annotations for complex business rules not covered by standard annotations

## Key annotations

| Annotation | Use |
|---|---|
| `@NotNull` / `@NotBlank` | Required fields; `@NotBlank` also rejects whitespace-only |
| `@Size(min, max)` | Length bounds for strings and collections |
| `@Email` | Email format; combine with `@Size(max=254)` |
| `@Pattern(regexp)` | Allowlist character set for passwords/codes |
| `@Min` / `@Max` | Numeric range bounds |
| `@Valid` | Cascade validation into nested objects |

## Controller pattern
```java
@PostMapping("/register")
public ResponseEntity<?> register(@Valid @RequestBody UserForm form, BindingResult result) {
    if (result.hasErrors()) {
        logger.warn("Validation failed: {}", result.getFieldErrors());
        return ResponseEntity.badRequest().body(result.getFieldErrors());
    }
    userService.create(form);
    return ResponseEntity.ok("Success");
}
```

## Checklist
- [ ] Validation constraints declared on domain model fields, not scattered in services
- [ ] Sensitive fields have both `@NotBlank` and `@Size` constraints
- [ ] Controller methods use `@Valid` to trigger automatic validation
- [ ] Nested objects annotated with `@Valid @NotNull`
- [ ] Validation errors return `400` with field details; no system internals exposed
- [ ] Custom constraints implemented for business rules not covered by built-ins
