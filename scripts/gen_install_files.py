#!/usr/bin/env python3
"""Regenerate install.sh's FILES=( ... ) array from the working tree.

The array was hand-maintained (114 entries) and drifted from disk. This script
derives it from `git ls-files --cached --others --exclude-standard` — tracked
plus untracked-but-not-ignored files — filtered to the runtime surface:

  SKILL.md, refs/, vocab/, scripts/, standards/

Gitignored content (standards/security/, dev dirs) is excluded automatically,
matching the shipping policy. Run after adding/removing any runtime file:

  python3 scripts/gen_install_files.py
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INSTALL = ROOT / "install.sh"
PREFIXES = ("refs/", "vocab/", "scripts/", "standards/")


def runtime_files() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    keep = [f for f in out if f == "SKILL.md" or f.startswith(PREFIXES)]
    return sorted(set(keep), key=lambda f: (f != "SKILL.md", f))


def main() -> int:
    files = runtime_files()
    text = INSTALL.read_text()
    block = "FILES=(\n" + "".join(f"  {f}\n" for f in files) + ")"
    new_text, n = re.subn(r"FILES=\(\n(?:[^)]*?\n)\)", block, text, count=1)
    if n != 1:
        print("error: FILES=( ... ) block not found in install.sh", file=sys.stderr)
        return 1
    INSTALL.write_text(new_text)
    print(f"install.sh FILES regenerated: {len(files)} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
