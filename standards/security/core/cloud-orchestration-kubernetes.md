---
description: Kubernetes hardening — RBAC, admission policies, network policies, secrets, supply chain
alwaysApply: false
---

# Kubernetes Hardening

## NEVER
- Grant cluster-admin or wildcard RBAC to application service accounts
- Run pods as root, with `privileged: true`, or with a writable root filesystem
- Store plaintext secrets in manifests, ConfigMaps, or container images
- Mount the Docker/CRI socket into a workload
- Pull unsigned images, or accept image tags without digest pinning
- Disable cluster audit logs or allow direct etcd access from outside the control plane

## ALWAYS
- Separate namespaces per team/app; bind only the roles each workload needs
- Enforce admission policies (OPA/Gatekeeper/Kyverno) covering image source, non-root, dropped capabilities, read-only root FS, and required network policies
- Default-deny network policies; explicit ingress/egress allow-lists; mTLS within service mesh where applicable
- Source secrets via KMS provider; rotate regularly; restrict secret mount paths
- Use hardened OS on nodes with auto-updates; isolate sensitive workloads via taints/tolerations on dedicated nodes
- Verify image signatures and provenance (SLSA/Sigstore) at admission

## Verification
- Run CIS Kubernetes benchmark scans against the cluster
- Unit-test admission policies (OPA/conftest) in CI; periodic admission dry-run on live manifests

## Incident readiness
- Centralize audit logs; restrict etcd access to control plane; test backup/restore regularly
- Define break-glass roles requiring MFA and time-bound approval

## Checklist
- [ ] Namespaces scoped per team/app; RBAC least-privilege; audit logs on
- [ ] Admission enforces image provenance, non-root, dropped caps, read-only FS, network policies
- [ ] Default-deny network policies with explicit egress allow-list
- [ ] Secrets sourced from KMS; no plaintext in manifests/images
- [ ] Image signatures and SLSA provenance verified at admission
- [ ] etcd isolated; backups tested; break-glass roles defined
