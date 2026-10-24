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
  --manifest   With --out: also write a section manifest, a JSON list of
               {header, rel, bucket, byte_start, byte_end} in payload order.
               Offsets are UTF-8 byte positions in the payload file; the slice
               [byte_start:byte_end] is one section including its header line.
               Sections are joined by "\\n\\n---\\n\\n". `--manifest PATH`
               writes PATH; a bare `--manifest` writes beside --out with a .json
               suffix (payload-<fp>.md -> payload-<fp>.json). The envelope gains
               manifest_path. cook_cache.py write reads that sibling file.

Output
------
Compact JSON on stdout. Without --out:
  {"content": "<assembled markdown>", "sections": [...], "degraded": [...], "metadata": {...}}
With --out (content lands in FILE, not stdout):
  {"path": "FILE", "bytes": N, "sections": [...], "degraded": [...], "metadata": {...}}

Exit codes: 0 always (a partial load is not a failure).

Slice (v1.2.0 Phase 6)
----------------------
  python3 scripts/cook_compile.py slice --payload FILE --section S [--section S ...]
                                        [--manifest PATH] [--list]

  Prints only the named sections of an already compiled payload, read through
  its manifest. No LLM, no recompile. Each S is a header ("## React — Hooks" or
  "React — Hooks" without the "## ") or a standards-relative path
  (standards/react/refs/hooks.md). Output is the raw bytes of each section
  (header line included), in payload order, joined by the payload's own
  separator, so one section is byte-identical to its range in the payload.
  --manifest defaults to the .json beside FILE. --list prints the sections
  (header, rel, bytes) as JSON instead and takes no --section.
  Exit 0 ok; 1 unknown or ambiguous section (the available sections are
  listed on stderr); 2 missing or stale manifest, or missing payload.
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

    sep = "\n\n---\n\n"
    content = sep.join(e["text"] for e in entries)
    manifest: list[dict] = []
    offset = 0
    for e in entries:
        size = len(e["text"].encode("utf-8"))
        manifest.append({"header": e["header"], "rel": e["rel"], "bucket": e["cat"],
                         "byte_start": offset, "byte_end": offset + size})
        offset += size + len(sep.encode("utf-8"))
    return {
        "manifest": manifest,
        "content": content,
        "sections": [e["header"] for e in entries],
        "degraded": degraded,
        "metadata": {
            "resolutions_applied": [],
            "dropped_for_budget": dropped,
        },
    }


def compile_to_file(skills: list[str], cook_root: Path, out: str,
                    budget: int | None = None, manifest: str | None = None) -> dict:
    """Compile and write the payload to `out`; return the summary envelope the
    CLI prints with --out. `manifest` is None (no manifest), "auto" (beside
    `out` with a .json suffix) or an explicit path."""
    result = compile_skills(skills, cook_root, budget=budget)
    rows = result.pop("manifest")
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(result["content"], encoding="utf-8")
    envelope = {
        "path": str(out_path),
        "bytes": len(result["content"].encode("utf-8")),
        "sections": result["sections"],
        "degraded": result["degraded"],
        "metadata": result["metadata"],
    }
    if manifest:
        mpath = out_path.with_suffix(".json") if manifest == "auto" else Path(manifest)
        mpath.parent.mkdir(parents=True, exist_ok=True)
        mpath.write_text(json.dumps(rows, indent=1), encoding="utf-8")
        envelope["manifest_path"] = str(mpath)
    return envelope


SEP = "\n\n---\n\n"


class SliceError(Exception):
    def __init__(self, msg: str, code: int):
        super().__init__(msg)
        self.code = code


