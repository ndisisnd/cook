---
status: planned
parent: done/verify-[8].md
---

# Verification Run [10] — React Source-Coverage Audit & Gap Fix

> Follow-up to **[done/verify-[8].md](done/verify-[8].md)** (React folder archive).
> verify-[8] §3 defines a mandatory **source-coverage gate**: the 8 deprecated `react-*`
> folders may only be archived once every rule/example in them is confirmed present in
> the active `SKILL.md` / `refs/` (or deliberately dropped with a stated reason).
> verify-[5] (now `done/verify-[5].md`) specified that audit but left its boxes
> unchecked, and verify-[8] inherited it as an open gate.
>
> **This run is the execution of record for that gate.** It runs the audit once, here,
> and records the result in §1. A verify-[8] executor confirms coverage by reading this
> file — the §3 audit must **not** be re-run from scratch there. The consolidation is
> high quality — the new refs are typed rewrites that mostly *exceed* the originals — but
> the audit found **three gaps of unequal weight** (see §1): one load-bearing (10-A), one
> zero-action drop (10-B), one minor and optional (10-C). This plan closes them. Once §4
> lands, verify-[8]'s §3 gate is satisfied and the archive (verify-[8] §4) may run.
>
> **This file is a plan. It changes nothing on its own.** The only file changes it
> authorises live in §4, and they are all **additive** to the active React skill — no
> existing rule is altered, no folder is moved here.

---

## 1. Audit Result

Every old per-skill source was read in full and compared to its consolidation target.
(`react-hooks/refs/REFERENCE.md` also points to a `custom-hooks.md` / `advanced-patterns.md`
that were never created — no orphaned content hides behind those dead links.)

### Fully covered (no action)

| Old source | Destination | Notes |
|---|---|---|
| `react-hooks/SKILL.md` (hook rules) | `SKILL.md` § P0 Hook Correctness | covered |
| `react-typescript/` (SKILL.md + `example.md`) | `SKILL.md` § P1 TypeScript | covered; `as` pattern also in `refs/component-patterns.md` |
| `react-component-patterns/{SKILL,patterns,REFERENCE}.md` | `refs/component-patterns.md` | superior typed rewrite; adds polymorphic `as`. Dropped only untyped variants (Accordion, MouseTracker) — patterns themselves retained |
| `react-performance/{SKILL,REFERENCE}.md` | `refs/performance.md` | superior; adds virtualization, `startTransition`, web worker (typed) |
| `react-security/{SKILL,REFERENCE}.md` | `refs/security.md` | superior; adds SSR-escape, client-permission, dependency-hygiene |
| `react-state-management/{SKILL,REFERENCE}.md` | `refs/state-management.md` | superior; adds RTK, TanStack Query, URL state |
| `react-testing/{SKILL,REFERENCE}.md` | `refs/testing.md` | superior; MSW v2, jest-axe, router/context |
| `react-tooling/{SKILL,example}.md` | `refs/tooling.md` | covered; `why-did-you-render` + `useDebugValue` both present |
| all `evals/evals.json` | n/a | carry no rules — archived as-is |

### Gaps found (must close before archive)

| ID | Crit. | Source | Missing content | Resolution |
|---|---|---|---|---|
| **10-A** | **HIGH** | `react-hooks/refs/REFERENCE.md` | A **custom-hooks library** — `useLocalStorage`, `useDebounce`, `useWindowSize`, `useOnClickOutside`, `useIntersectionObserver`, `usePrevious`, `useToggle`. No home in the new structure (no 7th ref exists). | **Extract** → new `refs/hooks.md`. The only gap with real content-loss risk — this is what actually blocks verify-[8]. §4 Step 1. |
| **10-B** | none | `react-security/refs/REFERENCE.md` | "Rate Limiting on Client" (`createRateLimiter`) | **Documented deliberate drop — no file edit.** Client-side rate limiting is not an enforceable control — trivially bypassed; the server owns rate limits. Keeping it in a *security* ref implies false assurance. Recorded once in the CHANGELOG (§4 Step 6). |
| **10-C** | **LOW** | `react-performance/refs/REFERENCE.md` | "Image Optimization" (`loading="lazy"`, `decoding="async"`, `next/image`) | **Optional partial carry.** Two HTML attributes, not a house rule; `next/image` belongs to the nextjs domain. Add a 3-line note to `refs/performance.md`, *or* drop it like 10-B if trimming scope. §4 Step 3. |

