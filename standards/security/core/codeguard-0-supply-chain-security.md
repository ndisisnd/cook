---
description: Dependency and supply-chain security — pinning, SBOM, provenance, integrity, private registries
alwaysApply: false
---

# Supply Chain Security

## NEVER
- Install directly from untrusted/wildcard registries — use an allow-listed scope
- Run dependency install without a lockfile, or run `npm install` (non-deterministic) in CI — use `npm ci` or the ecosystem equivalent
- Allow install scripts to execute unreviewed
- Skip signature/provenance verification at deploy
- Accept transitive workarounds when a direct-dependency fix exists
- Ship a release with unresolved high/critical CVEs outside the documented SLA

## ALWAYS
- Pin versions via lockfile; prefer digest pinning for images and vendored assets
- Generate and store SBOMs alongside artifacts; attest provenance (SLSA, Sigstore)
- Sign artifacts at build; verify signatures at deploy/admission
- Use private registries with integrity verification; enable maintainer 2FA where you publish
- Run SCA, SAST, and IaC scans in CI gates; fail on critical findings; require approval + compensating control for overrides

## Development practices
- Minimize dependency footprint; remove unused packages; prefer stdlib for trivial tasks
- Guard against typosquatting and protestware: monitor maintainers and releases; require provenance checks
- Hermetic builds: no network during compile/packaging unless required; cache with authenticity checks

## Vulnerability management
- Patched CVEs: test and deploy fixes; document API breaking changes
- Unpatched CVEs: apply compensating controls (input validation, wrappers) per CVE type; document risk acceptance with business justification

## Incident response
- Maintain rapid rollback; isolate compromised packages; throttle rollouts; notify stakeholders
- Monitor advisory feeds (npm, OSV, GitHub Security Advisories); auto-open tickets for critical CVEs

## Checklist
- [ ] Lockfiles present and respected (`npm ci`, `pip install --require-hashes`, etc.)
- [ ] Private/allow-listed registries with integrity checks
- [ ] SBOM + provenance stored; signatures verified pre-deploy
- [ ] Automated dependency updates gated by tests and review
- [ ] High-severity vulns remediated within SLA or formally mitigated
- [ ] Rollback path tested; advisory monitoring active
