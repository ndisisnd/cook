#!/usr/bin/env python3
"""cook routing: derive the skill list from routes (auto) or flags (explicit).

One implementation shared by the product (scripts/cook_run.py) and the gate
(verify/routing_parity.py). Stdlib only. No I/O besides reading standards/.

Skill-list rule (deterministic; keep it identical before and after each phase)
-------------------------------------------------------------------------
Paths are relative to the cook root. Order: global entries first (SKILL.md,
then refs sorted by name), then each domain in sorted order (SKILL.md, then
refs sorted by name). A path appears once.

Auto mode (protocol-manual.md Steps 3-5):
  * `standards/global/SKILL.md` always (P0).
  * For each `concern:<c>` route: `standards/global/refs/<c>.md`.
  * For each `domain:<d>` route: `standards/<d>/SKILL.md`, plus the refs the
    domain `_INDEX.md` selects. Each markdown table row of the index whose
    first cell reads `<d> -> <ref> ref` (or `<d> -> <ref>`) names
    `refs/<ref>.md`. A row such as `database -> PostgreSQL refs` names every
    ref whose stem starts with `postgresql-`. The SKILL row (`**<d>**`) never
    selects a ref. A ref row selects its file when ANY of:
      - one of its file patterns matches a path. Patterns are comma-separated
        backticked globs: `**` crosses directories, `*` does not cross `/`,
        `{a,b}` is alternation, `**/` may match zero directories. A pattern
        with no `/` also matches any file basename. Pattern `—` means none.
      - one of its keywords occurs in the task text (case-insensitive,
        word-bounded). Keywords are comma-separated cells.

Explicit mode (protocol-explicit.md "Path list"; no P0):
  * `global` -> global SKILL.md + every global ref.
  * concern flag (a stem of standards/global/refs) -> that ref only.
  * `<d>:all` -> `standards/<d>/SKILL.md` plus every `standards/<d>/refs/*.md`
    (the full shelf; `all` is reserved and no ref may use that stem).
  * bare domain flag `<d>`: `standards/<d>/SKILL.md`; with any `<d>:<ref>`
    flag for the same domain -> plus only those refs (plus prose keyword
    matches); otherwise plus every ref with NO file pattern in the index (always
    loads), plus the patterned refs whose pattern matches `paths`, plus the
    refs whose index keywords occur in the prose. Bare, no prose, no files
    -> every ref of the shelf, reported as a `no_file_signals` fallback.
  * `<d>:<ref>` with no bare `<d>` -> that ref only.
"""
from __future__ import annotations

import re
from pathlib import Path

COOK_ROOT = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------------ globbing

def glob_to_regex(pat: str) -> re.Pattern:
    i, out, n = 0, "", len(pat)
    while i < n:
        c = pat[i]
        if pat.startswith("**/", i):
            out += "(?:.*/)?"
            i += 3
        elif pat.startswith("**", i):
            out += ".*"
            i += 2
        elif c == "*":
            out += "[^/]*"
            i += 1
        elif c == "?":
            out += "[^/]"
            i += 1
        elif c == "{":
            j = pat.find("}", i)
            if j == -1:
                out += re.escape(c)
                i += 1
            else:
                alts = pat[i + 1:j].split(",")
                out += "(?:" + "|".join(re.escape(a) for a in alts) + ")"
                i = j + 1
        else:
            out += re.escape(c)
            i += 1
    return re.compile(r"\A" + out + r"\Z")


def pattern_matches(pat: str, paths: list[str]) -> bool:
    rx = glob_to_regex(pat)
    for p in paths:
        if rx.match(p):
            return True
        if "/" not in pat and rx.match(p.rsplit("/", 1)[-1]):
            return True
    return False


def keyword_matches(kw: str, prose: str) -> bool:
    kw = kw.strip()
    if not kw or kw == "—":
        return False
    return re.search(r"(?<![A-Za-z0-9_])" + re.escape(kw) + r"(?![A-Za-z0-9_])",
                     prose, re.IGNORECASE) is not None


# --------------------------------------------------------------- index parse

ARROW_RE = re.compile(r"→\s*([^|]+?)\s*(?:ref|refs)?\s*$")


def refs_of(domain: str) -> list[str]:
    d = COOK_ROOT / "standards" / domain / "refs"
    return sorted(p.stem for p in d.glob("*.md")) if d.is_dir() else []


def index_rows(domain: str) -> list[dict]:
    """Rows of the domain _INDEX.md that name a ref: {refs, patterns, keywords}."""
    idx = COOK_ROOT / "standards" / domain / "_INDEX.md"
    if not idx.exists():
        return []
    have = refs_of(domain)
    rows = []
    for line in idx.read_text(encoding="utf-8").splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        m = ARROW_RE.search(cells[0].replace("**", ""))
        if not m:
            continue
        name = m.group(1).strip()
        if name in have:
            names = [name]
        else:
            prefix = name.lower().replace(" ", "-") + "-"
            names = [r for r in have if r.startswith(prefix)]
        pats = re.findall(r"`([^`]+)`", cells[1])
        kws = [k.strip() for k in cells[2].split(",") if k.strip()]
        rows.append({"refs": names, "patterns": pats, "keywords": kws})
    return rows


