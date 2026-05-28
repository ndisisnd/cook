---
description: Infrastructure-as-Code security — network exposure, encryption, IAM, images, secrets, backups
alwaysApply: false
---

# Infrastructure as Code

When writing Terraform, CloudFormation, Pulumi, Bicep, or ARM templates, enforce secure defaults and identify misconfigurations.

## NEVER
- Allow `0.0.0.0/0` to remote admin ports (SSH 22, RDP 3389)
- Allow `0.0.0.0/0` to database ports (3306, 5432, 1433, 1521, 27017, etc.)
- Allow `0.0.0.0/0` to Kubernetes API endpoints (EKS, AKS, GKE)
- Expose cloud database services (RDS, Azure SQL, Cloud SQL) publicly
- Use wildcard IAM permissions (`"Action": "*"`, `"Resource": "*"`)
- Assign Owner/Admin roles to service principals where a narrower role exists
- Use long-lived API keys/client secrets where workload identity is available
- Enable IMDSv1 on AWS instances (only IMDSv2)
- Use legacy local-user authentication where OAuth/OIDC is supported
- Disable administrative-activity logging on sensitive services
- Hardcode secrets, passwords, API keys, or certificates in IaC source
- Create backups without encryption, retention, or lifecycle policies
- Use non-hardened, full-OS container or VM images

## ALWAYS
- Restrict admin and data services to specific IP ranges / CIDR blocks
- Prefer private networking (VPC, VNET, VPN, internal transit) unless public access is required
- Enable VPC/VNET flow logs
- Default-deny network rules; explicit allow only for required traffic
- Prefer egress blocked by default; allow via egress firewall/proxy, security group, or DNS filter
- Encrypt at rest for all storage (S3, Azure Blob, GCS, EBS, RDS, Azure SQL, Cloud SQL, DocumentDB)
- Encrypt in transit (TLS 1.2+); validate certs; encrypt inter-service traffic inside VPCs
- Apply stricter encryption and access controls based on data classification (PII/PHI/financial/IP)
- Use separate KMS keys per classification level
- Define retention periods and automated lifecycle deletion
- Log all data access, modification, deletion; alert on anomalies
- Enable audit logging for privileged operations
- Mark secrets in Terraform with `sensitive = true`; use the equivalent annotation in other IaC

## Container & VM images
- Choose distroless or minimal container images from trusted sources
- Use secure baseline VM images from trusted publishers
- Pin tags and digests; avoid `latest`

## Backups
- Encrypt at rest and in transit using separate keys from production data
- Configure cross-region replication for backup storage
- Test restoration regularly; verify backup integrity
- Apply retention and lifecycle policies; never indefinite retention by default

## Checklist
- [ ] No `0.0.0.0/0` rules on admin / DB / k8s-API ports
- [ ] Private networking by default; flow logs on
- [ ] No wildcard IAM; workload identity in use; IMDSv2 only
- [ ] Encryption at rest + in transit everywhere; per-classification keys
- [ ] Audit logging on for privileged ops
- [ ] Secrets marked sensitive; never hardcoded
- [ ] Container/VM images distroless/minimal and pinned
- [ ] Backups encrypted, replicated, tested, lifecycle-managed
