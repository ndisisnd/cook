# Security policy

## Reporting a vulnerability

Please don't open a public issue for a security problem. Report it privately through
[GitHub's private vulnerability reporting](https://github.com/ndisisnd/cook/security/advisories/new)
— it goes straight to the maintainer and stays closed until there's a fix.

Include what you can: what the issue is, how to reproduce it, and what an attacker
could do with it. A rough report is more useful than no report.

You'll get an acknowledgment as soon as a maintainer sees it. Once a fix ships, you'll
be credited in the advisory unless you'd rather not be.

## Supported versions

This project is distributed from `main`. Fixes land on `main`; there are no maintained
release branches. Use the latest commit.

## Scope

cook runs locally inside Claude Code. It reads your repository (file paths, manifests,
git context), loads standards from its own bundled `standards/` library, and compiles
them into a single markdown payload for your coding agent. Its Python compiler stitches
those files together; the installer (`install.sh`) fetches a tarball from GitHub over
HTTPS and unpacks it into `~/.claude/skills/cook/`. Optional telemetry is written to a
local, gitignored JSON store and is off by default.

There is no server, no network listener, and no credential handling. The realistic
surface is what the installer fetches and unpacks, what the compiler reads and writes,
and the local cache and telemetry files.

## Disclosure

Report privately, and please hold off on publishing until a fix is out. Fixed issues are
published as a GitHub advisory with credit to the reporter.
