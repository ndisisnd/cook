#!/usr/bin/env python3
"""cook standards freshness validator.

Every standards file must say when a human last reviewed it, so drift against
fast-moving frameworks is visible instead of silent. Mechanical only — no LLM.

    python3 scripts/check_freshness.py              # exit 0 = clean, 1 = missing/invalid
    python3 scripts/check_freshness.py --max-age 90 # warn past N days (default 90)
    python3 scripts/check_freshness.py --strict     # stale files also fail

Rules
-----
* `standards/<domain>/SKILL.md` — frontmatter `metadata:` must carry
  `targets:` (the one-line version target) and `last_reviewed: YYYY-MM-DD`.
* `standards/<domain>/refs/*.md` — frontmatter must carry `last_reviewed:`.
* `_INDEX.md` files are routing tables, not standards — skipped.
* Gitignored shelves (if any) are checked only when present.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

COOK_ROOT_DEFAULT = Path(__file__).resolve().parent.parent

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
REVIEWED_RE = re.compile(r"^\s*last_reviewed:\s*['\"]?(\d{4}-\d{2}-\d{2})['\"]?\s*$", re.MULTILINE)
TARGETS_RE = re.compile(r"^\s*targets:\s*\S", re.MULTILINE)


def check_file(path: Path, *, is_skill: bool, today: date, max_age: int) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for one standards file."""
    errors: list[str] = []
    warnings: list[str] = []
    match = FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
    if not match:
        return [f"{path}: no frontmatter"], warnings
    front = match.group(1)
    reviewed = REVIEWED_RE.search(front)
    if not reviewed:
        errors.append(f"{path}: missing last_reviewed")
    else:
        try:
            age = (today - date.fromisoformat(reviewed.group(1))).days
        except ValueError:
            errors.append(f"{path}: invalid last_reviewed {reviewed.group(1)!r}")
        else:
            if age > max_age:
                warnings.append(f"{path}: last reviewed {age} days ago")
    if is_skill and not TARGETS_RE.search(front):
        errors.append(f"{path}: missing metadata.targets")
    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=COOK_ROOT_DEFAULT)
    parser.add_argument("--max-age", type=int, default=90)
    parser.add_argument("--strict", action="store_true", help="treat stale files as errors")
    args = parser.parse_args(argv)

    standards = args.root / "standards"
    today = date.today()
    errors: list[str] = []
    warnings: list[str] = []
    checked = 0
    for domain in sorted(p for p in standards.iterdir() if p.is_dir()):
        files = [(domain / "SKILL.md", True)] if (domain / "SKILL.md").exists() else []
        files += [(f, False) for f in sorted(domain.rglob("*.md"))
                  if f.name not in ("SKILL.md", "_INDEX.md")]
        for path, is_skill in files:
            e, w = check_file(path, is_skill=is_skill, today=today, max_age=args.max_age)
            errors += [x.replace(str(args.root) + "/", "") for x in e]
            warnings += [x.replace(str(args.root) + "/", "") for x in w]
            checked += 1

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"FAIL  {e}")
    if args.strict:
        errors += warnings
    if errors:
        print(f"FAIL — {len(errors)} problem(s) across {checked} standards files.")
        return 1
    print(f"OK — {checked} standards files carry review metadata"
          f"{f' ({len(warnings)} stale)' if warnings else ''}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
