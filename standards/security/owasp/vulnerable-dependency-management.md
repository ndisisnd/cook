---
description: Detect, triage, and remediate vulnerable third-party dependencies through automated scanning and systematic response
alwaysApply: false
---

# Vulnerable Dependency Management

## NEVER
- Skip dependency vulnerability scanning at any phase of the project lifecycle
- Rely solely on external controls when a source-level fix is available
- Accept high-severity vulnerability risk without escalating to Chief Risk Officer
- Modify transitive dependencies directly without understanding the full dependency chain

## ALWAYS
- Integrate automated vulnerability scanning from project inception (OWASP Dependency-Check, npm audit, Dependency-Track)
- Scan against CVE databases, full-disclosure sources, and provider-specific feeds
- Fail CI builds on high-severity vulnerability findings
- Scan on every build; track and report remediation progress
- Maintain comprehensive automated tests covering all features that use affected dependencies
- Document every vulnerability decision: CVSS score, mitigation rationale, test results, risk acceptance
- Prefer fixing at source (dependency update or code fix) over compensating controls
- Monitor dependencies for maintenance status and community activity

## Remediation Case Matrix

| Case | Condition | Action |
|------|-----------|--------|
| 1 | Patched version available | Update in test env → run tests → deploy if pass |
| 2 | Patch delayed; workaround available | Apply workaround; add protective wrappers on impacted functions |
| 3 | No patch | Identify all callers; implement compensating controls; add unit tests |
| 4 | Newly discovered vulnerability | Notify provider → follow Case 2 (cooperative) or Case 3 (unresponsive) |

Protective wrapper pattern (Case 2/3):
```java
public void callFunctionWithRCEIssue(String input) {
    if (Pattern.matches("[a-zA-Z0-9]{1,50}", input)) {
        functionWithRCEIssue(input);
    } else {
        SecurityLogger.warn("Exploitation attempt detected");
        throw new SecurityException();
    }
}
```

## Checklist
- [ ] Dependency scanning (Dependency-Check / npm audit) runs on every CI build
- [ ] High-severity findings fail the build
- [ ] All four remediation cases have a documented response plan
- [ ] Protective wrappers or compensating controls added when no patch is available
- [ ] Automated tests cover features using vulnerable dependencies
- [ ] Risk acceptance decisions documented and escalated to CRO
- [ ] Dependencies monitored for maintenance status and new disclosures
