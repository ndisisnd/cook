#!/usr/bin/env python3
"""cook telemetry — optional usage log.

An opt-in record of every successful cook fire. When enabled, each fire appends
one entry capturing the intent, the raw prompt (the task summary cook was given),
and the standards extracted — grouped as folder → the standards loaded within it.

Storage is a single JSON file, `telemetry/telemetry.json`, under the cook root
(alongside `.agent-skills/`). The same file holds the enabled flag, so state
survives across fires. It is never shipped by the installer and is gitignored —
it is a local, runtime artifact.

Usage
-----
  python3 scripts/cook_telemetry.py enable
  python3 scripts/cook_telemetry.py disable
  python3 scripts/cook_telemetry.py status
  python3 scripts/cook_telemetry.py record \
      --intent <label> --prompt <text> --skills P[,P...] [--mode M]

`record` is a no-op when telemetry is disabled — it never fails a fire. All
subcommands exit 0 on the happy path; telemetry must never block cook.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

COOK_ROOT_DEFAULT = Path(__file__).resolve().parent.parent
TELEMETRY_DIR = "telemetry"
TELEMETRY_FILE = "telemetry.json"


def _store_path(cook_root: Path) -> Path:
    return cook_root / TELEMETRY_DIR / TELEMETRY_FILE


def _load(store: Path) -> dict:
    """Read the store, tolerating absence and corruption (fresh default)."""
    try:
        data = json.loads(store.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"enabled": False, "records": []}
    if not isinstance(data, dict):
        return {"enabled": False, "records": []}
    data.setdefault("enabled", False)
    records = data.get("records")
    data["records"] = records if isinstance(records, list) else []
    return data


def _save(store: Path, data: dict) -> None:
    """Atomic write: temp file in the same dir, then rename."""
    store.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(store.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp, store)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def group_standards(skills: list[str]) -> dict[str, list[str]]:
    """Group `standards/<folder>/...` paths into folder → [standard, ...].

    A standard is named 'SKILL' for the shelf entry, 'refs/<stem>' for a ref,
    or the bare stem for anything else. Order preserved, duplicates dropped.
    """
    grouped: dict[str, list[str]] = {}
    for raw in skills:
        rel = raw.strip()
        if not rel:
            continue
        parts = Path(rel).parts
        if len(parts) >= 3 and parts[0] == "standards":
            folder = parts[1]
            remainder = parts[2:]
        elif len(parts) >= 2 and parts[0] == "standards":
            folder = parts[1]
            remainder = parts[2:]
        else:
            folder = parts[0] if parts else rel
            remainder = parts[1:]
        stem = Path(parts[-1]).stem if parts else rel
        if len(remainder) >= 2 and remainder[0] == "refs":
            name = f"refs/{stem}"
        elif stem.lower() == "skill":
            name = "SKILL"
        else:
            name = stem
        bucket = grouped.setdefault(folder, [])
        if name not in bucket:
            bucket.append(name)
    return grouped


# --- subcommands ------------------------------------------------------------

def cmd_enable(store: Path, _args) -> int:
    data = _load(store)
    data["enabled"] = True
    _save(store, data)
    print(f"cook telemetry enabled — logging to {store}")
    return 0


def cmd_disable(store: Path, _args) -> int:
    data = _load(store)
    data["enabled"] = False
    _save(store, data)
    print("cook telemetry disabled — existing records are kept")
    return 0


def cmd_record(store: Path, args) -> int:
    data = _load(store)
    if not data.get("enabled"):
        return 0  # opt-in: silent no-op when disabled
    skills = [s for s in (args.skills or "").split(",") if s.strip()]
    entry = {
        "ts": _now(),
        "intent": args.intent or "unspecified",
        "prompt": args.prompt or "",
        "mode": args.mode or "auto",
        "standards": group_standards(skills),
    }
    data["records"].append(entry)
    _save(store, data)
    return 0


def _bar(n: int, total: int, width: int = 24) -> str:
    if total <= 0:
        return ""
    filled = round(width * n / total)
    return "█" * filled + "·" * (width - filled)


def cmd_status(store: Path, _args) -> int:
    data = _load(store)
    enabled = data.get("enabled", False)
    records = data.get("records", [])
    state = "enabled" if enabled else "disabled"
    print(f"cook telemetry — {state}")
    print(f"store: {store}")

    if not records:
        print("\nNo fires recorded yet.")
        if not enabled:
            print("Run `cook --enable-telemetry` to start logging.")
        return 0

    total = len(records)
    first = records[0].get("ts", "?")
    last = records[-1].get("ts", "?")
    print(f"\nFires recorded: {total}")
    print(f"Window: {first} → {last}")

    intents = Counter(r.get("intent", "unspecified") for r in records)
    folders: Counter = Counter()
    standards: Counter = Counter()
    for r in records:
        std = r.get("standards", {}) or {}
        for folder, names in std.items():
            folders[folder] += 1
            for name in names:
                standards[f"{folder}/{name}"] += 1

    def _section(title: str, counter: Counter, limit: int) -> None:
        if not counter:
            return
        print(f"\n{title}:")
        top = counter.most_common(limit)
        peak = top[0][1] if top else 1
        width = max((len(k) for k, _ in top), default=0)
        for key, n in top:
            print(f"  {key.ljust(width)}  {str(n).rjust(4)}  {_bar(n, peak)}")

    _section("By intent", intents, 20)
    _section("By folder (fires touching it)", folders, 20)
    _section("Top standards", standards, 15)
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="cook telemetry (optional usage log)")
    p.add_argument("--cook-root", default=None,
                   help="cook repository root (default: parent of this script's parent)")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("enable", help="turn telemetry on")
    sub.add_parser("disable", help="turn telemetry off (records kept)")
    sub.add_parser("status", help="print telemetry stats")

    rec = sub.add_parser("record", help="append one fire (no-op when disabled)")
    rec.add_argument("--intent", default="unspecified",
                     help="intent label from vocab/intent-vocabulary.json")
    rec.add_argument("--prompt", default="",
                     help="raw task summary cook was given")
    rec.add_argument("--skills", default="",
                     help="comma-separated skill paths that were compiled")
    rec.add_argument("--mode", default="auto",
                     help="invocation mode: auto | explicit-flags | explicit-prose")

    args = p.parse_args()
    cook_root = Path(args.cook_root).resolve() if args.cook_root else COOK_ROOT_DEFAULT
    store = _store_path(cook_root)

    dispatch = {
        "enable": cmd_enable,
        "disable": cmd_disable,
        "record": cmd_record,
        "status": cmd_status,
    }
    try:
        return dispatch[args.command](store, args)
    except Exception as exc:  # never let telemetry break a fire
        if args.command == "record":
            return 0
        print(f"telemetry error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
