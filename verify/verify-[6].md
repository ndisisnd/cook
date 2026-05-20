---
status: pending
---

# Verification Run [6] — Cook Skill Refactor: Keyword-Driven Orchestrator

## 1. What Will Be Changed

### Problem before

`cook/SKILL.md` is a two-path if/else router: it sends the agent to either `review/SKILL.md` or `global/SKILL.md` and then tells it to follow hardcoded domain paths. There is no keyword extraction, no programmatic index lookup, and no structured data return to the calling agent.

The mode-detection logic (how to decide `--frontend` vs `--backend` vs `--full-stack`) lives in `standards/global/_INDEX.md`, which means it is buried inside a domain skill rather than controlled by the top-level router.

The mode-specific rules (`--frontend`, `--backend`, `--full-stack`) are inline in `standards/global/SKILL.md`, which means every global skill invocation loads all three modes even when only one applies.

### After

`cook/SKILL.md` becomes a keyword-driven orchestrator with a defined step-by-step protocol:

1. Receive a code summary from the invoking agent
2. Extract keywords from the summary (file patterns, tech stack, domain terms, patterns)
3. Detect mode (`--frontend` / `--backend` / `--full-stack`) from keywords and file patterns — this logic moves here from `global/_INDEX.md`
4. Detect domain (flutter / nextjs / react / database / graphql / typescript / dart) from keywords
5. Load the matching domain `_INDEX.md` and match keywords against its file-pattern and keyword columns
6. Load only the matched sub-skills
7. Load `global/refs/<mode>.md` for the detected mode
8. Compile all ref content and return it to the calling agent

The mode routing table is removed from `global/_INDEX.md` and the `--frontend`, `--backend`, `--full-stack` inline sections are removed from `global/SKILL.md` and extracted to three new ref files.

---

## 2. Files Touched

| File | Action |
|---|---|
| `cook/SKILL.md` | Rewrite — full orchestrator protocol with keyword extraction, mode detection, domain routing, and structured return |
| `standards/global/_INDEX.md` | Edit — remove mode routing table; keep only ref-loading guidance |
| `standards/global/SKILL.md` | Edit — remove P1 mode-specific sections; keep P0 universal rules only; update References section to point to the three new mode refs |
| `standards/global/refs/frontend.md` | Create — extracted from `global/SKILL.md` P1 `--frontend` section |
| `standards/global/refs/backend.md` | Create — extracted from `global/SKILL.md` P1 `--backend` section |
| `standards/global/refs/full-stack.md` | Create — extracted from `global/SKILL.md` P1 `--full-stack` section |

No changes to any domain skill files (`flutter/`, `nextjs/`, `react/`, etc.).

---

## 3. Expected Output When Running the Skill

### Scenario A — Frontend component work in Next.js

Input summary: "add a user profile page using App Router, Tailwind, and zustand for local state"

Cook extracts keywords: `App Router`, `Tailwind`, `zustand`, `page.tsx`
Mode detected: `--frontend`
Domain detected: nextjs
Matched skills from `nextjs/_INDEX.md`: `nextjs-app-router`, `nextjs-styling`, `nextjs-state-management`
Mode ref loaded: `global/refs/frontend.md`

Returns: global P0 rules + frontend mode ref + nextjs-app-router SKILL.md + nextjs-styling SKILL.md + nextjs-state-management SKILL.md

### Scenario B — Backend API work

Input summary: "add a paginated list endpoint for orders, scoped by tenant, using a repository pattern"

Cook extracts keywords: `endpoint`, `paginated`, `tenant`, `repository`, `api`
Mode detected: `--backend`
Domain detected: global (no framework-specific files)
Matched skills: none from domain index (global only)
Mode ref loaded: `global/refs/backend.md`

Returns: global P0 rules + backend mode ref

### Scenario C — Full-stack feature

Input summary: "connect the order list UI to the new orders API, validate on both client and server"

