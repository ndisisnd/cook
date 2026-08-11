# Releases

What's new for you, release by release.

## v1.0.0 — 2026-08-11

> cook gives your coding agent the right standards at the right moment. You describe the task; cook works out which languages, frameworks and concerns it touches, and hands your agent only the rules that apply — instead of a wall of guidance it has to wade through. This first release covers twelve technology areas plus a global set of rules that applies to any codebase, and works in both Claude Code and the OpenAI Codex CLI from a single install.

### ✨ New

- Ask your agent to run cook before any coding task and it loads the standards that match what you're actually changing — no manual setup, no choosing rules yourself.
- Standards for twelve areas: React, Next.js, TypeScript, Node.js, Swift, macOS, Flutter, Dart, CSS, GraphQL, SQL databases and Supabase — plus a global set of cross-cutting rules covering architecture, API design, security, authentication, error handling, performance, debugging and CI.
- Name what you want directly when you already know: ask for a specific area, or narrow to a single topic within it, and cook loads exactly that and nothing more.
- Describe a task in plain words instead of flags, and cook picks the relevant rules for you.
- Install in one line, with nothing to clone or configure. You can also install from a local copy when you're offline.
- Use the same install with the OpenAI Codex CLI as well as Claude Code. One copy on your machine serves both, so there's nothing to keep in sync and no second setup to maintain.
- Turn on a private, local record of which standards fire most often, so you can see what your work actually leans on. It's off by default and never leaves your machine.

### 📈 Improved

- cook remembers what it worked out for a project, so repeat runs on unchanged work return instantly instead of re-deriving everything.
- The compiled standards are written to a file rather than passed through your agent's context, which keeps long sessions from filling up with rules your agent has already read.
- Ask for a topic within an area and you get that topic, not the whole area — noticeably less to read for narrowly scoped work.
- Task descriptions are matched more precisely, so a passing mention of a common word no longer pulls in a whole set of unrelated rules.
- When you check what cook has been loading, the most useful ranking now leads.

### 🐛 Fixed

- Installing no longer trips GitHub's rate limit partway through and leaves you with a half-installed copy.
- Installing survives brief delays in GitHub's content delivery, instead of failing when you reinstall right after a push.
- Files you've changed but not yet staged are now recognised correctly, so cook routes to the right standards for work in progress.

### 🔒 Security

- cook only ever reads standards from inside its own installation. A rule pointing somewhere outside it is skipped and reported rather than quietly loaded.