def domain_refs_auto(domain: str, paths: list[str], prose: str) -> list[str]:
    chosen = set()
    for row in index_rows(domain):
        hit = (any(pattern_matches(p, paths) for p in row["patterns"])
               or any(keyword_matches(k, prose) for k in row["keywords"]))
        if hit:
            chosen.update(row["refs"])
    return sorted(chosen)


# ----------------------------------------------------------------- skill list

def rel(domain: str, ref: str | None = None) -> str:
    if ref is None:
        return f"standards/{domain}/SKILL.md"
    return f"standards/{domain}/refs/{ref}.md"


def skill_list_auto(routes: list[str], paths: list[str], prose: str,
                    p0: bool = True) -> list[str]:
    """Auto-mode list. p0=False drops global/SKILL.md (prose-without-flags
    explicit mode has no automatic P0)."""
    out = [rel("global")] if p0 else []
    concerns = sorted({r.split(":", 1)[1] for r in routes if r.startswith("concern:")})
    out += [rel("global", c) for c in concerns]
    for d in sorted({r.split(":", 1)[1] for r in routes if r.startswith("domain:")}):
        out.append(rel(d))
        out += [rel(d, r) for r in domain_refs_auto(d, paths, prose)]
    return _dedupe(out)


def refs_by_files(domain: str, paths: list[str]) -> list[tuple[str, str, str]]:
    """(ref, pattern, file) for every ref whose _INDEX.md file pattern matches a path."""
    out, seen = [], set()
    for row in index_rows(domain):
        for pat in row["patterns"]:
            rx = glob_to_regex(pat)
            hit = next((p for p in paths if rx.match(p)
                        or ("/" not in pat and rx.match(p.rsplit("/", 1)[-1]))), None)
            if hit is None:
                continue
            for r in row["refs"]:
                if (r, pat) not in seen:
                    seen.add((r, pat))
                    out.append((r, pat, hit))
    return out


def patternless_refs(domain: str) -> list[str]:
    """Refs of the shelf that no `_INDEX.md` row ties to a file pattern."""
    patterned = {r for row in index_rows(domain) if row["patterns"] for r in row["refs"]}
    return [r for r in refs_of(domain) if r not in patterned]


def _explicit(flags: list[str], prose: str, paths: list[str]):
    names = [f.lstrip("-") for f in flags]
    global_refs = refs_of("global")
    glob_part: list[str] = []
    dom: dict[str, dict] = {}
    for f in names:
        if f == "global":
            glob_part = [rel("global")] + [rel("global", r) for r in global_refs]
        elif ":" in f:
            d, r = f.split(":", 1)
            info = dom.setdefault(d, {"bare": False, "subs": set(), "all": False})
            if r == "all":
                info["all"] = True
            else:
                info["subs"].add(r)
        elif f in global_refs:
            if rel("global", f) not in glob_part:
                glob_part.append(rel("global", f))
        else:
            dom.setdefault(f, {"bare": False, "subs": set(), "all": False})["bare"] = True
    out: list[str] = []
    fallback: list[str] = []
    skill = [p for p in glob_part if p.endswith("/SKILL.md")]
    out += skill + sorted(p for p in glob_part if p not in skill)
    for d in sorted(dom):
        info = dom[d]
        if info["all"]:
            out.append(rel(d))
            refs = refs_of(d)
        elif info["bare"]:
            out.append(rel(d))
            if info["subs"]:
                refs = sorted(info["subs"] | (set(domain_refs_auto(d, [], prose))
                                              if prose else set()))
            elif prose or paths:
                refs = sorted(set(domain_refs_auto(d, paths, prose))
                              | set(patternless_refs(d)))
            else:
                refs = refs_of(d)               # no prose, no file signals
                fallback.append(d)
        else:
            refs = sorted(info["subs"])
        out += [rel(d, r) for r in refs]
    return _dedupe(out), fallback


def skill_list_explicit(flags: list[str], prose: str = "",
                        paths: list[str] | None = None) -> list[str]:
    return _explicit(flags, prose, paths or [])[0]


def explicit_fallbacks(flags: list[str], prose: str = "",
                       paths: list[str] | None = None) -> list[str]:
    """Domains whose bare flag fell back to the full shelf (no prose, no files)."""
    return _explicit(flags, prose, paths or [])[1]


def broad_routes(routes: list[str], domain_hints: list[str]) -> list[str]:
    """Greedy routing (protocol Step 2 sufficiency / corrupt cache): every
    concern ref plus every domain the signals point at, on top of `routes`."""
    extra = [f"concern:{c}" for c in refs_of("global")]
    extra += [f"domain:{d}" for d in domain_hints]
    return sorted(set(routes) | set(extra))