Cook extracts keywords: `UI`, `API`, `validate`, `client`, `server`
Mode detected: `--full-stack`
Domain detected: nextjs (inferred from existing codebase context)
Matched skills from `nextjs/_INDEX.md`: `nextjs-server-actions`, `nextjs-data-fetching`
Mode ref loaded: `global/refs/full-stack.md`

Returns: global P0 rules + full-stack mode ref + matched nextjs sub-skills

### Scenario D — Flutter state management work

Input summary: "add a BlocProvider for the cart feature using flutter_bloc"

Cook extracts keywords: `BlocProvider`, `flutter_bloc`, `_bloc.dart`
Mode detected: `--frontend`
Domain detected: flutter
Matched skills from `flutter/_INDEX.md`: `flutter-bloc-state-management`
Mode ref loaded: `global/refs/frontend.md`

Returns: global P0 rules + frontend mode ref + flutter-bloc-state-management SKILL.md

### Scenario E — Code review

Input summary: "review this PR"

Cook detects review intent from keywords: `review`
Routes to `standards/review/SKILL.md` (unchanged from current behaviour)

---

## 4. Success Criteria

### Structure
- [ ] `cook/SKILL.md` exists and has a step-by-step protocol section
- [ ] `standards/global/refs/frontend.md` exists and is non-empty
- [ ] `standards/global/refs/backend.md` exists and is non-empty
- [ ] `standards/global/refs/full-stack.md` exists and is non-empty
- [ ] `standards/global/SKILL.md` no longer contains `### --frontend`, `### --backend`, or `### --full-stack` headings
- [ ] `standards/global/_INDEX.md` no longer contains a Mode Routing or File Match table for frontend/backend/full-stack

### `cook/SKILL.md` protocol
- [ ] Has a named step for receiving the code summary from the caller
- [ ] Has a named step for keyword extraction
- [ ] Has a named step for mode detection with an explicit rule table mapping file patterns and keywords to `--frontend`, `--backend`, or `--full-stack`
- [ ] Has a named step for domain detection mapping keywords/file patterns to the correct domain `_INDEX.md`
- [ ] Has a named step for loading and searching the matched domain `_INDEX.md`
- [ ] Has a named step for compiling all matched refs and returning them to the calling agent
- [ ] Review routing is still present (summary with `review` intent → `standards/review/SKILL.md`)

### `cook/SKILL.md` mode detection table
- [ ] `--frontend` triggers: file patterns include `*.tsx`, `*.jsx`, `**/components/**`, `**/pages/**`, `**/app/**`, `**/hooks/**`; keywords include `frontend`, `ui`, `form`, `state`, `rendering`, `client`, `browser`
- [ ] `--backend` triggers: file patterns include `**/controllers/**`, `**/routes/**`, `**/handlers/**`, `**/services/**`; keywords include `backend`, `api`, `endpoint`, `auth`, `database`, `query`, `persistence`
- [ ] `--full-stack` triggers: keywords include `full-stack`, `full stack`, `end-to-end`, `connect ui to api`

### `cook/SKILL.md` domain detection table
- [ ] `flutter` → `standards/flutter/_INDEX.md` when keywords contain Flutter terms or files match `**/*.dart`
- [ ] `nextjs` → `standards/nextjs/_INDEX.md` when keywords contain Next.js terms or files match Next.js patterns
- [ ] `react` → `standards/react/_INDEX.md` when keywords contain React terms and no Next.js signals
- [ ] `database` → `standards/database/_INDEX.md` when keywords contain sql, schema, migration, redis, postgres
- [ ] `graphql` → `standards/graphql/_INDEX.md` when keywords contain GraphQL, resolver, schema, query
- [ ] `typescript` → `standards/typescript/SKILL.md` when files match `*.ts` and no framework signals
- [ ] `dart` → `standards/dart/_INDEX.md` when keywords contain Dart terms

### `global/refs/frontend.md`
- [ ] Contains component structure rules (one component per file, lift state minimally, extract business logic to hooks)
- [ ] Contains UI security rules (no `dangerouslySetInnerHTML` without sanitization, no auth tokens in `localStorage`, no unsanitized URL construction)
- [ ] Contains performance rules (avoid unnecessary re-renders, parallel fetch, virtualize long lists)
- [ ] Does NOT contain backend or full-stack rules

