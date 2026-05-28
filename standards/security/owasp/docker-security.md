---
description: Secure Docker containers — non-root users, capabilities, secrets, networking, images
alwaysApply: false
---

# Docker Security

## NEVER
- Run containers as root; never omit or set `USER root` in Dockerfiles
- Mount `/var/run/docker.sock` into containers
- Enable TCP Docker daemon socket without TLS (`-H tcp://0.0.0.0:XXX`)
- Use `--privileged` flag
- Use `--net=host` or share the host network namespace
- Embed secrets, passwords, or API keys in Dockerfiles or environment variables in image layers
- Use `latest` tags for base images in production
- Use `ADD` when `COPY` suffices (no archive extraction needed)
- Curl-bash in `RUN` directives when package managers are available
- Disable seccomp, AppArmor, or SELinux security profiles

## ALWAYS
- Specify a non-root `USER` in Dockerfiles; use `docker run -u <user>` or `securityContext.runAsUser`
- Drop all capabilities (`--cap-drop all`) and add only required ones (`--cap-add`)
- Set `--security-opt=no-new-privileges`; set `allowPrivilegeEscalation: false` in Kubernetes
- Use read-only root filesystems (`--read-only` / `readOnlyRootFilesystem: true`)
- Mount volumes `:ro` when write access is not needed; use `--tmpfs` for temporary writes
- Use Docker Secrets or Kubernetes encrypted secrets for sensitive data
- Define custom Docker networks; avoid default bridge networking
- Limit memory and CPU resources in compose/Kubernetes specs
- Include `HEALTHCHECK` in Dockerfiles
- Use minimal base images (alpine, distroless); remove package managers from production images
- Scan images for vulnerabilities before deployment

## Checklist
- [ ] Non-root `USER` set in all Dockerfiles
- [ ] No `docker.sock` volume mount; no TCP daemon without TLS
- [ ] `--cap-drop all` applied; no `--privileged`
- [ ] Read-only root filesystem enabled; `--tmpfs` for ephemeral writes
- [ ] No secrets in Dockerfile or image layers; Docker/Kubernetes secrets used
- [ ] Base image pinned to specific version; image scanned before deployment
- [ ] No `--net=host`; custom networks defined; unnecessary ports unexposed