> Note: `react-performance/REFERENCE.md` also held a manual `useDebounce` — that is
> subsumed by 10-A (it lives in the new `refs/hooks.md`), so it is not a separate gap.

---

## 2. After

```
standards/react/
├── SKILL.md          # +1 References entry (hooks)
├── _INDEX.md         # +1 File Match row + Loading line (hooks ref)
└── refs/
    ├── component-patterns.md   performance.md  (+native-lazy note, optional)
    ├── security.md             state-management.md
    ├── testing.md              tooling.md
    └── hooks.md                # NEW — typed custom-hooks library
```

Seven refs instead of six. Every deprecated-folder rule is now either in an active file
or recorded as a deliberate drop — verify-[8] §3 gate satisfied.

---

## 3. Scope Guardrails

- **Additive only.** No edit changes an existing rule. The only structural change is one
  new ref file plus its two pointer entries (References list + `_INDEX.md` row).
- **No archiving here.** Moving the 8 folders to `archive/react/` is verify-[8] §4 and
  must run *after* this. Do not move anything in this run.
- **`refs/hooks.md` is a rules-adjacent reference, not a utility dump.** Each hook is a
  *canonical implementation* a reviewer can point to — typed, with the correctness note
  that makes it standards-worthy (cleanup, deps, SSR-safe access). **All seven hooks in
  Step 1 clear this bar** — their "Must demonstrate" column *is* that note (including the
  small ones: `usePrevious` and `useToggle` are kept as canonical idioms, not utilities).
  The bar governs any *future* addition: if an 8th hook can't carry such a note, it does
  not belong here.
- Touch nothing outside `standards/react/` (no other domain, no `cook/SKILL.md`).
- **No redesign.** This run closes a coverage gap and unblocks verify-[8] — nothing more.
  Do not restructure, reorder, or rewrite existing sections.

---

## 4. Execution Steps

### Step 1 — Create `standards/react/refs/hooks.md` (closes 10-A · HIGH — the load-bearing gap)

Port the seven hooks from `react-hooks/refs/REFERENCE.md`, rewritten as typed TypeScript.
Each gets a one-line "why" and the correctness note that makes it a standard. Required
hooks and the non-negotiable points each must show:

| Hook | Signature (typed) | Must demonstrate |
|---|---|---|
| `useLocalStorage` | `<T>(key: string, initial: T): [T, (v: T \| ((p: T) => T)) => void]` | lazy init from storage; `try/catch` around parse/write; functional-updater support; SSR-safe `typeof window` guard |
| `useDebounce` | `<T>(value: T, delay: number): T` | `setTimeout` + cleanup `clearTimeout` in effect; deps `[value, delay]` |
| `useWindowSize` | `(): { width: number; height: number }` | `resize` listener with cleanup; SSR-safe initial read |
| `useOnClickOutside` | `(ref: RefObject<HTMLElement>, handler: (e: Event) => void): void` | `mousedown` + `touchstart`; `contains` guard; cleanup |
| `useIntersectionObserver` | `(ref: RefObject<Element>, options?: IntersectionObserverInit): boolean` | observer created in effect; `observer.disconnect()` cleanup |
| `usePrevious` | `<T>(value: T): T \| undefined` | ref updated in effect; returns prior commit's value |
| `useToggle` | `(initial?: boolean): [boolean, () => void]` | `useCallback`-stabilised toggle |

File header mirrors the other refs: `# React Hooks` then one `##` section per hook with a
short intro sentence and a single typed code block. Keep it ≈100–130 lines.

### Step 2 — Wire `refs/hooks.md` into `SKILL.md`

In the `## References` list (currently 6 bullets), add a 7th. The list is **priority/
grouped, not alphabetical** (component-patterns, state-management, performance, testing,
security, tooling) — append `hooks` as the final bullet:

```
- [hooks](refs/hooks.md) — reusable custom hooks: useLocalStorage, useDebounce, useWindowSize, useOnClickOutside, useIntersectionObserver, usePrevious, useToggle
```

Do not change any other line of `SKILL.md`.

### Step 3 — Add native lazy-load note to `refs/performance.md` (closes 10-C · LOW)

