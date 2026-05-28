---
description: DevOps, CI/CD, and container hardening — pipelines, artifacts, Docker/K8s images, virtual patching, toolchain
alwaysApply: false
---

# DevOps, CI/CD & Containers

## NEVER
- Hardcode secrets in pipeline configs or Dockerfiles — fetch from vault/KMS at runtime
- Run containers as root, `--privileged`, or with the Docker daemon socket mounted
- Expose the Docker daemon over TCP without TLS (`-H tcp://0.0.0.0:XXX`)
- Mount `/var/run/docker.sock` into application containers or compose services
- Use base images without pinned tags + digests, or images that include shells/package managers in the final stage
- Skip artifact signature verification at deploy
- Disable CI security gates (SAST/SCA/DAST/IaC) to merge

## ALWAYS
- Use protected branches, mandatory reviews, and signed commits
- Use ephemeral, isolated runners with least-privilege credentials; mask secrets in logs
- Pin dependencies via lockfiles; use private registries; verify integrity
- Sign commits and artifacts (containers, jars); verify before deploy; adopt SLSA provenance
- Run SAST, SCA, DAST, and IaC scans in CI; block on critical findings

## Docker & container hardening
- Set `USER` to a non-root UID in the Dockerfile
- Use `--security-opt=no-new-privileges`
- `--cap-drop=ALL` and add only the capabilities needed
- Read-only root filesystem; tmpfs for temp writes; CPU/memory limits
- Custom networks (not host); limit exposed ports
- Minimal base images (distroless/alpine); pin by tag + digest; strip package managers; add `HEALTHCHECK`
- Mount secrets via runtime secret stores — never bake into layers or ENV
- Scan images at build and at admission; block high-severity vulns

## Node.js in containers
- `npm ci --omit=dev` for deterministic builds; pin base image by digest
- `ENV NODE_ENV=production`
- Drop privileges with `USER node`; copy with correct ownership
- Use an init (`dumb-init` or similar) and implement graceful shutdown
- Multi-stage builds; secrets via BuildKit mounts; maintain `.dockerignore`

## Virtual patching (temporary mitigation)
- Use WAF/IPS/ModSecurity when a code fix is not yet available
- Prefer positive (allow-list) rules over exploit-specific signatures
- Process: prepare tooling in advance → analyze CVE → deploy in log-only → switch to enforce → retire after code fix lands

## C/C++ toolchain hardening
- Compiler: `-Wall -Wextra -Wconversion`, `-fstack-protector-all`, `-fPIE`/`-pie`, `-D_FORTIFY_SOURCE=2`, CFI (`-fsanitize=cfi` with LTO)
- Linker: full RELRO (`-Wl,-z,relro,-z,now`), noexecstack, NX/DEP, ASLR
- Debug builds: enable sanitizers (ASan, UBSan); assert-only in debug
- CI: verify protections with `checksec`; fail builds if missing

## Checklist
- [ ] Pipeline: secrets in vault; ephemeral runners; security scans; signed artifacts with provenance
- [ ] Containers: non-root, least-privilege, read-only FS, resource limits; no socket mounts
- [ ] Images: minimal, pinned by digest, scanned; healthchecks; `.dockerignore` maintained
- [ ] Node images: `npm ci`, `NODE_ENV=production`, init + graceful shutdown
- [ ] Virtual-patching process documented; rules accurate; retired after code fix
- [ ] Native builds: hardening flags verified in CI via `checksec`
