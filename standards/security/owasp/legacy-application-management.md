---
description: Security controls for managing End-of-Life and legacy applications still in active use
alwaysApply: false
---

# Legacy Application Management

## NEVER
- Leave a legacy application exposed without additional network-level access controls
- Skip vulnerability scanning because automated tools have limited coverage
- Allow direct user access to legacy applications without intermediary services where possible
- Run legacy apps without an incident response playbook and escalation contacts

## ALWAYS
- Maintain a comprehensive inventory: version, config, network hosts, SBOM, physical location
- Conduct formal risk assessment (NIST RMF or equivalent) covering data impact, known CVEs, and lateral movement risk
- Host legacy apps in restricted subnets with IP allowlisting; close all unnecessary ports
- Encrypt data at rest and in transit; for plain-text-only protocols, apply maximum network access restrictions
- Prioritize patches by CVE severity and public exploit availability; apply access restrictions when patching is impossible
- Run regular vulnerability scans (Nessus/Qualys), SAST, and SCA on schedule
- Develop custom APIs or scripts to feed legacy log data into modern security tooling
- Document and maintain institutional knowledge; train multiple staff members on legacy troubleshooting
- Maintain a migration plan with explicit milestones, dates, and business/security justification

## Access Controls
- Require authentication via IdP; enforce VPN for network access where applicable
- Disable high-risk administrative features and reduce available feature sets
- Consider air-gapping for high-risk applications when patching is not possible

## Monitoring & Incident Response
- Monitor for anomalous network traffic and activity surges
- Prioritize incident response for critical legacy systems
- Include emergency procedures, escalation contacts, and IR leader in playbooks
- Integrate IR with broader business continuity planning

## Checklist
- [ ] Full inventory maintained: version, config, SBOM, network dependencies
- [ ] Formal risk assessment completed using a recognized framework
- [ ] Restricted subnet, IP allowlisting, unnecessary ports closed
- [ ] Data encrypted at rest and in transit (or air-gapped)
- [ ] Automated scans (SAST, SCA, network) run on schedule; patches prioritized by CVE/exploit
- [ ] Custom log integration feeds legacy events into modern SIEM/security tooling
- [ ] Incident response playbook documented with escalation contacts
- [ ] Migration plan with milestones and completion dates in place
