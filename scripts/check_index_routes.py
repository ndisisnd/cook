#!/usr/bin/env python3
"""cook index-route validator — Phase 3 (feature 7 prevention pass).

Walks every `standards/*/_INDEX.md`, extracts each route target it tells cook to
LOAD, and asserts the target file exists. Catches the rename-without-index-update
drift (e.g. `prisma-migrations.md` renamed to `prisma-schema.md` but the index
still points at the old path) at the moment it is introduced.

Mechanical only — no LLM. Wire it into CI / pre-commit:

    python3 scripts/check_index_routes.py        # exit 0 = clean, 1 = dangling

What counts as a "route target"
-------------------------------
Only the directives that cook actually loads from:

  * `<SKILLS>/<domain>/SKILL.md` and `<SKILLS>/<domain>/refs/<name>.md`
    — the explicit "Load …" directives in every domain index. `<SKILLS>`
    resolves to the `standards/` root.
  * Bare ``<name>.md`` siblings listed on the SAME line as a qualified
    `<SKILLS>/.../refs/…` target — the comma-listed refs (e.g. the database
    index's `postgresql-checklist.md`, `sql-gotchas.md`).
  * Backtick ``refs/<name>.md`` tokens — the global index's Concern Match table,
    which omits the `<SKILLS>/` prefix; resolved relative to the index's folder.

Deliberately NOT treated as route targets: the archived/provenance tables in the
flutter & nextjs indexes. Their left-column source paths (`flutter-bloc-…/SKILL.md`)
are multi-segment archived paths cook never loads, so they are skipped by
construction — only `refs/<name>.md`, bare siblings, and `<SKILLS>/…` tokens match.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

COOK_ROOT_DEFAULT = Path(__file__).resolve().parent.parent

SKILLS_RE = re.compile(r"<SKILLS>/([A-Za-z0-9_\-./]+\.md)")
BACKTICK_RE = re.compile(r"`([^`]+)`")
REFS_TOKEN_RE = re.compile(r"refs/[A-Za-z0-9_\-]+\.md")          # refs/x.md
BARE_MD_RE = re.compile(r"[A-Za-z0-9_\-]+\.md")                   # x.md (no slash)


def extract_targets(index_path: Path, standards_root: Path) -> list[tuple[str, Path]]:
    """Return (raw_token, resolved_path) route targets declared in one _INDEX.md."""
    domain_dir = index_path.parent
    targets: list[tuple[str, Path]] = []
    seen: set[Path] = set()

    def add(token: str, path: Path):
        rp = path.resolve()
        if rp not in seen:
            seen.add(rp)
            targets.append((token, path))

    for line in index_path.read_text(encoding="utf-8").splitlines():
        refs_dir_ctx: Path | None = None  # per-line context for bare siblings

        # 1. <SKILLS>/…  →  standards/…   (qualified, prefix-resolved)
        for m in SKILLS_RE.finditer(line):
            rel = m.group(1)
            path = standards_root / rel
            add(f"<SKILLS>/{rel}", path)
            if "/refs/" in rel:
                refs_dir_ctx = path.parent

        # 2. backtick tokens
        for tok in BACKTICK_RE.findall(line):
            if tok.startswith("<SKILLS>/"):
                continue  # already handled above
            if REFS_TOKEN_RE.fullmatch(tok):
                # domain-relative concern/ref (global Concern Match table)
                path = domain_dir / tok
                add(tok, path)
                refs_dir_ctx = domain_dir / "refs"
            elif refs_dir_ctx is not None and BARE_MD_RE.fullmatch(tok):
                # bare sibling on a line that already anchored a refs/ dir
                add(tok, refs_dir_ctx / tok)

    return targets


def main():
    p = argparse.ArgumentParser(description="cook _INDEX.md route-target validator")
    p.add_argument("--cook-root", default=None,
                   help="cook repo root (default: parent of this script's parent)")
    p.add_argument("--standards", default=None,
                   help="standards dir to scan (default: <cook-root>/standards)")
    args = p.parse_args()

    cook_root = Path(args.cook_root).resolve() if args.cook_root else COOK_ROOT_DEFAULT
    standards_root = (Path(args.standards).resolve() if args.standards
                      else cook_root / "standards")

    indexes = sorted(standards_root.glob("*/_INDEX.md"))
    if not indexes:
        print(f"no _INDEX.md found under {standards_root}", file=sys.stderr)
        sys.exit(2)

    checked = 0
    dangling: list[str] = []
    for idx in indexes:
        rel_idx = idx.relative_to(cook_root) if cook_root in idx.parents else idx
        for token, path in extract_targets(idx, standards_root):
            checked += 1
            if not path.exists():
                dangling.append(f"  {rel_idx}  →  `{token}`  (resolved: {path})")

    if dangling:
        print(f"DANGLING route targets ({len(dangling)} of {checked} checked):")
        print("\n".join(dangling))
        sys.exit(1)

    print(f"OK — {checked} route targets across {len(indexes)} indexes all resolve.")
    sys.exit(0)


if __name__ == "__main__":
    main()
