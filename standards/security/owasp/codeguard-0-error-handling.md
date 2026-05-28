---
description: Secure error handling — prevent info leakage, ensure proper logging, return generic responses
alwaysApply: false
---

# Error Handling Security

## NEVER
- Return stack traces, file paths, version info, or internal error details to clients
- Log passwords, tokens, or personal information in error logs
- Leave debug error pages or detailed exception output enabled in production
- Expose server version or technology stack in error responses

## ALWAYS
- Implement global error handlers that catch all unhandled exceptions
- Return generic error messages to clients (e.g., "An error occurred, please retry")
- Log detailed error context server-side: user ID, IP, timestamp, stack trace
- Use appropriate HTTP status codes: 4xx for client errors, 5xx for server errors
- Add security headers to error responses to prevent XSS and info disclosure
- Escape error response content to prevent injection
- Use structured logging; implement log rotation and secure storage
- Disable debug/detailed error pages in production (ASP.NET: `customErrors mode="RemoteOnly"`)
- Follow RFC 7807 for consistent error response format

## Platform Config

| Platform | Config |
|----------|--------|
| ASP.NET | `<customErrors mode="RemoteOnly">` in web.config |
| ASP.NET Core | Disable `UseDeveloperExceptionPage()` in production |
| Java | Map all exceptions to generic `/error.jsp` in web.xml |
| Spring Boot | `@RestControllerAdvice` with `ProblemDetail.forStatusAndDetail()` |

## Java/Spring Example
```java
@RestControllerAdvice
public class RestResponseEntityExceptionHandler extends ResponseEntityExceptionHandler {
    @ExceptionHandler(Exception.class)
    public ProblemDetail handleGlobalError(RuntimeException ex, WebRequest req) {
        // log ex server-side
        return ProblemDetail.forStatusAndDetail(HttpStatus.INTERNAL_SERVER_ERROR,
            "An error occurred, please retry");
    }
}
```

## Checklist
- [ ] Global error handler catches all unhandled exceptions
- [ ] Client responses contain no stack traces, paths, or version info
- [ ] Debug error pages disabled in production
- [ ] Server-side logs include user context but no sensitive data
- [ ] Error responses use correct HTTP status codes
- [ ] Error response content escaped; security headers present
- [ ] Structured logging with rotation and secure storage in place
