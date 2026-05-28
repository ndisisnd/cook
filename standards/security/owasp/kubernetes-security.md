---
description: Kubernetes cluster hardening — host, build, deploy, runtime, RBAC, secrets, and audit logging
alwaysApply: false
---

# Kubernetes Security

## NEVER
- Run containers as root or with privileged security contexts
- Store secrets in environment variables; mount them as read-only volumes instead
- Allow unauthenticated or anonymous access to the kubelet or API server
- Use built-in authentication methods in production clusters
- Leave etcd accessible without mutual TLS and firewall isolation

## ALWAYS
- Run the latest stable Kubernetes version (project supports last 3 minor releases)
- Apply `securityContext` with `runAsNonRoot: true` and `readOnlyRootFilesystem: true`
- Enforce Pod Security Admission with `restricted` profile on all non-system namespaces
- Implement NetworkPolicies to segment pod-to-pod traffic
- Define ResourceQuotas per namespace to prevent DoS
- Enable RBAC with least-privilege principles; use OIDC with MFA for human access
- Enable encryption at rest for Secret resources in etcd
- Enable Kubernetes audit logging for all API requests
- Integrate vulnerability scanning into CI to block vulnerable images

## Build Phase
- Store approved images in private registries only
- Use minimal/distroless base images; remove shells and package managers from runtime containers

## Runtime Monitoring
Monitor for anomalies and alert on:
- Shell execution inside containers
- Access to sensitive files (e.g., `/etc/shadow`)
- Unexpected outbound network connections
- Process activity deviations between replicas

## Access & Secrets
- Rotate credentials frequently; revoke bootstrap tokens promptly
- Use external secrets managers for multi-cluster environments
- Secure the Kubernetes Dashboard behind an authenticating reverse proxy
- Control network access to sensitive ports: `6443` (API server), `2379-2380` (etcd)

## Checklist
- [ ] All pods run non-root with read-only root filesystem
- [ ] Pod Security Admission enforced at `restricted` level on workload namespaces
- [ ] NetworkPolicies in place; ResourceQuotas defined
- [ ] etcd access restricted: mutual TLS + firewall, encryption at rest enabled
- [ ] RBAC least-privilege; OIDC + MFA for cluster access
- [ ] Audit logging enabled; runtime anomaly monitoring active
- [ ] CI pipeline scans images; only approved images in private registries