def load_manifest(payload: Path, manifest: Path | None = None) -> tuple[bytes, list[dict]]:
    """Return (payload bytes, manifest rows) after checking the manifest still
    describes the payload. Raises SliceError(code 2) when it does not."""
    mpath = manifest or payload.with_suffix(".json")
    try:
        raw = payload.read_bytes()
    except OSError as exc:
        raise SliceError(f"Error: cannot read payload {payload}: {exc.strerror}", 2)
    try:
        rows = json.loads(mpath.read_text(encoding="utf-8"))
    except OSError:
        raise SliceError(f"Error: no manifest at {mpath}. Recompile the payload "
                         f"(cook_run.py or cook_compile.py --out ... --manifest).", 2)
    except ValueError:
        raise SliceError(f"Error: manifest {mpath} is not valid JSON; recompile the payload.", 2)
    sep = SEP.encode("utf-8")
    stale = None
    if not isinstance(rows, list) or not rows:
        stale = "manifest holds no sections"
    else:
        try:
            pos = 0
            for i, r in enumerate(rows):
                start, end = r["byte_start"], r["byte_end"]
                if start != pos or end < start:
                    stale = f"section {i} offsets do not follow the previous section"
                    break
                if not raw[start:end].startswith(r["header"].encode("utf-8") + b"\n"):
                    stale = f"section {r['header']!r} header not found at byte {start}"
                    break
                pos = end
                if i < len(rows) - 1:
                    if raw[pos:pos + len(sep)] != sep:
                        stale = f"separator missing after section {r['header']!r}"
                        break
                    pos += len(sep)
            else:
                if pos != len(raw):
                    stale = f"manifest ends at byte {pos}, payload is {len(raw)} bytes"
        except (KeyError, TypeError):
            stale = "manifest rows lack header or byte offsets"
    if stale:
        raise SliceError(f"Error: stale manifest {mpath} ({stale}). The payload changed "
                         f"after the manifest was written; recompile the payload.", 2)
    return raw, rows


def pick_sections(rows: list[dict], wanted: list[str]) -> list[dict]:
    """Rows matching `wanted` (header, header without '## ', or rel), payload order."""
    chosen: set[int] = set()
    for w in wanted:
        key = w.strip()
        hits = [i for i, r in enumerate(rows)
                if key in (r["header"], r["header"].removeprefix("## "), r["rel"])]
        avail = "; ".join(f"{r['header']} ({r['rel']})" for r in rows)
        if not hits:
            raise SliceError(f"Error: unknown section {w!r}. Available: {avail}", 1)
        if len(hits) > 1:
            raise SliceError(f"Error: section {w!r} is ambiguous; use the path. "
                             f"Available: {avail}", 1)
        chosen.add(hits[0])
    return [rows[i] for i in sorted(chosen)]


def slice_payload(payload: Path, wanted: list[str], manifest: Path | None = None) -> bytes:
    raw, rows = load_manifest(payload, manifest)
    picked = pick_sections(rows, wanted)
    return SEP.encode("utf-8").join(raw[r["byte_start"]:r["byte_end"]] for r in picked)


def sections_of(manifest_path: str | Path) -> list[dict]:
    """[{header, rel, bytes}] from a manifest file; [] when it cannot be read."""
    try:
        rows = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        return [{"header": r["header"], "rel": r["rel"],
                 "bytes": r["byte_end"] - r["byte_start"]} for r in rows]
    except (OSError, ValueError, KeyError, TypeError):
        return []


def slice_main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="cook_compile.py slice",
                                 description="print named sections of a compiled payload")
    ap.add_argument("--payload", required=True)
    ap.add_argument("--section", action="append", default=[], metavar="HEADER|REL")
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--list", action="store_true", dest="list_only")
    a = ap.parse_args(argv)
    payload = Path(a.payload)
    mpath = Path(a.manifest) if a.manifest else None
    try:
        if a.list_only:
            raw, rows = load_manifest(payload, mpath)
            out = [{"header": r["header"], "rel": r["rel"],
                    "bytes": r["byte_end"] - r["byte_start"]} for r in rows]
            print(json.dumps(out, separators=(",", ":")))
            return 0
        if not a.section:
            print("Error: give at least one --section (or --list).", file=sys.stderr)
            return 2
        data = slice_payload(payload, a.section, mpath)
    except SliceError as exc:
        print(str(exc), file=sys.stderr)
        return exc.code
    sys.stdout.buffer.write(data)
    sys.stdout.buffer.flush()
    return 0


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "slice":
        sys.exit(slice_main(sys.argv[2:]))
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
    p.add_argument("--manifest", nargs="?", const="auto", default=None,
                   help="write the section manifest (needs --out); bare flag = "
                        "beside --out with a .json suffix")
    args = p.parse_args()

    cook_root = Path(args.cook_root).resolve() if args.cook_root else COOK_ROOT_DEFAULT
    skills = [s for s in args.skills.split(",") if s.strip()]

    if args.out:
        envelope = compile_to_file(skills, cook_root, args.out,
                                   budget=args.budget, manifest=args.manifest)
        print(json.dumps(envelope, separators=(",", ":")))
    else:
        result = compile_skills(skills, cook_root, budget=args.budget)
        result.pop("manifest")
        print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