def index_paths(skills: list[str]) -> list[str]:
    """_INDEX.md files (relative to the cook root) of every shelf in `skills`."""
    out = []
    for s in skills:
        parts = s.split("/")
        if len(parts) >= 2 and parts[0] == "standards":
            idx = f"standards/{parts[1]}/_INDEX.md"
            if idx not in out and (COOK_ROOT / idx).exists():
                out.append(idx)
    return out


def _dedupe(items: list[str]) -> list[str]:
    seen, out = set(), []
    for i in items:
        if i not in seen:
            seen.add(i)
            out.append(i)
    return out


# -------------------------------------------------------------------- explain

def _split_skill(path: str):
    """standards/<d>/SKILL.md -> (d, None); standards/<d>/refs/<r>.md -> (d, r)."""
    parts = path.split("/")
    if len(parts) == 3:
        return parts[1], None
    return parts[1], Path(parts[-1]).stem


def index_reasons(domain: str, ref: str, paths: list[str], prose: str,
                  bare: bool = False) -> list[str]:
    """Why a domain _INDEX.md row selects `ref`: the file pattern + file, or keyword."""
    out: list[str] = []
    if bare and ref in patternless_refs(domain):
        out.append("no file patterns: always loads")
    for row in index_rows(domain):
        if ref not in row["refs"]:
            continue
        for pat in row["patterns"]:
            if pattern_matches(pat, paths):
                rx = glob_to_regex(pat)
                hit = next((p for p in paths if rx.match(p)
                            or ("/" not in pat and rx.match(p.rsplit("/", 1)[-1]))), "")
                out.append(f"file pattern `{pat}` matches {hit}")
        for kw in row["keywords"]:
            if keyword_matches(kw, prose):
                out.append(f"keyword '{kw}' in the task text")
    return out


def _tags_for(matched: dict, route: str) -> list[str]:
    return [f"tag {t} (matched on '{m['matched_on']}')"
            for t, m in sorted(matched.items()) if route in m["routes_to"]]


def explain(skills: list[str], *, flags: list[str], text: str, paths: list[str],
            matched: dict, fallback: bool = False) -> dict:
    """Why each skill file loaded and why sibling candidates did not.

    Read-only: it never changes the skill list. `paths` and `text` must be the
    ones the skill list was derived from. `matched`
    is do_classify()["matched"] (empty for explicit flags). Returns
    {"loaded": [{path, why: [..]}], "dropped": [{path, why}]}.
    """
    names = [f.lstrip("-") for f in flags]
    subs: dict[str, set] = {}
    for f in names:
        if ":" in f:
            d, r = f.split(":", 1)
            subs.setdefault(d, set()).add(r)
    fb = explicit_fallbacks(flags, text, paths) if names else []
    loaded, domains = [], []
    for s in skills:
        d, ref = _split_skill(s)
        if d not in domains:
            domains.append(d)
        why: list[str] = []
        if names:                                   # explicit flags
            if d == "global" and "global" in names:
                why.append("flag --global (whole global shelf)")
            elif d == "global":
                why.append(f"flag --{ref} (concern ref)")
            elif ref is None:
                why.append(f"flag --{d} (shelf floor)")
            else:
                if ref in subs.get(d, ()):
                    why.append(f"flag --{d}:{ref}")
                if f"{d}:all" in names:
                    why.append(f"flag --{d}:all (full shelf)")
                elif d in names and d in fb:
                    why.append(f"flag --{d} alone (full shelf): no file signals "
                               f"(fallback_reason no_file_signals)")
                elif d in names:
                    why += index_reasons(d, ref, paths if not subs.get(d) else [], text,
                                         bare=not subs.get(d))
        else:                                       # routed (auto or prose)
            if d == "global" and ref is None:
                why.append("P0: global SKILL.md loads on every auto run")
            elif d == "global":
                why += _tags_for(matched, f"concern:{ref}")
                if not why and fallback:
                    why.append("broad fallback: no domain resolved, every concern loads")
            elif ref is None:
                why += _tags_for(matched, f"domain:{d}")
                if not why and fallback:
                    why.append("broad fallback: domain named by a signal hint")
            else:
                why += index_reasons(d, ref, paths, text)
        if not why:
            why.append("kept from the cached routing entry (not re-derived)")
        loaded.append({"path": s, "why": why})
    have = set(skills)
    dropped = []
    for d in domains:
        for r in refs_of(d):
            p = rel(d, r)
            if p in have:
                continue
            if names:
                if subs.get(d):
                    why = f"shelf suppressed: only the named --{d}:<ref> flags load"
                elif d in names and text:
                    why = "has file patterns and none matched the touched files"
                elif d in names:
                    why = "has file patterns and none matched the touched files"
                else:
                    why = "no flag names it"
            elif d == "global":
                why = f"no concern:{r} route"
            else:
                why = ("no _INDEX.md file pattern or keyword matched"
                       if any(r in row["refs"] for row in index_rows(d))
                       else "no _INDEX.md row names this ref")
            dropped.append({"path": p, "why": why})
    return {"loaded": loaded, "dropped": dropped}