**Criticality: LOW — optional.** This is two HTML attributes, not a house rule. If
trimming scope, treat 10-C as a documented drop like 10-B (record it in the CHANGELOG,
Step 6) and skip this edit. Otherwise, in the "Reduce Bundle Size (P0)" section, after
the lazy-component guidance, add:

````
### Native Image Lazy-Loading

Defer off-screen images with native browser attributes — no library required:

```tsx
<img src={src} alt={alt} loading="lazy" decoding="async" />
```

For Next.js projects, prefer `next/image` (automatic sizing, format negotiation, and
lazy-loading) — see the nextjs domain. In plain React, the native attributes above are
the baseline.
````

No other change to `performance.md`.

### Step 4 — Record the deliberate drop for 10-B

No file edit. `createRateLimiter` from `react-security/refs/REFERENCE.md` is
**intentionally not carried over**: client-side rate limiting is not a security control
and would imply false assurance in a security ref. This satisfies the "deliberately
dropped for a stated reason" branch of verify-[8] §3. Record it in the CHANGELOG
(Step 6) — that entry is its single home.

### Step 5 — Update `standards/react/_INDEX.md`

Add a File Match row and a Loading Instruction line for the new ref. Place the row with
the other `react → … ref` rows:

```
| react → hooks ref | `**/*.tsx`, `**/*.jsx` | useLocalStorage, useDebounce, useWindowSize, useOnClickOutside, useIntersectionObserver, usePrevious, useToggle, custom hook |
```

Loading Instructions, add:

```
> Load `<SKILLS>/react/refs/hooks.md` when implementing or reviewing reusable custom hooks.
```

Leave the "Deprecated (pending removal)" section alone — verify-[8] §4 rewrites it into
the "Archived" note when the folders move.

### Step 6 — Update `CHANGELOG.md`

One entry: react ref-extraction gap fix — added `refs/hooks.md` (7 typed hooks),
native lazy-load note in `performance.md`, documented drop of client rate-limiter.

---

## 5. Success Criteria

### refs/hooks.md (10-A)
- [ ] `standards/react/refs/hooks.md` exists with all 7 hooks, each typed TS with a single code block
- [ ] Each hook shows its correctness note (cleanup / deps / SSR-safe access where applicable)
- [ ] No hook is a bare snippet without a "why it's the standard" line
- [ ] `SKILL.md` § References lists a `hooks` entry pointing to `refs/hooks.md`

### performance.md (10-C — optional, LOW)
- [ ] Either: a "Native Image Lazy-Loading" note exists in the Reduce Bundle Size section
      showing `loading="lazy"` + `decoding="async"` and deferring `next/image` to nextjs;
      **or** 10-C was recorded as a deliberate drop in the CHANGELOG (see Step 3)
- [ ] No other section of `performance.md` changed

### Deliberate drop (10-B)
- [ ] CHANGELOG records `createRateLimiter` as an intentional drop with the stated reason

### _INDEX.md
- [ ] A `react → hooks ref` File Match row exists with the 7 hook keywords
- [ ] A Loading Instruction line for `refs/hooks.md` exists
- [ ] The "Deprecated (pending removal)" section is left intact (verify-[8] owns it)

### Gate satisfied / no regressions
- [ ] Every gap in §1 is either closed (10-A, and 10-C unless dropped) or recorded as a deliberate drop (10-B)
- [ ] verify-[8] §3 source-coverage gate can now be marked passed
- [ ] All §3 Scope Guardrails held (additive only; no `react-*/` folder moved; no other domain touched; no redesign)
- [ ] `CHANGELOG.md` updated

---

## 6. Verification Notes for the Executing Agent

1. **Order matters across runs:** this run (10) must complete before verify-[8] §4
   (the archive). Archiving first would move `react-hooks/refs/REFERENCE.md` out of
   `standards/` before its content is extracted — port from it first.
2. Steps 1–3 and 5 are pure additions. Read each target file before editing and confirm
   you are inserting, not replacing.
3. The hooks in `react-hooks/refs/REFERENCE.md` are untyped `.jsx`. Do not copy verbatim —
   rewrite with explicit generics and React types to match the house style of the other
   refs (see `refs/component-patterns.md` for the bar).
4. After Step 1, re-read `refs/hooks.md` in full to confirm every hook compiles mentally
   (correct deps arrays, cleanup returns, nullable refs).
