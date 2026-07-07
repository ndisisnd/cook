#!/usr/bin/env python3
"""cook compiler — Phase 2 (mechanical compilation layer).

Converts a list of matched skill paths into a single standards payload.
No LLM. Pure file-read + concatenation. Deterministic: same input → same output.

Usage
-----
  python3 scripts/cook_compile.py --skills P[,P...] [--cook-root DIR] [--out FILE]

  --skills     Comma-separated skill paths (relative to cook root), e.g.
               standards/global/SKILL.md,standards/react/SKILL.md,standards/global/refs/security.md
  --cook-root  Cook repository root (default: parent of this file's parent)
  --out        Write the assembled markdown to FILE instead of inlining it in
               stdout. The consumer reads the file; the payload never transits
               the model's context as an envelope field.

Output
------
Compact JSON on stdout. Without --out:
  {"content": "<assembled markdown>", "sections": [...], "degraded": [...], "metadata": {...}}
With --out (content lands in FILE, not stdout):
  {"path": "FILE", "bytes": N, "sections": [...], "degraded": [...], "metadata": {...}}

Exit codes: 0 always (a partial load is not a failure).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


COOK_ROOT_DEFAULT = Path(__file__).resolve().parent.parent


def strip_frontmatter(text: str) -> str:
    """Remove YAML frontmatter (the block between the first two '---' lines)."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return text
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            return "\n".join(lines[i + 1:]).lstrip("\n")
    return text  # no closing ---, leave as-is


def _title(s: str) -> str:
    """Convert a slug like 'api-design' or 'apiDesign' to 'Api Design'."""
    return s.replace("-", " ").replace("_", " ").title()


def section_header(rel: str) -> str:
    """Derive a terse section header from a standards-relative path.

    Buckets:
      standards/global/SKILL.md          → "## Universal"
      standards/global/refs/<name>.md    → "## <Name>"  (concern)
      standards/<domain>/SKILL.md        → "## <Domain>"
      standards/<domain>/refs/<name>.md  → "## <Domain> — <Name>"
    """
    parts = Path(rel).parts  # e.g. ('standards', 'react', 'refs', 'hooks.md')
    if len(parts) < 2:
        return f"## {_title(Path(rel).stem)}"

    domain = parts[1] if len(parts) > 1 else "unknown"
    filename = parts[-1]
    stem = Path(filename).stem  # strip .md

    if domain == "global":
        if stem.lower() == "skill":
            return "## Universal"
        return f"## {_title(stem)}"

    if stem.lower() == "skill":
        return f"## {_title(domain)}"

    return f"## {_title(domain)} — {_title(stem)}"


def categorise(rel: str) -> str:
    """Return 'universal', 'concern', or 'domain'."""
    parts = Path(rel).parts
    if len(parts) < 2:
        return "domain"
    domain = parts[1]
    if domain == "global":
        stem = Path(parts[-1]).stem.lower()
        return "universal" if stem == "skill" else "concern"
    return "domain"


def compile_skills(skills: list[str], cook_root: Path, budget: int | None = None) -> dict:
    """Assemble the standards payload from a list of skill paths.

    When budget (bytes) is set and the assembled content exceeds it, sections
    are dropped lowest-priority first — domain refs, then domain SKILL.md
    entries, then concern refs, each last-listed first — until the payload
    fits. Universal (global P0) is never dropped. Dropped paths are recorded
    in metadata.dropped_for_budget.
    """
    # Dedup while preserving first-seen order
    seen: set[str] = set()
    unique: list[str] = []
    for s in skills:
        s = s.strip()
        if s and s not in seen:
            seen.add(s)
            unique.append(s)

    # Bucket
    universal: list[str] = []
    domain: list[str] = []
    concern: list[str] = []
    for s in unique:
        cat = categorise(s)
        if cat == "universal":
            universal.append(s)
        elif cat == "concern":
            concern.append(s)
        else:
            domain.append(s)

    ordered = universal + domain + concern
    entries: list[dict] = []   # {rel, cat, is_ref, header, text}
    degraded: list[str] = []

    root = cook_root.resolve()
    for rel in ordered:
        path = (cook_root / rel).resolve()
        # Bounds check before any read: a path that resolves outside cook_root
        # (e.g. ../../outside.md) must never be read, or its content leaks into
        # the payload. Degrade it like an unreadable file instead.
        if not path.is_relative_to(root):
            degraded.append(rel)
            continue
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError:
            degraded.append(rel)
            continue
        body = strip_frontmatter(raw).strip()
        header = section_header(rel)
        entries.append({
            "rel": rel,
            "cat": categorise(rel),
            "is_ref": Path(rel).stem.lower() != "skill",
            "header": header,
            "text": f"{header}\n\n{body}",
        })

    def assembled_size(items):
        return len("\n\n---\n\n".join(e["text"] for e in items).encode("utf-8"))

    dropped: list[str] = []
    if budget is not None and assembled_size(entries) > budget:
        # Drop priority (last-listed first within each tier); Universal never drops.
        def drop_candidates():
            tiers = (
                [e for e in entries if e["cat"] == "domain" and e["is_ref"]],
                [e for e in entries if e["cat"] == "domain" and not e["is_ref"]],
                [e for e in entries if e["cat"] == "concern"],
            )
            for tier in tiers:
                yield from reversed(tier)

        for victim in list(drop_candidates()):
            if assembled_size(entries) <= budget:
                break
            entries.remove(victim)
            dropped.append(victim["rel"])

    content = "\n\n---\n\n".join(e["text"] for e in entries)
    return {
        "content": content,
        "sections": [e["header"] for e in entries],
        "degraded": degraded,
        "metadata": {
            "resolutions_applied": [],
            "dropped_for_budget": dropped,
        },
    }


def main():
    p = argparse.ArgumentParser(description="cook compiler (Phase 2)")
    p.add_argument("--skills", required=True,
                   help="Comma-separated skill paths relative to cook root")
    p.add_argument("--cook-root", default=None,
                   help="Cook repository root (default: parent of this script's parent)")
    p.add_argument("--out", default=None,
                   help="write assembled markdown to FILE; stdout carries a "
                        "summary envelope (path, bytes, sections, degraded) "
                        "without the content")
    p.add_argument("--budget", type=int, default=None,
                   help="max payload bytes; over-budget sections drop lowest-"
                        "priority first (domain refs, domain SKILLs, concerns; "
                        "Universal never drops), recorded in "
                        "metadata.dropped_for_budget")
    args = p.parse_args()

    cook_root = Path(args.cook_root).resolve() if args.cook_root else COOK_ROOT_DEFAULT
    skills = [s for s in args.skills.split(",") if s.strip()]

    result = compile_skills(skills, cook_root, budget=args.budget)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(result["content"], encoding="utf-8")
        envelope = {
            "path": str(out_path),
            "bytes": len(result["content"].encode("utf-8")),
            "sections": result["sections"],
            "degraded": result["degraded"],
            "metadata": result["metadata"],
        }
        print(json.dumps(envelope, separators=(",", ":")))
    else:
        print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