### `global/refs/backend.md`
- [ ] Contains API semantics rules (`GET` read-only, correct status codes, paginate all list endpoints)
- [ ] Contains error architecture rules (domain layer, API layer, infrastructure layer separation)
- [ ] Contains auth and ownership rules (scope by owner/tenant, require auth by default, role guards)
- [ ] Contains performance rules (no N+1, index foreign keys and filter columns)
- [ ] Does NOT contain frontend or full-stack rules

### `global/refs/full-stack.md`
- [ ] States to apply both frontend and backend rules
- [ ] Contains cross-layer rules: no business logic leaking from backend to frontend components
- [ ] Contains validation rule: validate once at server boundary, mirror in UI for UX only
- [ ] Contains API contract rule: field removal, rename, or status code change requires a version bump
- [ ] Does NOT duplicate the frontend or backend rules inline — references those refs instead

### `global/SKILL.md` after edit
- [ ] P0 universal rules section is unchanged
- [ ] P1 section is removed (no `--frontend`, `--backend`, `--full-stack` subsections)
- [ ] References section is updated to list `refs/frontend.md`, `refs/backend.md`, `refs/full-stack.md` with conditional load descriptions
- [ ] Anti-patterns section is unchanged

### `global/_INDEX.md` after edit
- [ ] Mode Routing section is removed
- [ ] File Match table for global frontend/backend/full-stack is removed
- [ ] Ref loading table is still present
- [ ] Notes section updated to reflect that mode selection now happens in `cook/SKILL.md`

### No unintended changes
- [ ] No files under `standards/flutter/` were modified
- [ ] No files under `standards/nextjs/` were modified
- [ ] No files under `standards/react/` were modified
- [ ] No files under `standards/database/` were modified
- [ ] No files under `standards/graphql/` were modified
- [ ] No files under `standards/typescript/` were modified
- [ ] No files under `standards/dart/` were modified
- [ ] `standards/review/SKILL.md` was not modified

---

## 5. Executable Steps for the Implementing Agent

### Step 1 — Read source material

Read all of the following files before writing anything:

- `cook/SKILL.md`
- `standards/global/SKILL.md`
- `standards/global/_INDEX.md`
- `standards/flutter/_INDEX.md`
- `standards/nextjs/_INDEX.md`
- `standards/react/_INDEX.md`
- `standards/database/_INDEX.md`
- `standards/graphql/_INDEX.md`
- `standards/typescript/SKILL.md`
- `standards/dart/_INDEX.md`

These are the source of truth for every keyword and file-pattern rule you will consolidate into the new `cook/SKILL.md`.

### Step 2 — Create `standards/global/refs/frontend.md`

Extract the full `### --frontend` section from `standards/global/SKILL.md` (Component structure, UI security, Performance subsections). Write it to `standards/global/refs/frontend.md`. Do not add or remove rules — copy exactly.

### Step 3 — Create `standards/global/refs/backend.md`

Extract the full `### --backend` section from `standards/global/SKILL.md` (API semantics, Error architecture, Auth and ownership, Performance subsections). Write it to `standards/global/refs/backend.md`. Do not add or remove rules — copy exactly.

### Step 4 — Create `standards/global/refs/full-stack.md`

Extract the full `### --full-stack` section from `standards/global/SKILL.md`. Write it to `standards/global/refs/full-stack.md`. The file should note that the frontend and backend rules also apply — do not inline them, reference the two sibling refs.

### Step 5 — Edit `standards/global/SKILL.md`

Remove the entire `## Priority: P1 — Mode-Specific Rules` section (all three mode subsections). In the `## References` section, add entries for `refs/frontend.md`, `refs/backend.md`, and `refs/full-stack.md` with load-when descriptions. Leave P0, Anti-patterns, and all other existing refs untouched.

### Step 6 — Edit `standards/global/_INDEX.md`

Remove the `## File Match` table and `## Mode Routing` section. Keep the `## Ref Loading` table and `## Notes`. Update the Notes to say mode selection now happens in `cook/SKILL.md`.

