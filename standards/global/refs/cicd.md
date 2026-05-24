# Cicd

Cross-cutting concern: the vendor-neutral shape of a CI/CD pipeline — gating order,
job hygiene, secret handling, and artifact promotion. Loads alongside whatever
domain also matched. Platform specifics stay in their own refs and are referenced,
not restated here: Flutter packaging (Fastlane, `.aab`/`.ipa`, `subosito/flutter-action`)
lives in `flutter/refs/cicd.md`; Next.js build/Docker/standalone output in
`nextjs/refs/tooling.md`.

Each rule below carries a detection signal so review mode can flag it. P0 unless
tagged `P1 (design)`.

## Pipeline Shape & Gating

- **Fail fast — format → lint → static analysis run before tests, build, and deploy.**
  The cheap checks gate the expensive ones; a broken format never burns a build.
  Signal: a workflow that runs the build or tests before, or instead of, format/lint/static analysis.
- **Mainline merges are blocked unless required checks pass** — tests, lint, and
  typecheck, plus any stack-specific security or migration checks.
  Signal: a protected branch with no required status checks, or a merge path that bypasses them.

## Job Hygiene

- **Every job sets an explicit timeout, and superseded branch runs are cancelled.**
  Signal: a job with no `timeout-minutes`; no `concurrency` group to cancel in-progress runs.

## Triggers & Secret Exposure

- **CI runs on every PR and on protected-branch merges; deploy jobs never run from
  unreviewed PR code holding production secrets.**
  Signal: `pull_request_target` that checks out the PR head *and* exposes secrets.
- **Secrets are injected from the platform or a vault — never committed, baked into
  images, or echoed in logs.**
  Signal: a secret literal in the repo; an env-dump step (`printenv`/`env`) inside a workflow.

## Artifact Promotion & Release

- **Production promotes a previously built artifact; it does not rebuild from a
  different source state at deploy time.**
  Signal: a deploy job that runs its own build step instead of consuming the artifact CI produced.
- **P1 (design):** stage through environments with health checks and an automatic
  rollback or manual halt. P1 because an agent often cannot confirm rollout wiring
  from a diff.
  Signal: a deploy straight to production with no staging gate, health check, or rollback path.

## Anti-Patterns

Deploy-on-PR with prod secrets · uncapped jobs · rebuild-during-release · secrets in
logs · `pull_request_target` + PR-head checkout + secrets · late static analysis
(after the expensive build).
