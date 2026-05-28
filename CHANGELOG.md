# Changelog

All notable changes to this project are documented here, newest first.

---

## [pending] — 2026-05-28 · `--global` shelf flag and `--domain:ref` sub-ref flags

**feat(cook): add `--global` and sub-ref `--<domain>:<ref>` flag modes for granular explicit loading.**

- `--global` loads the complete global shelf: `standards/global/SKILL.md` + all 8 concern refs. It is the only explicit-mode path that opts back into the P0 floor without triggering auto-detection.
- Sub-ref flags (`--react:hooks`, `--react:state-management`) load a single ref file from a domain shelf without loading the domain SKILL.md. Combine with the domain flag (`--react --react:hooks`) to load both. Sub-ref flags are valid for all domain shelves; the ref is validated against actual files on disk at runtime via `valid_sub_flags()`.
- `vocab/tag-vocabulary.json`: added `global` tag with `routes_to: ["shelf:global"]`; updated `_note` to document the three prefix categories (`concern:`, `domain:`, `shelf:`) and the sub-ref syntax.
- `scripts/cook_cache.py`: added `valid_domain_flags()` (returns domain-only flag names) and `valid_sub_flags(domain)` (enumerates ref stems from disk); updated flag validation in `cmd_lookup` to accept compound `domain:ref` tokens with domain and ref-stem checks; updated docstring.
- `SKILL.md`: Step 0 documents two flag forms (simple vs sub-ref); Step 0b adds `--global` routing and sub-ref routing rules; Step 6 path-list bullet updated.
- `README.md`: flags section gains Shelf and Sub-ref categories; examples table extended with `--global`, `--react:hooks`, and `--react --react:hooks` rows.
- `ARCHITECTURE.md`: Args section updated with simple-flag, sub-ref-flag, and `--global` descriptions.

---

## [pending] — 2026-05-28 · Explicit args support (`--flag` / prose)

**feat(cook): add explicit override modes to `/cook` — flags pin concerns/domains; prose triggers LLM-guided library search.**

Three invocation modes are now supported:

- **`auto`** (no args, existing behaviour): auto-detects the change surface from git + manifests, loads global P0 + matched concerns + matched domains. Unchanged from the pre-feature protocol.
- **`explicit-flags`** (`/cook --security`, `/cook --react --nextjs`, etc.): bypasses auto-detection and P0. Each flag loads exactly the named shelf — concern flags load `standards/global/refs/<concern>.md`; domain flags load `standards/<domain>/SKILL.md` + all `standards/<domain>/refs/*`. Cache participates (fingerprint includes flags). Valid flag names are derived at runtime from `vocab/tag-vocabulary.json` `routes_to`; an unknown flag exits non-zero with usage.
- **`explicit-prose`** (`/cook refactor the OAuth callback`, `/cook --react fix re-renders`): the LLM picks refs from the relevant `_INDEX.md` tables. With flags, the LLM narrows within those shelves; without flags, the LLM scans the whole library. No cache read or write — prose is intentionally uncacheable. P0 is not loaded.

**P0 trade-off:** any explicit flag or prose argument skips the global P0 floor. The contract is "load exactly what I named." Default `/cook` keeps the floor.

- `SKILL.md`: new Step 0 (arg parsing, mode branch table, Steps 0a–0c). Step 2 notes P0 is default-protocol-only. Step 5 notes it is skipped on `explicit-prose`. Step 6 path-list gains an Explicit path bullet.
- `scripts/cook_cache.py`: new `valid_flags()` (runtime-computed from vocab); `fingerprint()` accepts optional `flags` (empty/absent → byte-identical basis, no cache flush); `cmd_lookup` gains `--flag`/`--prose` with three-mode logic; `cmd_write` records `flags` and `mode` on entries.
- `ARCHITECTURE.md`: new **Args** section with mode table and cache-key extension description.
- `README.md`: new **Usage** subsection with flag reference, six worked examples, and P0 trade-off note.
- `vocab/tag-vocabulary.json`: `_note` updated — `routes_to` targets double as the public `--flag` namespace; renaming one is a breaking CLI change.
- `verify/check-cook-args.py` (new): 25-assertion test suite (D1–D7) covering flag namespace closure, fingerprint backwards-compat, fallback suppression, prose skip-cache, unknown-flag error, cache round-trip, and two-domain composition.

---

## [pending] — 2026-05-25 · Remove review standard

**refactor(cook): remove `standards/review/` and all live routing references to it.**

