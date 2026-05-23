#!/usr/bin/env python3
"""cook resolver — Phase 1 (fingerprint-first cache + grounded signal gathering).

Mechanical only: git, file reads, hashing, JSON. No LLM. This runs BEFORE any
classification so a cache hit never wakes the model.

Subcommands
-----------
  lookup [--path P ...] [--project DIR]
      Gather raw signals via the T1/T2/T4/T5 cascade (T3 plan/PRD parsing is
      left to the agent on the miss path), build a fingerprint from raw
      observable signals (NO intent label), and check the cache. Prints a JSON
      blob to stdout: status (hit|miss|stale), fingerprint, signals, confidence,
      fallback, and on a hit the cached routing.

  write --fingerprint F --intent I --skills S[,S...] [--tags T,...]
        [--confidence high|medium|low] [--fallback] [--degraded P,...]
        [--index IDX,...]
      Atomically upsert a cache entry (tmp + os.replace) with a tag-vocabulary
      checksum and per-index checksums.

Paths
-----
  cook root (this file's parent.parent): vocab/tag-vocabulary.json, .agent-skills/routing.json
  project (--project, default CWD):      git surface + manifests to scan
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

COOK_ROOT = Path(__file__).resolve().parent.parent
VOCAB_FILE = COOK_ROOT / "vocab" / "tag-vocabulary.json"
STATE_DIR = COOK_ROOT / ".agent-skills"
ROUTING_FILE = STATE_DIR / "routing.json"

MANIFESTS = ["package.json", "pubspec.yaml", "tsconfig.json", "next.config.js",
             "next.config.ts", "next.config.mjs"]


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str | None:
    try:
        return sha256_text(path.read_text())
    except OSError:
        return None


# --------------------------------------------------------- gather (T1/T2/T4/T5)

def git_files(project: Path) -> list[str]:
    """T2 — ground truth: uncommitted + staged changes."""
    out = set()
    for cmd in (["git", "diff", "--name-only", "HEAD"],
                ["git", "status", "--porcelain"]):
        try:
            res = subprocess.run(cmd, cwd=project, capture_output=True,
                                 text=True, timeout=10)
        except (OSError, subprocess.SubprocessError):
            continue
        if res.returncode != 0:
            continue
        for line in res.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            # porcelain lines look like "XY path"; diff lines are bare paths
            if cmd[1] == "status":
                line = line[3:].strip() if len(line) > 3 else line
            out.add(line)
    return sorted(out)


def detect_manifests(project: Path) -> list[str]:
    return [m for m in MANIFESTS if (project / m).exists()]


def manifest_frameworks(project: Path, manifests: list[str]) -> list[str]:
    fw = set()
    if any(m.startswith("next.config") for m in manifests):
        fw.add("nextjs")
    pkg = project / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text())
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            if "next" in deps:
                fw.add("nextjs")
            if "react" in deps:
                fw.add("react")
        except (OSError, json.JSONDecodeError):
            pass
    if "tsconfig.json" in manifests:
        fw.add("typescript")
    pub = project / "pubspec.yaml"
    if pub.exists():
        try:
            text = pub.read_text()
            fw.add("flutter" if "flutter:" in text or "flutter\n" in text else "dart")
        except OSError:
            pass
    return sorted(fw)


def extensions(files: list[str]) -> list[str]:
    return sorted({Path(f).suffix.lower() for f in files if Path(f).suffix})


def derive_domains(files, frameworks, project: Path):
    """Extension disambiguation: (extension × path × manifest) — extension alone
    NEVER decides a domain. Returns sorted domain hints."""
    hints = set()
    has_next = "nextjs" in frameworks
    has_react = "react" in frameworks
    has_flutter = "flutter" in frameworks
    for f in files:
        low = f.lower()
        suf = Path(low).suffix
        in_app_pages = ("/app/" in f or f.startswith("app/")
                        or "/pages/" in f or f.startswith("pages/")
                        or "src/app/" in f)
        if suf in (".sql",) or low.endswith(".entity.ts") or "/migrations/" in low:
            hints.add("database")
        elif suf in (".graphql", ".gql"):
            hints.add("graphql")
        elif suf in (".tsx", ".jsx"):
            if has_next or in_app_pages:
                hints.add("nextjs")
            elif has_react:
                hints.add("react")
            else:
                hints.add("react")  # JSX implies React family even without dep
        elif suf == ".ts":
            if has_next or in_app_pages:
                hints.add("nextjs")
            else:
                hints.add("typescript")
        elif suf == ".dart":
            hints.add("flutter" if has_flutter else "dart")
    return sorted(hints)


def gather(explicit_paths: list[str], project: Path) -> dict:
    source = "none"
    files: list[str] = []
    if explicit_paths:                       # T1
        files = sorted(set(explicit_paths))
        source = "explicit"
    if not files:                            # T2
        gf = git_files(project)
        if gf:
            files, source = gf, "git"
    manifests = detect_manifests(project)    # T4
    frameworks = manifest_frameworks(project, manifests)
    if not files and frameworks:             # greenfield: manifest only
        source = "manifest"
    domain_hints = derive_domains(files, frameworks, project)

    # mechanical confidence floor (LLM may refine on the miss path)
    if domain_hints:
        confidence, fallback = "high", False
    elif files or frameworks:
        confidence, fallback = "medium", False
    else:                                    # T5 — nothing observable
        confidence, fallback = "low", True

    return {
        "source": source,
        "files": files,
        "extensions": extensions(files),
        "frameworks": frameworks,
        "domain_hints": domain_hints,
        "confidence": confidence,
        "fallback": fallback,
    }


def fingerprint(signals: dict) -> str:
    """Hash of RAW OBSERVABLE SIGNALS ONLY — deliberately excludes intent label,
    so the cache can be checked before classification."""
    basis = json.dumps({
        "files": signals["files"],
        "frameworks": signals["frameworks"],
        "domain_hints": signals["domain_hints"],
    }, sort_keys=True)
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]


# ----------------------------------------------------------------- cache I/O

def load_routing() -> dict:
    if ROUTING_FILE.exists():
        try:
            return json.loads(ROUTING_FILE.read_text())
        except (OSError, json.JSONDecodeError):
            pass
    return {"version": 1, "entries": {}}


def atomic_write(data: dict):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = ROUTING_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2))
    os.replace(tmp, ROUTING_FILE)            # atomic rename


def entry_is_fresh(entry: dict) -> bool:
    """Feature 4: vocab checksum + index checksums must still match."""
    if entry.get("vocab_checksum") != sha256_file(VOCAB_FILE):
        return False
    for idx, recorded in entry.get("index_checksums", {}).items():
        if sha256_file(COOK_ROOT / idx) != recorded:
            return False
    return True


# ----------------------------------------------------------------- commands

def cmd_lookup(args):
    project = Path(args.project).resolve() if args.project else Path.cwd()
    signals = gather(args.path or [], project)
    fp = fingerprint(signals)
    routing = load_routing()
    entry = routing["entries"].get(fp)

    if entry is None:
        status, payload = "miss", None
    elif entry_is_fresh(entry):
        status, payload = "hit", entry
    else:
        status, payload = "stale", None

    print(json.dumps({
        "status": status,
        "fingerprint": fp,
        "signals": signals,
        "confidence": signals["confidence"],
        "fallback": signals["fallback"],
        "routing": payload,
    }, indent=2))


def cmd_write(args):
    routing = load_routing()
    skills = [s for s in args.skills.split(",") if s]
    indexes = [i for i in (args.index or "").split(",") if i]
    routing["entries"][args.fingerprint] = {
        "intent": args.intent,
        "skills": skills,
        "canonical_tags": [t for t in (args.tags or "").split(",") if t],
        "confidence": args.confidence,
        "fallback": args.fallback,
        "degraded": [d for d in (args.degraded or "").split(",") if d],
        "vocab_checksum": sha256_file(VOCAB_FILE),
        "index_checksums": {i: sha256_file(COOK_ROOT / i) for i in indexes},
        "decided_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    atomic_write(routing)
    print(json.dumps({"status": "written", "fingerprint": args.fingerprint}))


def main():
    p = argparse.ArgumentParser(description="cook resolver (Phase 1)")
    sub = p.add_subparsers(dest="cmd", required=True)

    lk = sub.add_parser("lookup")
    lk.add_argument("--path", action="append", help="explicit file path (repeatable)")
    lk.add_argument("--project", help="project dir to scan (default CWD)")
    lk.set_defaults(func=cmd_lookup)

    wr = sub.add_parser("write")
    wr.add_argument("--fingerprint", required=True)
    wr.add_argument("--intent", required=True)
    wr.add_argument("--skills", required=True, help="comma-separated skill paths")
    wr.add_argument("--tags", help="comma-separated canonical tags")
    wr.add_argument("--confidence", default="high", choices=["high", "medium", "low"])
    wr.add_argument("--fallback", action="store_true")
    wr.add_argument("--degraded", help="comma-separated failed paths")
    wr.add_argument("--index", help="comma-separated _INDEX.md paths to checksum")
    wr.set_defaults(func=cmd_write)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
