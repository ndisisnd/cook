---
last_reviewed: 2026-10-23
---

# Cicd

Vendor-neutral CI/CD pipeline shape. Flutter packaging lives in `flutter/refs/cicd.md`; Next.js build/Docker/standalone output in `nextjs/refs/tooling.md`.

Each rule carries a detection signal for review mode. P0 unless tagged `P1 (design)`.

## Pipeline Shape & Gating

- **Fail fast — format → lint → static analysis run before tests, build, and deploy.**
  Signal: a workflow that runs build or tests before, or instead of, format/lint/static analysis.
- **Mainline merges are blocked unless required checks pass** — tests, lint, typecheck, plus stack-specific security or migration checks.
  Signal: a protected branch with no required status checks, or a merge path that bypasses them.

## Job Hygiene

- **Every job sets an explicit timeout, and superseded branch runs are cancelled.**
  Signal: a job with no `timeout-minutes`; no `concurrency` group cancelling in-progress runs.

## Triggers & Secret Exposure

- **CI runs on every PR and on protected-branch merges; deploy jobs never run from unreviewed PR code holding production secrets.**
  Signal: `pull_request_target` that checks out the PR head *and* exposes secrets.
- **Secrets are injected from the platform or a vault — never committed, baked into images, or echoed in logs.**
  Signal: a secret literal in the repo; an env-dump step (`printenv`/`env`) in a workflow.

## Artifact Promotion & Release

- **Production promotes a previously built artifact; it does not rebuild from a different source state at deploy time.**
  Signal: a deploy job running its own build step instead of consuming the CI artifact.
- **P1 (design):** stage through environments with health checks and an automatic rollback or manual halt (P1: an agent often cannot confirm rollout wiring from a diff).
  Signal: a deploy straight to production with no staging gate, health check, or rollback path.

## Supply Chain & Containers

- **Install a release-age cooldown and disable dependency lifecycle scripts by default.** pnpm `minimumReleaseAge` (minutes, pnpm >=10.16; default 1440 from v11), npm `min-release-age` (days, npm >=11.10), Yarn `npmMinimalAgeGate` (minutes); exempt urgent security fixes by name. Scripts off: npm `ignore-scripts=true`, Yarn `enableScripts: false` (pnpm is off already: allow-list builds in `onlyBuiltDependencies` on v10, `allowBuilds` on v11); allow-list only packages that need a build.
  Signal: no cooldown config; install scripts run for every dependency.
- **Publish packages through trusted publishing (OIDC) (npm >=11.5.1) bound to one repo and workflow file; set publish access to "require 2FA and disallow tokens".** A lockfile and provenance are not enough: a hijacked maintainer or CI ships validly signed malware. After a compromise, rotate every secret reachable from dev machines and CI.
  Signal: a long-lived `NPM_TOKEN` in publish CI.
- **Container images: pin the base by tag and digest, run as a non-root `USER`, and keep secrets out of layers (BuildKit secret mounts).** Never mount `/var/run/docker.sock` or run `--privileged`; drop caps (`--cap-drop=ALL`, `no-new-privileges`) and use a read-only root filesystem.
  Signal: `FROM x:latest`; no `USER`; a docker socket volume.
