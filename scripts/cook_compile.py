#!/usr/bin/env python3
"""cook compiler — Phase 2 (mechanical compilation layer).

Converts a list of matched skill paths into a single standards payload.
No LLM. Pure file-read + concatenation. Deterministic: same input → same output.

Usage
-----
  python3 scripts/cook_compile.py --skills P[,P...] [--cook-root DIR]

  --skills     Comma-separated skill paths (relative to cook root), e.g.
               standards/global/SKILL.md,standards/react/SKILL.md,standards/global/refs/security.md
  --cook-root  Cook repository root (default: parent of this file's parent)

Output
------
JSON on stdout:
  {
    "content":  "<assembled markdown>",
    "degraded": ["path/that/failed.md", ...],
    "metadata": {"resolutions_applied": [], "dropped_for_budget": []}
  }

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


def compile_skills(skills: list[str], cook_root: Path) -> dict:
    """Assemble the standards payload from a list of skill paths."""
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
    sections: list[str] = []
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
        sections.append(f"{header}\n\n{body}")

    content = "\n\n---\n\n".join(sections)
    return {
        "content": content,
        "degraded": degraded,
        "metadata": {
            "resolutions_applied": [],
            "dropped_for_budget": [],
        },
    }


def main():
    p = argparse.ArgumentParser(description="cook compiler (Phase 2)")
    p.add_argument("--skills", required=True,
                   help="Comma-separated skill paths relative to cook root")
    p.add_argument("--cook-root", default=None,
                   help="Cook repository root (default: parent of this script's parent)")
    args = p.parse_args()

    cook_root = Path(args.cook_root).resolve() if args.cook_root else COOK_ROOT_DEFAULT
    skills = [s for s in args.skills.split(",") if s.strip()]

    result = compile_skills(skills, cook_root)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