- `SKILL.md`: removed Step 2 (review-code intent fast path); renumbered Steps 3–7 → 2–6; updated all internal cross-references. Removed `review` from the keywords list and updated the description.
- `ARCHITECTURE.md`: removed Step 2 section, removed `review/` from the directory tree, removed the `review` row from the Skills table, and removed the `review` Refs subsection. Updated Step 1 hit-path cross-reference.
- `README.md`: removed the Review row from the Available Standards table; rewrote the Step 3 description to remove review-specific language.
- `vocab/intent-vocabulary.json`: removed the `review-code` intent entry; 10 intents remain.
- `standards/global/_INDEX.md`: removed the Notes line redirecting to `standards/review/SKILL.md`.
- `chef/eval_set.json`: adapted cases 7 and 11 from `review-code` to `harden-security`; stripped `standards/review/SKILL.md` from `skills_include`; rewrote grading checks; added `"note"` fields recording the original test purpose.
- `chef/eval_benchmark.json`: updated `notes` fields for cases 7 and 11 to record the adaptation.
- `chef/eval_issues.json`: updated issue-010 to remove the review-specific example.
- `verify/done/check-vocab-parity.py`: removed the `EXCLUDE = {"review"}` guard (no `standards/review/_INDEX.md` exists to exclude); fixed `ROOT` path computation (was off by one level after script was moved to `verify/done/`).
- All verification checks pass: 0 `review-code` intent entries in eval set, 10 intents in vocab, 531/531 index keywords covered, 77/77 route targets resolve.
- `install.sh`: removed stale `standards/review/` entries; added missing `standards/nodejs/` and `standards/supabase/` to match disk.

---

## [8c7763b] — 2026-05-25 · Concern-ref enumeration and path-traversal guard

**fix(cook): enumerate all 8 fallback concern refs explicitly; add path-traversal bounds check in compiler.**

- `SKILL.md` Step 4 now lists all 8 `standards/global/refs/` concern files (`architecture.md`, `api-design.md`, `error-handling.md`, `security.md`, `auth.md`, `performance.md`, `debug.md`, `cicd.md`) as the single authoritative enumeration. The previous list omitted `auth.md` and `cicd.md`, causing partial loads on the fallback/greedy path (the only recorded eval failure, case 9).
- Step 1b and Step 7 fallback branches now reference "all 8 concern refs enumerated in Step 4" instead of the ambiguous "full/broad concern set."
- `scripts/cook_compile.py` now resolves each skill path and checks it is within `cook_root` before reading. A path that escapes the root (e.g. `../../outside.md`) is added to `degraded` and skipped — previously such a path would be read and its content silently included in the payload if the file existed.

---

## [pending] — 2026-05-24 · Node.js runtime domain

**feat(standards): add nodejs runtime domain (event loop, streams, async rejection lifecycle, process signals, supply chain).**

- Added `standards/nodejs/` — a new `domain:nodejs` covering Node runtime mechanics only. It co-loads with `typescript` for `.ts` server entries and links to neighbouring refs instead of restating API, auth, security, performance, CI, or database rules.
- Added four refs: `refs/runtime-safety.md` (event loop, streams/backpressure, worker threads, Buffer safety, graceful shutdown), `refs/async-errors.md` (promise rejection lifecycle, callback/timer/event-boundary throws, global handlers, timeouts), `refs/tooling.md` (runtime/package-manager pinning, frozen installs, env validation, structured logging), and `refs/testing.md` (Node service/CLI/integration/network-boundary tests).
- Routing: added a `nodejs` tag to `vocab/tag-vocabulary.json` routing to `domain:nodejs`, added `standards/nodejs/_INDEX.md`, and added precise cook triggers (`**/*.cjs`, `server.{ts,js,mjs,cjs}`, `app.{ts,js,mjs,cjs}`, `**/*.server.{ts,js,mjs,cjs}`) without broad `.mjs`, routes, or controllers triggers.
- Resolver: patched `scripts/cook_cache.py` so `.cjs` resolves `nodejs` by extension, while `.ts`/`.js`/`.mjs` require a server-framework manifest plus a server entry/path and no frontend path. TypeScript server entries add `nodejs` alongside `typescript`, never instead of it; browser React and generic routes paths do not load `nodejs`.
- Cache: new framework/domain hints shift the fingerprint basis → one cold rebuild on first run after this change; stale checksum entries are not served as hits.
- Docs: added `nodejs` to the `ARCHITECTURE.md` standards tree, Skills table, and Refs index, and to the `README.md` Available Standards table.
- Vocab parity holds at 519/519 (`verify/check-vocab-parity.py`); route targets resolve (79/79 across 11 indexes, `scripts/check_index_routes.py`).
- Plan: `improve/standards/cook-feat-standards-nodejs.md`; acceptance: `improve/standards/cook-feat-standards-nodejs-acceptance.md`.

---

## [pending] — 2026-05-24 · Supabase platform domain

**feat(standards): add supabase platform domain (RLS, anon/service_role boundary, Postgres/Edge functions, CLI migrations).**

