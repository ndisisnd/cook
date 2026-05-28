---
description: Security assessment methodology for RESTful web services — attack surface discovery, parameter identification, and testing
alwaysApply: false
---

# REST API Security Assessment

REST attack surfaces are not visible through UI inspection; services expose more endpoints than any client uses.

## NEVER
- Limit request capture to URLs only — REST services carry parameters in headers and body
- Assume visible application links enumerate the full attack surface
- Skip authentication mechanism analysis before fuzzing

## ALWAYS
- Capture full HTTP transactions (headers + body) via proxy during assessment
- Combine documentation review with dynamic proxy-based collection
- Test all HTTP methods supported by each endpoint
- Validate input handling for every parameter location: URL segments, custom headers, body
- Test authentication bypass and privilege escalation scenarios
- Document all discovered endpoints and parameter structures

## Attack Surface Discovery

| Source | What to obtain |
| ------ | -------------- |
| Formal descriptions | WSDL 2.0, WADL when available |
| Developer docs | API guides, endpoint lists |
| Source / config | Framework config files (especially .NET) for REST definitions |
| Proxy capture | All HTTP methods, headers, structured body content |

## Parameter Identification

Signals that a URL segment is a parameter (not a path):
- Repeating patterns: dates, numbers, ID-like strings
- Segment with no extension when others have extensions
- High variance segment with many different observed values
- Abnormal HTTP headers suggest header-based parameters

Verification: set suspected value to invalid input — 404 = path element; app-level error = parameter.

## Fuzzing and Auth

- Analyze valid vs invalid value patterns before fuzzing
- Focus on marginal invalid values (e.g., zero for positive integers; out-of-range sequences)
- Reverse-engineer custom token authentication and replicate it in fuzzing tools
- Account for machine-to-machine session differences; maintain auth context throughout testing

## Checklist
- [ ] Full request/response captured (headers + body) for all interactions
- [ ] All HTTP methods tested per endpoint
- [ ] URL-embedded, header, and body parameters identified and fuzzed
- [ ] Authentication mechanism reverse-engineered and emulated in tests
- [ ] Rate limiting and DoS protections assessed
- [ ] Error handling checked for information disclosure
- [ ] Discovered endpoints and parameters documented
