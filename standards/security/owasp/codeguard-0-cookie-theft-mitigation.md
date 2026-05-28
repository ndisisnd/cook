---
description: Detect and mitigate session cookie theft via server-side fingerprinting and risk-based response
alwaysApply: false
---

# Cookie Theft Mitigation

## NEVER
- Store session fingerprint data client-side — always server-side only
- Rely on a single header change as the sole theft signal — use multiple detection vectors
- Skip session ID regeneration when hijacking is suspected

## ALWAYS
- Capture session environment at login: IP, User-Agent, Accept-Language, date
- Save additional headers for enhanced detection: Accept, Accept-Encoding, sec-ch-ua
- Compare fingerprint on every request to detect anomalous changes
- Account for legitimate variation (IP subnet roaming, browser updates) to reduce false positives
- Regenerate session ID when potential hijacking is detected
- Store fingerprint data using framework-provided secure session storage (encrypted)
- Log all suspicious session activity with sufficient context for investigation

## Detection and Response

| Risk Level | Trigger | Response |
|------------|---------|----------|
| High | IP geo-range mismatch, UA replaced | Require re-authentication |
| Medium | Multiple header changes simultaneously | CAPTCHA or step-up verification |
| Low | Single minor header drift | Log, continue monitoring |

## Middleware Pattern

```js
function cookieTheftDetectionMiddleware(req, res) {
  if (!checkGeoIPRange(req.clientIP, req.session.ip)) { /* high-risk response */ }
  if (!checkUserAgent(req.userAgent, req.session.ua)) { /* risk-based response */ }
  // check Accept-Language, sec-ch-ua, etc.
}
```

Apply this middleware selectively to high-value endpoints to manage performance impact.

## Checklist
- [ ] Session fingerprint (IP, UA, Accept-Language) stored server-side at login
- [ ] Fingerprint compared on each sensitive request
- [ ] Risk-based response applied (re-auth / CAPTCHA / log) by severity
- [ ] Session ID regenerated on detected anomaly
- [ ] Legitimate variation (subnet roaming, browser updates) handled gracefully
- [ ] Suspicious activity logged with full context
