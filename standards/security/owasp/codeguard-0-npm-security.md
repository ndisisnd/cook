---
description: npm package security — dependency integrity, secret leakage prevention, and registry hygiene
alwaysApply: false
---

# NPM Security

## NEVER
- Expose npm tokens in source code, logs, CI env vars, or config files committed to VCS
- Install packages without vetting credibility (check source repo + registry metadata)
- Upgrade to a new version immediately — allow community review time
- Allow wildcard package names or typosquatted variants (verify with `npm info <pkg>`)
- Use `npm install` in CI or production (non-deterministic; use `npm ci` instead)

## ALWAYS
- Use `npm ci` in CI/CD and production; `yarn install --frozen-lockfile` for Yarn
- Run `npm publish --dry-run` before actual publish; use `files` in package.json as allowlist
- Use `--ignore-scripts` when installing from unknown or unvetted sources
- Enable 2FA with `npm profile enable-2fa auth-and-writes`
- Create tokens with minimum required permissions; restrict to IP CIDR ranges where possible
- Audit tokens regularly with `npm token list`; revoke unused or compromised tokens immediately
- Run `npm audit` on every CI run; triage and fix findings
- Use a private registry (e.g. Verdaccio) for access control and routing

## Publish Safety
- `files` field in package.json acts as allowlist for published content
- If both `.gitignore` and `.npmignore` exist, `.npmignore` takes precedence — audit both
- NPM auto-revokes tokens it detects in published packages, but prevention is mandatory

## Typosquatting Defense
- Verify package name + metadata: `npm info <package>`
- Confirm repository link points to expected maintainer
- Stay logged out of npm during regular development
- Check for look-alike names when copy-pasting install commands

## Token Management

| Action | Command |
|--------|---------|
| Create read-only token | `npm token create --read-only` |
| Restrict to CIDR | `npm token create --cidr=<range>` |
| List tokens | `npm token list` |
| Revoke token | `npm token revoke <token>` |

## Checklist
- [ ] `npm ci` used in all CI and production installs
- [ ] No tokens, credentials, or secrets in committed files
- [ ] `npm publish --dry-run` verified before every publish
- [ ] 2FA enabled with `auth-and-writes` mode
- [ ] Tokens scoped to minimum permissions; unused tokens revoked
- [ ] `npm audit` passing in CI; vulnerabilities triaged
- [ ] Packages vetted before install; `--ignore-scripts` for untrusted sources