- Added `standards/supabase/` — a new `domain:supabase` covering the Supabase platform contract only (it co-loads on top of `database`, which keeps all generic Postgres rules). `SKILL.md` carries 13 P0 rules (7 RLS, 3 keys/client boundary, 3 Postgres/Edge function) each with a review `Signal:`, 2 signal-bearing P1 workflow rules, and 1 `P1 (design)` Realtime rule
- Added six refs: `refs/rls.md` (enable-on-create, per-operation policies, `SELECT`+`UPDATE` pairing, `WITH CHECK`, `(select auth.uid())` wrapping, `app_metadata` vs `user_metadata`, indexing predicate columns), `refs/keys-and-clients.md` (anon vs service_role boundary, public-env pitfalls, SSR admin-client separation), `refs/database-functions.md` (`SECURITY INVOKER`/`DEFINER` + `search_path = ''`), `refs/edge-functions.md` (Deno, `verify_jwt`, secrets, connection pooling), `refs/migrations.md` (CLI workflow, RLS-as-SQL, storage/Realtime policies), and `refs/checklist.md` (pre-deploy review gate). De-duplicated against `database` and `global/refs/auth.md` — bordering rules link rather than restate
- Routing: added a `supabase` tag to `vocab/tag-vocabulary.json` (25 platform aliases — `row level security`, `service_role`, `auth.uid`, `verify_jwt`, `security definer`, …) routing to `domain:supabase`. Deliberately left `rls`, `migration`, `postgres`, `index`, `transaction` on the `database` tag so the two co-load with no vocabulary theft. Added `standards/supabase/_INDEX.md` (file-pattern + keyword rows for the SKILL and all six refs), `supabase/**` to cook's `SKILL.md` `triggers.files`, and `supabase` to cook's trigger keywords
- Resolver: patched `scripts/cook_cache.py` so a `supabase/migrations/*.sql` change resolves **both** `database` and `supabase` (co-load), `supabase/functions/**` resolves `supabase`, and a manifest (`supabase/config.toml` or `@supabase/supabase-js` dep) lists `supabase` in `frameworks`. The supabase detection is a **separate second pass** after the extension chain (so the `.sql` arm can't consume the file first — the CG-1 failure mode) and is **segment-anchored** (`startswith("supabase/")` / `"/supabase/" in low`) so look-alikes like `mysupabase/x.ts` do not falsely load, while nested `src/lib/supabase/client.ts` correctly does
- Cache: new framework/domain hints shift the fingerprint basis → one cold rebuild on first run after this change (existing `routing.json` entries go stale, none served as a stale hit)
- Docs: added `supabase` to the `ARCHITECTURE.md` Skills table, `standards/` tree, and Refs index, and to the `README.md` Available Standards table
- Vocab parity holds at 502/502 (`verify/check-vocab-parity.py`); route targets resolve (74/74 across 10 indexes, `scripts/check_index_routes.py`)
- Plan: `improve/standards/cook-feat-standards-supabase.md`; acceptance: `improve/standards/cook-feat-standards-supabase-acceptance.md`

---

## [31e6810] — 2026-05-24 · One-line installer

**feat(install): add installation script and README setup guide.**

- Added `install.sh` — a `curl … | bash` installer that downloads cook's full file set (SKILL.md, vocab, scripts, and all `standards/**` skills + refs) into `~/.claude/skills/cook/`, with a `COOK_DIR` override for a custom destination; requires `curl` and `python3`
- Added a "Requirements" / setup section to `README.md` documenting the one-line install command and the `COOK_DIR` override

---

## [0151218] — 2026-05-24 · cook skill robustness improvements

**fix(cook): add error handling and clarify protocol steps.**

- Added error handling for failed script runs in the cache-lookup step — non-zero exit or unparseable JSON now treated as `miss` with `confidence: low`, continuing to Step 1c without crashing
- Clarified Step 1c to explicitly read `vocab/intent-vocabulary.json` and `vocab/tag-vocabulary.json` before classifying
- Expanded Step 2 cache-hit path to load both `standards/global/SKILL.md` and `standards/review/SKILL.md`, write the cache entry with both skill paths, and compile both via Step 7 — invoking agent now receives a compiled payload, not a bare file reference

---

## [5c11b34] — 2026-05-24 · Auth code examples + service-to-service auth

**feat(standards): add Secure Patterns examples and a Service-to-Service Auth section to auth.md.**

- Added a `## Secure Patterns` section to `standards/global/refs/auth.md` — five TypeScript good/`// Never:` snippets (token storage, argon2id hashing, JWT verification with pinned `algorithms`+`aud`/`iss`, constant-time comparison, client-credentials service token), closing the style gap with `security.md` (which already carried examples; auth.md had none)
- Added a `## Service-to-Service Auth` section — two P0 rules with `Signal:`s (mTLS / short-lived client-credentials token, never a long-lived shared static API key [API2]; receiving service verifies caller identity via mTLS cert or token `aud`+`iss`, never network reachability alone [zero-trust]) and one `P1 (design)` rule (scope/rotate service credentials, source from a secret manager)
- Extended the `auth.md` intro summary and Anti-Patterns block (static shared API keys; trusting network reachability over caller identity). OWASP intro mapping unchanged — S2S maps to API2, already listed
- Routing: added 12 service-auth aliases to `tags.auth.aliases` in `vocab/tag-vocabulary.json` (mtls/mutual tls, client credentials, service-to-service/m2m/machine-to-machine, api key, service account, workload identity, zero-trust); added five keywords (`mtls, client credentials, service-to-service, api key, service account`) to the `refs/auth.md` row in `global/_INDEX.md`; extended the `auth` References blurb in `global/SKILL.md`
- Vocab parity holds at 466/466 (`verify/check-vocab-parity.py`); route targets resolve (66/66, `scripts/check_index_routes.py`)
- Plan: `improve/standards/cook-feat-standards-1.3.md`; verify: `improve/standards/cook-feat-standards-1.3-verify.md`

---

## [5c11b34] — 2026-05-24 · Close auth coverage gaps (brute-force, JWT verification, password reset, enumeration, OAuth state, MFA, password policy)

**feat(standards): close auth coverage gaps surfaced by the security.md OWASP tables.**

- Closed the gap between what `security.md`'s OWASP tables advertise and what `auth.md` prescribes. Added P0 rules (each with a `Signal:`) to `standards/global/refs/auth.md`: brute-force/rate-limiting on auth endpoints (A04/API4), JWT signature verification — pinned algorithm, reject `alg:none`, validate `aud`/`iss` (A08/API2), OAuth `state` + exact-match `redirect_uri` (A01/API2), single-use/short-expiry password-reset tokens with session invalidation (API6), account-enumeration uniformity, and constant-time secret comparison
- Added two `P1 (design)` rules: MFA + step-up re-auth for sensitive actions, and an input-side password policy (NIST 800-63B length floor + breached-password check)
- Updated the `auth.md` intro OWASP mapping `A01/A02/A07 + API2/API5` → `A01/A02/A04/A07/A08 + API2/API4/API5/API6`; extended the Anti-Patterns block
- Reconciled `security.md`: expanded the "lives in auth.md" cross-reference note (brute-force/rate-limiting, JWT verification, password-reset now owned by auth.md) and stated the OWASP tables stay as the master detection reference — no rule duplication
- Routing: extended `tags.auth.aliases` in `vocab/tag-vocabulary.json` (mfa/2fa/multi-factor/step-up, brute force/lockout, password reset/forgot password/account recovery, password policy/breached password, redirect_uri, user enumeration, timing-safe); added six keywords (`mfa, 2fa, brute force, lockout, password reset, password policy`) to the `refs/auth.md` row in `global/_INDEX.md`; extended the `auth` References blurb in `global/SKILL.md`. Deliberately did **not** add bare `rate limit` (owned elsewhere — avoids a cross-concern collision)
- Vocab parity holds at 461/461 (`verify/check-vocab-parity.py`); route targets resolve (66/66, `scripts/check_index_routes.py`)
- Plan: `improve/standards/cook-feat-standards-1.2.md`; verify: `improve/standards/cook-feat-standards-1.2-verify.md`

---

## [24195ed] — 2026-05-24 · Add cicd cross-cutting concern; route CI workflow files in cook

**feat(standards): add cicd cross-cutting concern; route CI workflow files in cook.**

- Added `standards/global/refs/cicd.md` (`concern:cicd`) — the vendor-neutral pipeline baseline: fail-fast gating order, blocked merges on failing checks, per-job timeouts + run cancellation, PR/secret-exposure rules, secrets-from-vault, and artifact promotion; 7 rules, each carrying a `Signal:` for review mode, staged-rollout/rollback tagged `P1 (design)`
- De-duplicated the platform refs: removed the shared timeout/fail-fast/secrets rule prose from `flutter/refs/cicd.md` (kept Fastlane, `.aab`/`.ipa`, `subosito/flutter-action`, the workflow examples) and trimmed the generic CI prose from `nextjs/refs/tooling.md` (kept Docker/standalone, `.next/cache`, telemetry); both now point to the global baseline
- Routing: added a `cicd` tag (`routes_to: ["concern:cicd"]`) to `vocab/tag-vocabulary.json`; added a `refs/cicd.md` Concern Match row to `global/_INDEX.md`; listed `cicd` in `global/SKILL.md` References; noted in `flutter/_INDEX.md` that a Flutter CI task loads `domain:flutter` + `concern:cicd` together
- Cook activation: added `.github/workflows/**`, `**/*.yml`, `**/*.yaml` to cook `SKILL.md` `metadata.triggers.files` so a CI-only change in any repo (not just Flutter/Next.js) reaches cook; the broad YAML glob only governs activation — concern routing stays precise (below)
- Mechanical concern detection (`scripts/cook_cache.py`): added a `derive_concerns()` path + `CONCERN_PATTERNS` (GitHub Actions, GitLab CI, Jenkins, Fastlane, Azure, Bitbucket) kept separate from `domain_hints` (no category leak); a recognised CI file emits `concern_hints: ["cicd"]` and floors confidence to `high`; `concern_hints` added to the fingerprint basis and `SKILL.md` Step 5 notes the pre-selection
- Cache impact: adding `concern_hints` to the fingerprint basis changes every hash, so the cache cold-rebuilds once — entries re-resolve on next use, no error
- Vocab parity holds at 455/455 (`verify/check-vocab-parity.py`); route targets resolve (66/66, `scripts/check_index_routes.py`)

---

## [b571dcc] — 2026-05-24 · Add auth cross-cutting concern; move auth keywords off security

**feat(standards): add auth cross-cutting concern; move auth keywords off security.**

- Added `standards/global/refs/auth.md` (`concern:auth`) — OAuth/PKCE flows, token & session storage, CSRF, RBAC deny-by-default, and credential hashing; every P0 rule carries a detection signal, refresh-rotation/scopes tagged `P1 (design)`, OWASP A01/A02/A07/API2/API5 referenced (not restated)
- De-duplicated `security.md`: removed the `localStorage` token-storage rule and the auth-on-routes / role-guard rules (now in `auth.md`); renamed `## Auth & Ownership` → `## Ownership Scoping`; added a cross-reference to `auth.md`. `security.md` keeps injection, CORS, SSRF, XSS, the OWASP tables, and the SAST scans
- `global/SKILL.md`: kept the `localStorage` token rule as a P0 always-on baseline line; added `auth` to the References section; scoped the `security` reference blurb to non-auth topics
- Routing: added an `auth` tag (`routes_to: ["concern:auth"]`) to `vocab/tag-vocabulary.json` and moved `auth, token, jwt, session, cookie, role, csrf, SameSite` off the `security` tag (one owner per keyword); added a `refs/auth.md` Concern Match row to `global/_INDEX.md` and trimmed the moved keywords from the `security` row
- Vocab parity holds at 445/445 (`verify/check-vocab-parity.py`)
- Note: `git` from the original plan set was dropped (human-process gate, collides with `commit-this` + CHANGELOG workflow); `cicd` is Part 2, shipped separately

---

## [ce3c96e] — 2026-05-24 · Cook robustness — Phase 3 (self-heal + fallback)

**Added cache self-heal, hard-failure fallback routing, and a mechanical route-target validator (`feat/cook-robustness`).**

- Feature 7 self-heal: added `heal` subcommand to `scripts/cook_cache.py` that reconciles an entry's `degraded` flag with the compiler's fresh read result, rewriting atomically only when the set changed (clears when a file is fixed, updates when a new read fails); mechanical, no LLM, safe on the cache-hit fast path
- Component 8 hard-failure fallback: `load_routing()` now returns `(routing, corrupt)` distinguishing an unparseable cache (corrupt) from a cold miss; `lookup` emits `status: fallback` on corruption so the agent degrades to greedy routing instead of silently rebuilding
- Added `scripts/check_index_routes.py` — a mechanical CI/pre-commit validator that walks every `standards/*/_INDEX.md`, extracts each route target cook loads, and fails the build on a dangling path (catches rename-without-index-update drift)
- `SKILL.md` Step 7 updated with the `heal` reconcile call, partial-load semantics, and the corrupt-cache fallback path

---

## [8c63370] — 2026-05-24 · Cook robustness — Phase 0 + Phase 1 + Phase 2

**Added the routing vocabulary, fingerprint-first cache resolver, and mechanical compilation layer (`feat/cook-robustness`).**

- Phase 0: added `vocab/tag-vocabulary.json` (14 canonical tags routing to `domain:*`/`concern:*`, seeded from every `_INDEX.md` keyword column at full coverage parity — 432/432) and `vocab/intent-vocabulary.json` (11-label closed set)
- Phase 1: added `scripts/cook_cache.py` — a mechanical resolver (`lookup`/`write`, no LLM) that gathers signals via the T1/T2/T4/T5 cascade + extension disambiguation, builds a fingerprint from raw observable signals (no intent label), and checks the cache before any classification; cache entries carry vocab + index checksums and are written atomically
- Phase 2: added `scripts/cook_compile.py` — a mechanical compilation script (no LLM) that takes a comma-separated path list, deduplicates, buckets into Universal/Domain/Concern, strips YAML frontmatter, and concatenates with terse section headers; output is a JSON envelope `{content, degraded, metadata}`; `SKILL.md` Step 7 updated to invoke it via a single Bash call
- Added `improve/` and `.agent-skills/` to `.gitignore`

---

## [001e8ef] — 2026-05-23 · Standardise _INDEX.md format

**Closed verify-[14] by applying five formatting rules across five AUTO-GENERATED `_INDEX.md` files.**

- Rule 1: updated comment header from `frontmatter` → `frontmatters` in `database`, `react`, and `nextjs` (the em dash variant in `nextjs` was also corrected from ` - ` to ` — `)
- Rule 2: added `(auto-check against the file you are editing)` parenthetical to `## File Match` heading in `database` and `react`
- Rule 3: replaced all `->` table arrows with `→` in `nextjs`
- Rule 4: removed the `## Loading Instructions` heading line from `flutter`, `nextjs`, and `react` (blockquotes left in place)
- Rule 5: renamed `## Deprecated (pending removal)` → `## Archived` in `dart`
- `global` and `review` intentionally untouched (custom formats)

---

## [0a23e59] — 2026-05-21 · Fix root SKILL.md TypeScript row accuracy

**Closed verify-[13] by correcting two documentation inaccuracies in the root `SKILL.md` Step 6 TypeScript domain row.**

- Replaced the stale "no index" parenthetical with accurate wording: cook bypasses the auto-generated `_INDEX.md` and loads the SKILL directly
- Added an explicit inline note that `**/*.tsx` is excluded from the TypeScript domain by design — those files are covered by the React or Next.js domains

---

## [3f2cc8e] — 2026-05-21 · Harden and archive React consolidation

**Closed verify-[12] by making the consolidated React skill authoritative, hardening active refs, and archiving the deprecated `react-*` sub-skills.**

- Added current React hook guidance for full Rules of Hooks coverage, `useEffectEvent`, `useSyncExternalStore`, `useId`, `useLayoutEffect`, stale async cleanup, and compiler-era memoization
- Fixed active examples and guardrails for stable context provider values, accessible compound widgets, TanStack Virtual layout, Trusted Types/safe sinks, SSR JSON escaping, cookie/CSRF nuance, TanStack Query defaults, Redux Toolkit, Jotai, RTL async/absence/timer rules, and hooks linting
- Regenerated `standards/react/_INDEX.md` keywords/loading notes and marked old React sub-skills as archived source trace
- Moved all deprecated `standards/react/react-*` folders to `archive/react/` using `git mv`, preserving their refs and evals verbatim
- Deliberately did not carry old Zustand token persistence, client-only rate limiting as a security control, unsafe script CSP guidance, duplicate weak examples, or stale missing-ref links into active refs

---

## [5005e0f] — 2026-05-21 · React refs: improve examples and cross-cutting concerns

**Modernized React ref examples, added missing cross-cutting guidance, and archived verify-[11] to open verify-[12].**

- `refs/component-patterns.md` — replaced the Compound Component example (Select → Accordion) with a factory-function context guard, added `event.preventDefault()` to the uncontrolled form example, added a Boolean Props section warning against impossible-state flag combinations and `&&`-with-zero renders
- `refs/performance.md` — added `useDeferredValue` example for urgent-vs-deferred inputs, `content-visibility: auto` CSS tip for large off-screen sections, and an RSC `cache()` deduplication pattern for server reads
- `refs/security.md` — added explicit `eval()`/`new Function` prohibition, added an Input Validation Boundary section (client-side validation is UX only; validate on the server), added `Permissions-Policy` header to the CSP example
- `refs/state-management.md` — added Jotai to the state-tool decision table, added provider memoization pattern (`useMemo`/`useCallback` on Context value), added rule against persisting tokens or secrets in Zustand/Redux/`localStorage`
- `refs/testing.md` — added shallow-rendering prohibition and real-provider guidance, added a Mocking Heavy Dependencies section with a framer-motion stub example
- Archived `verify/verify-[11.1].md` → `verify/done/` and created `verify/verify-[12].md`

---

## [87cc89c] — 2026-05-21 · Fix Next.js consolidation verification gaps

**Closed the verify-[11.1] follow-up gaps in the consolidated Next.js standard without changing archived source folders.**

- Replaced a server-side own-API cache example with direct DAL/database access using cache tags
- Updated App Router examples to use Next 15 async `params` handling
- Restored dropped source guidance for Auth.js/Clerk selection, `dynamicParams`, route colocation, Pages Router API status codes, and DAL error handling
- Documented `X-XSS-Protection` as legacy source guidance and kept CSP/output escaping as the active recommendation
- Kept the root cook router wording that loads matched domain skills plus refs because reverting it would reintroduce stale sub-skill routing after the Next.js consolidation

---

## [67ab48b] — 2026-05-21 · Consolidate nextjs domain into single-skill structure

**Collapsed 18 Next.js sub-skill folders into one `SKILL.md` + 13 topic refs, matching the single-skill domain shape used by Flutter, React, Dart, TypeScript, Global, Database, and GraphQL. All superseded files are preserved in `archive/nextjs/` for review.**

- Created `standards/nextjs/SKILL.md` with Router Decision guidance, P0 rules for RSC boundaries, data fetching/access, App Router conventions, and security/auth, plus P1 rules for rendering/caching and Server Actions
- Created 13 flat refs under `standards/nextjs/refs/`: `app-router`, `pages-router`, `server-components`, `data-fetching`, `rendering-and-caching`, `server-actions`, `security`, `state-management`, `styling-and-optimization`, `testing`, `architecture`, `i18n`, `tooling`
- Merged overlapping domains: authentication + security, data-access-layer + data-fetching, rendering + caching, styling + optimization, and upgrade + tooling
- Carried forward the high-risk orphan/shared refs: `data-access-layer/refs/patterns.md`, `rendering/refs/SUSPENSE_BAILOUT.md`, `pages-router/refs/feature-sliced-design-pages.md`, and `architecture/refs/RSC_BOUNDARIES.md` as the single `server-components` boundary home
- Modernized examples where the source already pointed to Next 15/16 behavior: async request APIs, Cache Components / `'use cache'`, `cacheLife()`, `useActionState`, and direct service/DAL calls instead of internal API fetches
- Regenerated `standards/nextjs/_INDEX.md` to the AUTO-GENERATED format with File Match, Loading Instructions, and archived source trace
- Moved all 18 `nextjs-<name>/` folders to `archive/nextjs/` using `git mv`, preserving `SKILL.md`, `refs/`, and `evals/` contents verbatim

---

## [8f4c60c] — 2026-05-21 · Refine React consolidation audit

**Validated the verify-[10] React ref extraction against the legacy `react-*` sources and tightened the active refs where the migration introduced ambiguity or internal conflicts.**

- `SKILL.md` — softened arbitrary component-size, one-component, and prop-drilling rules into responsibility-based guidance while preserving the original intent
- `refs/component-patterns.md` — replaced a `key={i}` render-props example with an explicit `getKey` contract so it no longer conflicts with the stable-key rule
- `refs/hooks.md` — tightened `useLocalStorage`, `useWindowSize`, `useIntersectionObserver`, and `usePrevious` examples for latest-state updates, hydration safety, memoized options, and clearer typing
- `refs/security.md` — made the safe-link URL validation example exception-safe and SSR-safe
- `refs/tooling.md` — clarified the `why-did-you-render` snippet as a Vite example and used `import.meta.env.DEV`

---

## [8f4c60c] — 2026-05-21 · React ref-extraction gap fix (verify-[10])

**Closed the source-coverage gaps the verify-[10] audit found in the React consolidation, satisfying verify-[8] §3 before the deprecated `react-*/` folders are archived. All changes are additive to the active React skill.**

- Created `standards/react/refs/hooks.md` — a 7th ref with the custom-hooks library extracted from `react-hooks/refs/REFERENCE.md`, rewritten as typed TypeScript: `useLocalStorage`, `useDebounce`, `useWindowSize`, `useOnClickOutside`, `useIntersectionObserver`, `usePrevious`, `useToggle`. Each carries its correctness note (cleanup, exhaustive deps, SSR-safe access) (10-A · HIGH)
- `SKILL.md` — appended a `hooks` entry to the References list
- `refs/performance.md` — added a "Native Image Lazy-Loading" note (`loading="lazy"`, `decoding="async"`) in the Reduce Bundle Size section, deferring `next/image` to the nextjs domain (10-C · LOW)
- `_INDEX.md` — added a `react → hooks ref` File Match row and a Loading Instruction line for the new ref
- Documented deliberate drop (10-B): `createRateLimiter` ("Rate Limiting on Client") from `react-security/refs/REFERENCE.md` is **not** carried over — client-side rate limiting is not an enforceable security control (trivially bypassed; the server owns rate limits) and would imply false assurance in a security ref

---

## [d01640c] — 2026-05-21 · Flutter refs: resolve conflicts and fill gaps

**Fixed two critical conflicts and three gap/cross-reference issues across `standards/flutter/refs/`. No content deleted; all changes are additive edits or priority demotions.**

- `refs/navigation.md` — Added "Router Decision Rule" table at top; demoted GetX Navigation from P0 to P1 (HIGH), resolving the dual-P0 conflict with go_router
- `refs/state-management.md` — Renamed BLoC state template headings (Union ✅ PREFERRED, Flat ⚠️ LIMITED USE, Equatable ⚠️ LEGACY); inserted "Which to use" guidance block between Union and Flat sections
- `refs/architecture.md` — Added "Which Architecture to Use" decision table at top with 5 criteria and an explicit default ("Feature-Based for new projects")
- `refs/design-system.md` — Added idiomatic `Row(spacing:)` note to Spacing section with ✅/⚠️ examples and cross-reference to SKILL.md § P1 Idiomatic Flutter
- `refs/security.md` — Added `SecurityModule` DI snippet after raw `FlutterSecureStorage()` example; added cross-reference to `refs/dependency-injection.md § Third-Party Modules`
- `refs/error-handling.md` — Added scoping note to Repository Error Mapping section pointing to `refs/networking.md § Token Refresh Pattern` for global HTTP concerns

---

## [8995082] — 2026-05-21 · Consolidate flutter domain into single-skill structure

**Collapsed 22 flutter sub-skill folders into one `SKILL.md` + 13 topic refs, matching the dart/graphql exemplar shape. All superseded files are preserved in `archive/flutter/` for review.**

- Created `standards/flutter/SKILL.md` with always-on P0 rules (design system, error handling) and P1 rules (widgets, idiomatic Flutter, performance), plus a References section listing all 13 refs
- Created 13 flat refs under `standards/flutter/refs/`: `state-management`, `navigation`, `architecture`, `networking`, `error-handling`, `dependency-injection`, `design-system`, `localization`, `notifications`, `security`, `concurrency`, `cicd`, `testing`
- Merged conflicting go_router skills (`flutter-navigation` P1 + `flutter-go-router-navigation` P0) into a single unified go_router section in `refs/navigation.md`
- Carried forward 3 previously orphaned refs: `dls-modular-pattern.md` and `monolithic-pattern.md` into `refs/design-system.md`; `repository-mapping.md` into `refs/architecture.md`
- Confirmed 5 broken `REFERENCE.md` indexes (dangling targets that never existed) — no content carried; files preserved in archive
- Regenerated `standards/flutter/_INDEX.md` to AUTO-GENERATED format with File Match table, Loading Instructions, and Archived section referencing `archive/flutter/`
- Moved all 22 `flutter-<name>/` folders to `archive/flutter/` (repo root) using `git mv`, preserving full history; no files deleted
- `cook/SKILL.md` Flutter row already resolves to `standards/flutter/_INDEX.md`; no change required

---

## [56c3d70] — 2026-05-21 · Align skill-routing with keyword-driven model

**Fixed a dangling reference left in the review skill routing after the keyword-driven refactor.**

- Rewrote `standards/review/refs/skill-routing.md` to drop the `--frontend`/`--backend`/`--full-stack` mode flags and match concern refs via `standards/global/_INDEX.md` instead
- Replaced the mode-flag table with a Surface-to-Skills Mapping (concern refs + domain skills, additive union)
- Updated worked examples to load specific concern refs instead of mode-flag invocations
- Added §6 "Post-Verification Audit" to `verify-[6].md` and moved it into `verify/done/`

---

## [d290dac] — 2026-05-21 · Make cook a keyword-driven orchestrator

**cook now detects what a task touches by keyword and composes standards from concern refs — mode flags are gone.**

- Rewrote the top-level `SKILL.md` as a keyword-driven orchestrator: receive summary → detect review intent → extract keywords → load global P0 → match concern refs → detect domains → compile
- Removed the `--frontend`/`--backend`/`--full-stack` mode flags and the P1 mode section from `standards/global/SKILL.md`
- Converted `standards/global/_INDEX.md` into a Concern Match table (keyword + file pattern → concern ref)
- Folded the frontend/backend layer rules into concern refs: `architecture.md`, `security.md`, `performance.md`

---

## [d679bf1] — 2026-05-21 · Add changelog and verify-[6] plan

**Introduced a root changelog and captured the next verification plan as a standalone artifact.**

- Added `CHANGELOG.md` to track notable repository changes in reverse chronological order
- Added `verify/verify-[6].md` with the verification plan for the latest standards restructuring work

---

## [93f14d2] — 2026-05-20 · Consolidate standards into domain-based structure

**All skill files and references are now organized by domain — one skill entry point per domain, shared refs in a flat folder.**

- Merged separate PostgreSQL, MongoDB, and Redis skills into a single `standards/database/SKILL.md`
- Moved all database reference files into `standards/database/refs/` with vendor prefixes (e.g. `postgresql-best-practices.md`, `redis-checklist.md`)
- Collapsed all global sub-skills (api-design, architecture, code-review, coding-principles, debug, error-handling, owasp, performance, security-audit, security-standards) into a single `standards/global/SKILL.md` backed by consolidated `standards/global/refs/` files
- Added a new React consolidated `standards/react/SKILL.md` with full refs: component-patterns, performance, security, state-management, testing, tooling
- Added GraphQL refs for testing and tooling
- Moved completed verification artifacts into `verify/done/`

---

## [46aa432] — 2026-05-20 · Update review skill routing

**Small update to wire the new code review skill into the global index.**

- Updated `standards/global/_INDEX.md` to reference the new review skill
- Updated `standards/global/code-review/SKILL.md` with routing adjustments
- Updated `standards/review/SKILL.md` trigger language

---

## [4415cda] — 2026-05-20 · Add findings-first code review skill

**A new structured code review skill that outputs findings before explanations.**

- Created `standards/review/SKILL.md` — the main review skill definition
- Created `standards/review/_INDEX.md` — index for review standards
- Added reference files: `finding-severity.md`, `report-format.md`, `review-lenses.md`, `skill-routing.md`
- Added `review-plan.md` — the review workflow plan
- Updated root `SKILL.md` to include the new review skill

---

## [da88c8a] — 2026-05-20 · Reorganize TypeScript and add global standards

**TypeScript skills are consolidated into a single skill; global standards directory added.**

- Added `.gitignore`
- Updated Dart skill and its refs (testing, tooling)
- Added `standards/global/SKILL.md` and `standards/global/_INDEX.md` — new top-level global standards entry point
- Added unified `standards/typescript/SKILL.md` replacing four separate sub-skills
- Added new TypeScript ref files: `security.md`, `testing.md`, `tooling.md`
- Removed old TypeScript sub-skill directories: `typescript-best-practices`, `typescript-language`, `typescript-security`, `typescript-tooling`
- Added `verify/verify-[1].md` — first verification artifact

---

## [aeb9765] — 2026-05-19 · Rename context folders to refs

**Every skill's supporting files moved from `context/` to `refs/` — cleaner, more descriptive naming.**

- Renamed all `context/` directories to `refs/` across all skill domains: dart, database, flutter, global, graphql, nextjs, react, typescript
- Updated all `SKILL.md` files to point to `refs/` instead of `context/`
- No content changes — purely a folder rename

---

## [58c4303] — 2026-05-19 · Initial commit

**First commit — the full standards library from scratch.**

- Added `AGENTS.md` and root `SKILL.md`
- Added **Dart** standards with testing and tooling context
- Added **Database** standards: MongoDB (anti-patterns, best-practices, checklist, implementation, postgres-comparison), PostgreSQL (anti-patterns, best-practices, checklist, implementation, sql-gotchas), Redis (best-practices, checklist)
- Added **Flutter** standards: auto-route navigation, BLoC state management, CI/CD, concurrency, dependency injection, design system, error handling, feature-based clean architecture, GetX navigation, GetX state management, go-router navigation, idiomatic flutter, layer-based clean architecture, localization, navigation, notifications, performance, Retrofit networking, Riverpod state management, security, testing, widgets
- Added **Global** standards: API design, architecture, code review, coding principles, debug, error handling, OWASP (web + API), performance, security audit, security standards
- Added **GraphQL** standards: performance, schema design, security
- Added **Next.js** standards: app router, architecture, authentication, caching, data access layer, data fetching, i18n, optimization, pages router, rendering, security, server actions, server components, state management, styling, testing, tooling, upgrade guide
- Added **React** standards: component patterns, hooks, performance, security, state management, testing, tooling, TypeScript integration
- Added **TypeScript** standards: best practices, language features, security, tooling
