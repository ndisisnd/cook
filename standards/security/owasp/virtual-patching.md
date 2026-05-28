---
description: Apply temporary WAF/IPS controls to block known vulnerabilities while permanent code fixes are developed
alwaysApply: false
---

# Virtual Patching

Virtual patches are security policy enforcement rules (WAF/IPS) that intercept exploitation attempts in transit without modifying source code.

## NEVER
- Create exploit-specific patches that block only exact payloads — they provide minimal protection
- Treat virtual patches as permanent replacements for code-level fixes
- Deploy virtual patches without first testing in "Log Only" mode
- Skip false-positive validation before switching to blocking mode

## ALWAYS
- Prioritize permanent code fixes; treat virtual patches as temporary gap coverage
- Pre-authorize and pre-deploy virtual patching tools (ModSecurity, WAF, ESAPI WAF) before incidents occur
- Enable detailed HTTP audit logging (URI, full headers, request/response bodies) before an incident
- Subscribe to vendor/CVE alert feeds for early vulnerability notification
- Prefer positive security (allow-list) rules over negative security (block-list) rules
- Ensure virtual patches produce no false positives and no false negatives
- Test patches in "Log Only" mode first; request retest from vulnerability team before blocking
- Return to analysis if evasions are detected during retesting
- Document virtual patch rule IDs in the issue tracker; schedule periodic re-assessment for removal

## Security Model Comparison

| Model | Speed | Evasion risk | Best for |
|-------|-------|-------------|----------|
| Positive (allow-list) | Slower to create | Low | Specific, well-scoped parameters |
| Negative (block-list) | Fast | Higher | Broad initial coverage |

Positive security example (ModSecurity — only integers accepted for `reqID`):
```text
SecRule ARGS:/reqID/ "!@rx ^[0-9]+$" \
  "id:2,phase:2,block,msg:'Input Validation Error for reqID'"
```

## Workflow

```
Preparation → Identification → Analysis → Patch Creation → Implementation/Testing → Recovery/Follow-Up
```

Key analysis items: verify CVE identifier, designate impact level, specify affected versions, collect PoC exploit, list config requirements to trigger.

## Checklist
- [ ] Virtual patching tools (ModSecurity / WAF) deployed and ready before incidents
- [ ] Detailed HTTP audit logging enabled
- [ ] Vulnerability analyzed: CVE confirmed, impact level set, PoC collected
- [ ] Positive security rule used where scope is known; negative security for broad coverage
- [ ] Patch tested in Log Only mode with no false positives confirmed
- [ ] Rule IDs recorded in issue tracker; removal scheduled after code fix ships
- [ ] Patch does not block only a single exploit payload
