# Releases

What's new for you, release by release.

## v1.1.0 — 2026-10-23

> cook now covers iPhone and iPad apps, and it ships a full set of security rules, including a new one for encryption. The standards were brought up to date with the tools and versions current in October 2026, and several are much shorter, so your agent reads less to get the same guidance. This release takes cook to thirteen technology areas and nine cross-cutting concerns.

### ✨ New

- Standards for iPhone and iPad apps: app lifecycle, navigation, accessibility, background work, privacy, account deletion and App Store signing. SwiftUI work no longer pulls in Mac-only rules, and Mac work no longer pulls in iPhone rules.
- A new cryptography concern covers encryption choices, random numbers, key rotation and TLS. Ask for it directly, or let cook load it when your task mentions encryption.
- Security rules that used to live in a private library now ship with cook. They were checked against OWASP, NIST and IETF guidance, and 18 factual errors were fixed along the way.
- cook now flags standards that have not been reviewed recently, so stale rules show up before they mislead your agent.

### 📈 Improved

- Standards are refreshed to October 2026 versions: TypeScript 6, Node 24 LTS, Swift 6.2, macOS 26 with Xcode 27, PostgreSQL 16 to 18, Tailwind v4, OWASP Top 10 2025, React 19.3 and Next.js 16.4.
- Payloads are smaller. Measured on the rules your agent reads: React is 41% smaller, Next.js 32%, Swift 25% and TypeScript 19%. The whole library is 2% smaller even with the new iOS and security rules added, and 8% smaller without them.
- Rules that repeated each other across shelves now live in one place, so your agent no longer reads the same advice twice.

### 🐛 Fixed

- Flutter and React Native projects now load iOS rules for their iOS files, where before they loaded macOS rules.
- Rules that contradicted each other or recommended out-of-date settings were corrected, including unsafe database migration steps and end-of-life Node versions.

### Not in this release

- GraphQL, Supabase, Flutter and Dart have not been refreshed yet. They are planned for next releases.

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
