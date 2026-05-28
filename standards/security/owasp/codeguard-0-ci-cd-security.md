---
description: CI/CD pipeline security — secrets, supply chain, build isolation, signing, and scanning
alwaysApply: false
---

# CI/CD Security

## NEVER
- Hardcode secrets (API keys, passwords, tokens) in pipeline config files or source code
- Allow merges to protected branches without code review and passing status checks
- Grant build agents more permissions than the job requires
- Reuse build environments across jobs — use ephemeral containers or VMs only
- Pin dependencies without validating integrity hashes
- Deploy artifacts that are unsigned or whose signatures have not been verified
- Allow pipeline jobs to access production resources during testing

## ALWAYS
- Fetch secrets at runtime from a dedicated secret manager (HashiCorp Vault, AWS Secrets Manager, CI platform secret store); mask them in logs
- Enforce commit signing (GPG) to verify authorship and prevent spoofing
- Apply least privilege to all pipeline identities and build agents
- Use ephemeral, isolated build environments destroyed after each job
- Lock dependencies with a lock file (`package-lock.json`, `yarn.lock`, `Gemfile.lock`)
- Validate package integrity with hashes/checksums provided by the package manager
- Use private registries for internal packages to prevent dependency confusion attacks
- Integrate SAST, SCA, DAST, and IaC scanning as pipeline gates
- Sign all Git commits, build artifacts (Docker images, JARs), and deployment packages
- Verify signatures before deployment; reject unsigned or invalidly signed artifacts
- Consider SLSA framework for a verifiable chain of custody

## Security scanning gates

| Scan type | What it checks |
|---|---|
| SAST | Source code for vulnerabilities |
| SCA | Dependencies for known CVEs |
| DAST | Running application in test environment |
| IaC | Terraform/CloudFormation for misconfigurations |

## Checklist
- [ ] Secrets fetched from secret manager at runtime; never in source or config
- [ ] Protected branches require review + passing checks before merge
- [ ] Commit signing enforced
- [ ] Build agents use least-privilege identities; ephemeral isolated environments
- [ ] Dependency lock files committed; integrity hashes validated
- [ ] Private registry used for internal packages
- [ ] SAST, SCA, DAST, IaC scans are pipeline gates
- [ ] Artifacts signed; signatures verified before deployment