### Step 7 — Rewrite `cook/SKILL.md`

Replace the current router with a full orchestrator protocol. The new file must contain:

**Frontmatter** — keep existing `name`, `description`, `metadata` fields. Update description to reflect orchestrator role.

**Step-by-step protocol:**

1. **Receive summary** — accept the code task summary passed by the invoking agent.
2. **Extract keywords** — parse the summary for: file paths and extensions, framework or library names, domain terms (api, endpoint, auth, BlocProvider, etc.), and patterns (pagination, navigation, state, etc.).
3. **Detect mode** — match extracted keywords against the mode detection table (inline this table, moved from `global/_INDEX.md`):
   - `--frontend`: file patterns `*.tsx`, `*.jsx`, `**/components/**`, `**/pages/**`, `**/app/**`, `**/hooks/**`; keywords `frontend`, `ui`, `form`, `state`, `rendering`, `client`, `browser`
   - `--backend`: file patterns `**/controllers/**`, `**/routes/**`, `**/handlers/**`, `**/services/**`, `**/repositories/**`, `**/api/**`; keywords `backend`, `api`, `endpoint`, `auth`, `database`, `query`, `persistence`
   - `--full-stack`: keywords `full-stack`, `full stack`, `end-to-end`, `connect ui to api`
4. **Detect domain** — map keywords to domain `_INDEX.md`:
   - Flutter → `standards/flutter/_INDEX.md` (`.dart` files, Flutter/Dart terms)
   - Next.js → `standards/nextjs/_INDEX.md` (`app/`, `pages/`, Next.js terms)
   - React → `standards/react/_INDEX.md` (React terms, no Next.js signals)
   - Database → `standards/database/_INDEX.md` (sql, schema, migration, redis, postgres)
   - GraphQL → `standards/graphql/_INDEX.md` (GraphQL, resolver, schema, query)
   - TypeScript → `standards/typescript/SKILL.md` (`.ts` files, no framework signals)
   - Dart → `standards/dart/_INDEX.md` (`.dart` files, non-Flutter Dart terms)
5. **Load domain index** — read the matched domain `_INDEX.md`. Match extracted keywords against the file-pattern and keyword columns. Select every row that matches at least one signal.
6. **Load matched sub-skills** — for each matched row, load the corresponding `SKILL.md`.
7. **Compile and return** — load `standards/global/SKILL.md` (P0 universal rules) and `standards/global/refs/<mode>.md` (detected mode). Assemble all loaded content into a single standards payload. Return it to the invoking agent.

**Review routing** — preserve: if the summary signals `review`, `audit`, `check for bugs`, or `look for regressions`, skip Steps 2–7 and load `standards/review/SKILL.md` instead.

### Step 8 — Verify structure

After all edits, confirm:

```
cook/SKILL.md                         — exists, has 7-step protocol
standards/global/refs/frontend.md     — exists, non-empty
standards/global/refs/backend.md      — exists, non-empty
standards/global/refs/full-stack.md   — exists, non-empty
standards/global/SKILL.md             — P1 section removed, refs updated
standards/global/_INDEX.md            — mode routing removed
```

Confirm no files outside these six paths were modified.

### Step 9 — Spot-check content integrity

1. Read `standards/global/refs/frontend.md` and confirm it contains the component structure, UI security, and performance rules that were in `global/SKILL.md` P1 `--frontend`. Nothing added, nothing missing.
2. Read `standards/global/refs/backend.md` and confirm it contains API semantics, error architecture, auth/ownership, and performance rules from P1 `--backend`. Nothing added, nothing missing.
3. Read `standards/global/refs/full-stack.md` and confirm it contains the cross-layer contract rules from P1 `--full-stack`.
4. Read `standards/global/SKILL.md` and confirm the P0 section is byte-for-byte the same as before (no rules were lost or changed, only the P1 section was removed).
5. Read `cook/SKILL.md` and confirm the mode detection table contains every keyword and file-pattern that was in `global/_INDEX.md`'s `## File Match` table — no entries silently dropped.
