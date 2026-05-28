---
description: Integrate structured threat modeling into SDLC to identify and mitigate security threats early
alwaysApply: false
---

# Threat Modeling

## NEVER
- Treat threat modeling as optional or a one-time exercise
- Leave threat models undocumented or inaccessible to stakeholders
- Define mitigations without making them testable requirements
- Update the system without reviewing and updating the threat model

## ALWAYS
- Perform threat modeling during the design phase, before code is written
- Create Data Flow Diagrams (DFDs) showing trust boundaries, data flows, stores, processes, and external entities
- Apply STRIDE systematically to every component
- Prioritize threats by likelihood × impact vs. mitigation cost
- Document each threat's response: Mitigate, Eliminate, Transfer, or Accept
- Reference OWASP ASVS / MITRE CWE when writing mitigation requirements
- Involve dev, security, architecture, product, and operations in reviews
- Update the threat model whenever architecture or features change

## STRIDE Reference

| Category | Violates | Example |
|----------|----------|---------|
| Spoofing | Authenticity | Stolen auth token to impersonate user |
| Tampering | Integrity | Abusing app to perform unintended DB writes |
| Repudiation | Non-repudiability | Log manipulation to cover attacker actions |
| Information Disclosure | Confidentiality | DB extraction of user account data |
| Denial of Service | Availability | Account lockout via repeated failed auth |
| Elevation of Privilege | Authorization | JWT tampering to escalate role |

## Process (4 Questions)

| Step | Question | Key output |
|------|----------|------------|
| 1 — Model | What are we working on? | DFDs with trust boundaries |
| 2 — Identify | What can go wrong? | STRIDE-enumerated threats |
| 3 — Respond | What are we going to do? | Mitigate / Eliminate / Transfer / Accept per threat |
| 4 — Review | Did we do a good enough job? | Stakeholder sign-off; mitigations verified testable |

## Checklist
- [ ] DFD created covering all trust boundaries, data flows, stores, and external entities
- [ ] STRIDE applied to each component; threats documented
- [ ] Every threat has an assigned response strategy
- [ ] Mitigations written as testable, implementable requirements
- [ ] Cross-functional review completed (dev, security, arch, product, ops)
- [ ] Threat model stored accessibly and kept in sync with system changes
