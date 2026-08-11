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

This project is distributed from `main`, with tagged releases cut from it; `v1.0.0` is
the current release. Fixes land on `main`; there are no maintained release branches. If
you're on an older tag, update to the latest commit or the newest release rather than
waiting for a backport.

## Scope

cook runs locally inside your coding agent — Claude Code or the OpenAI Codex CLI. It
reads your repository (file paths, manifests, git context), loads standards from its own
bundled `standards/` library, and compiles them into a single markdown payload for that
agent. Its Python compiler stitches those files together; the installer (`install.sh`)
fetches a tarball from GitHub over HTTPS and unpacks it into `~/.claude/skills/cook/`.
Optional telemetry is written to a local, gitignored JSON store and is off by default.

The installer also writes outside its own install directory, which is worth knowing
about. It creates a symlink at `~/.agents/skills/cook` pointing back to the install, so
Codex finds the same tree — if a real directory already exists there, it is reported and
left alone, never replaced. When `~/.codex` exists, the installer also rewrites a marked
block in `~/.codex/config.toml` that hides cook's per-domain shelves from Codex's skill
picker; only the content between cook's own markers is touched. Set `COOK_NO_CODEX=1` to
skip both steps.

There is no server, no network listener, and no credential handling. The realistic
surface is what the installer fetches, unpacks and links, what the compiler reads and
writes, and the local cache and telemetry files.

## Disclosure

Report privately, and please hold off on publishing until a fix is out. Fixed issues are
published as a GitHub advisory with credit to the reporter.
