#!/usr/bin/env python3
"""cook resolver — Phase 1 (fingerprint-first cache + grounded signal gathering).

Mechanical only: git, file reads, hashing, JSON. No LLM. This runs BEFORE any
classification so a cache hit never wakes the model.

Subcommands
-----------
  lookup [--path P ...] [--project DIR] [--flag NAME ...] [--prose TEXT]
      Gather raw signals via the T1/T2/T4/T5 cascade (T3 plan/PRD parsing is
      left to the agent on the miss path), build a fingerprint from raw
      observable signals (NO intent label), and check the cache. Prints a JSON
      blob to stdout: status (hit|miss|stale|skip), mode (auto|explicit-flags|
      explicit-prose), fingerprint, signals, confidence, fallback, and on a hit
      the cached routing.

      --flag NAME   Pin a specific concern, domain, or global shelf (repeatable).
                    Simple flags (--security, --react, --global) are validated
                    against tag-vocabulary.json routes_to. Compound sub-ref flags
                    (--react:hooks) load a single ref from a domain shelf; format
                    is <domain>:<ref> where ref is a stem under standards/<domain>/refs/.
                    Unknown flag → non-zero exit with usage.
      --prose TEXT  Prose argument. Any non-empty prose causes status: "skip"
                    (LLM must run; no deterministic cache key possible).

  write --fingerprint F --intent I --skills S[,S...] [--tags T,...]
        [--confidence high|medium|low] [--fallback] [--degraded P,...]
        [--index IDX,...] [--flag NAME ...] [--mode MODE]
      Atomically upsert a cache entry (tmp + os.replace) with a tag-vocabulary
      checksum and per-index checksums. Records flags and mode on the entry.

  classify [--prose TEXT] [--path P ...] [--project DIR]
      Mechanical canonicalization (miss path). Matches prose + gathered signals
      against tag-vocabulary.json tag names and aliases (case-insensitive,
      word-bounded; single-character aliases are ignored as noise) and folds in
      the resolver's domain/concern hints. Prints canonical_tags, routes, the
      per-tag match evidence, and needs_llm — true only when no domain:* route
      resolved, i.e. the only case where the model must read the vocab itself.

  heal --fingerprint F --degraded [P,...]
      Reconcile an existing entry's `degraded` flag with reality (Phase 3,
      feature 7 self-heal). Pass the `degraded` list the compiler just produced;
      the entry is rewritten atomically ONLY when the set actually changed —
      cleared when the file is fixed, updated when a new read fails. Mechanical,
      no LLM, so it is safe to call on the cache-hit fast path.

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
              "next.config.ts", "next.config.mjs", "supabase/config.toml"]

NODE_SERVER_DEPS = {
    "express", "fastify", "@nestjs/core", "koa", "@hapi/hapi", "koa-router",
    "hono", "elysia", "@apollo/server", "apollo-server", "@trpc/server",
}


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
            if "@supabase/supabase-js" in deps:
                fw.add("supabase")
            if deps.keys() & NODE_SERVER_DEPS:
                fw.add("nodejs")
        except (OSError, json.JSONDecodeError):
            pass
    if (project / "supabase" / "config.toml").exists():
        fw.add("supabase")
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
    has_node = "nodejs" in frameworks
    for f in files:
        low = f.lower()
        suf = Path(low).suffix
        in_app_pages = ("/app/" in f or f.startswith("app/")
                        or "/pages/" in f or f.startswith("pages/")
                        or "src/app/" in f)
        server_path = (low.startswith(("server/", "src/server/"))
                       or "/server/" in low
                       or low.endswith(("server.ts", "server.js", "server.mjs",
                                        "app.ts", "app.js", "app.mjs"))
                       or ".server." in low)
        frontend_path = (in_app_pages or low.startswith(("src/components/", "components/",
                                                         "src/app/", "app/", "pages/")))
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
                if has_node and server_path and not frontend_path:
                    hints.add("nodejs")
        elif suf == ".cjs":
            hints.add("nodejs")
        elif suf in (".js", ".mjs"):
            if has_node and server_path and not frontend_path:
                hints.add("nodejs")
        elif suf == ".dart":
            hints.add("flutter" if has_flutter else "dart")
        elif suf == ".swift":
            hints.add("swift")
        elif suf in (".css", ".scss", ".sass", ".less", ".pcss", ".postcss"):
            # A stylesheet extension unambiguously means the css shelf regardless
            # of framework — like .swift→swift and .dart→dart. Utility-framework
            # (Tailwind) classes inside .tsx/.html are caught by keyword routing,
            # not here, so a JSX file still routes to its framework shelf and the
            # css shelf co-loads only when the classifier sees Tailwind signals.
            hints.add("css")

    # Supabase platform domain — a SEPARATE second pass, NOT folded into the
    # elif chain above. The chain's `.sql` arm already fires for
    # supabase/migrations/*.sql and adds `database`; folding supabase into the
    # chain would let that arm consume the file first and the elif would never
    # run, so `supabase` would silently never be added (the CG-1 failure mode).
    # Match a path SEGMENT `supabase/`, never a bare substring: a bare
    # `"supabase/" in low` also matches `mysupabase/foo.ts`, `lib/foosupabase/x.ts`
    # — false loads. The segment form catches `supabase/config.toml` (root) and
    # `src/lib/supabase/client.ts` (nested client code, correctly Supabase) while
    # rejecting the look-alikes.
    for f in files:
        low = f.lower()
        if not (low.startswith("supabase/") or "/supabase/" in low):
            continue                       # not a supabase/ segment — leave to the chain
        hints.add("supabase")
        if "/migrations/" in low and low.endswith(".sql"):
            hints.add("database")          # belt-and-braces; the .sql arm also adds it

    # macOS app platform — a SEPARATE pass, like supabase above. `.swift` alone is
    # language-only (adds `swift` in the chain); the macOS *platform* shelf applies
    # only when a macOS app signal is present. Gate on the exact markers the macos
    # SKILL frontmatter triggers on — `**/*.entitlements` and `**/Info.plist` — so a
    # pure-language Swift package never pulls the platform shelf. (The macos SKILL is
    # self-scoped "macOS only"; this repo has no ios domain.)
    for f in files:
        low = f.lower()
        if low.endswith(".entitlements") or Path(low).name == "info.plist":
            hints.add("macos")
            break

    return sorted(hints)


# Path-identifiable concerns only. Keyword-only concerns (security, performance)
# stay agent-matched. Patterns mirror the global/_INDEX.md cicd row and are
# deliberately precise (workflow dirs and named CI files) so pubspec.yaml,
# codegen.yml, and tailwind.config do NOT trigger a concern.
CONCERN_PATTERNS = {
    "cicd": (".github/workflows/", ".gitlab-ci.yml", "jenkinsfile",
             "fastlane/", "azure-pipelines.yml", "bitbucket-pipelines.yml"),
}


def derive_concerns(files: list[str]) -> list[str]:
    """Detect path-identifiable cross-cutting concerns. Kept apart from
    derive_domains so domains and concerns never blur (no category leak)."""
    hints = set()
    for f in files:
        low = f.lower()
        for concern, needles in CONCERN_PATTERNS.items():
            if any(n in low for n in needles):
                hints.add(concern)
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
    concern_hints = derive_concerns(files)

    # mechanical confidence floor (LLM may refine on the miss path). A recognised
    # CI file is as strong a signal as a recognised source extension.
    if domain_hints or concern_hints:
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
        "concern_hints": concern_hints,
        "confidence": confidence,
        "fallback": fallback,
    }


def valid_flags() -> set:
    """Compute the valid simple --flag set at runtime from vocab routes_to.

    Strips any prefix (concern:/domain:/shelf:) from every routes_to target.
    Never hard-codes flag names — vocab is the only source.
    """
    vocab = json.loads(VOCAB_FILE.read_text())
    flags = set()
    for tag_data in vocab["tags"].values():
        for target in tag_data.get("routes_to", []):
            parts = target.split(":", 1)
            if len(parts) == 2:
                flags.add(parts[1])
    return flags


def valid_domain_flags() -> set:
    """Return only domain-type flag names (support sub-ref syntax <domain>:<ref>)."""
    vocab = json.loads(VOCAB_FILE.read_text())
    domains = set()
    for tag_data in vocab["tags"].values():
        for target in tag_data.get("routes_to", []):
            if target.startswith("domain:"):
                domains.add(target.split(":", 1)[1])
    return domains


def valid_sub_flags(domain: str) -> set:
    """Return valid ref stems for a domain (file names without .md extension)."""
    refs_dir = COOK_ROOT / "standards" / domain / "refs"
    if not refs_dir.is_dir():
        return set()
    return {p.stem for p in refs_dir.glob("*.md")}


def fingerprint(signals: dict, flags=None) -> str:
    """Hash of RAW OBSERVABLE SIGNALS ONLY — deliberately excludes intent label,
    so the cache can be checked before classification.

    When flags is non-empty, they are folded into the basis so flag-overrides
    produce distinct cache entries from auto-mode entries on the same surface.
    Empty/absent flags must NOT change the basis — existing auto-mode entries
    must remain valid after the upgrade (B2 backwards-compat guarantee).
    """
    basis = {
        "files": signals["files"],
        "frameworks": signals["frameworks"],
        "domain_hints": signals["domain_hints"],
        "concern_hints": signals["concern_hints"],
    }
    if flags:
        basis["flags"] = sorted(flags)
    return hashlib.sha256(json.dumps(basis, sort_keys=True).encode("utf-8")).hexdigest()[:16]


# ----------------------------------------------------------------- cache I/O

def load_routing() -> tuple[dict, bool]:
    """Return (routing, corrupt).

    corrupt is True only when the file exists but cannot be parsed — a missing
    file is a clean cold cache, not corruption. Component 8 (hard-failure
    fallback) keys off this: a corrupt cache must degrade to greedy routing, not
    masquerade as an ordinary miss that silently rebuilds and drops nothing.
    """
    if ROUTING_FILE.exists():
        try:
            return json.loads(ROUTING_FILE.read_text()), False
        except (OSError, json.JSONDecodeError):
            return {"version": 1, "entries": {}}, True
    return {"version": 1, "entries": {}}, False


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
    flags = args.flag or []
    prose = (args.prose or "").strip()

    # Validate flags: simple flags against vocab, compound domain:ref flags against disk.
    if flags:
        all_valid = valid_flags()
        all_domains = valid_domain_flags()
        errors = []
        for f in flags:
            if ":" in f:
                domain_part, ref_part = f.split(":", 1)
                if domain_part not in all_domains:
                    errors.append(
                        f"'{f}': sub-ref syntax requires a domain left of ':', "
                        f"'{domain_part}' is not a domain flag"
                    )
                else:
                    valid_refs = valid_sub_flags(domain_part)
                    if ref_part not in valid_refs:
                        errors.append(
                            f"'{f}': '{ref_part}' not found in {domain_part}/refs/ "
                            f"(valid: {', '.join(sorted(valid_refs))})"
                        )
            elif f not in all_valid:
                errors.append(f"unknown flag '{f}'")
        if errors:
            for e in errors:
                print(f"Error: {e}", file=sys.stderr)
            print(f"Valid simple flags: {', '.join(sorted(all_valid))}", file=sys.stderr)
            sys.exit(1)

    # Explicit-prose path: skip cache entirely.
    # LLM must interpret prose; no deterministic key is possible without either
    # requiring verbatim string equality (useless) or normalising with an LLM
    # (defeats the cache's guarantee that a hit never wakes the model).
    if prose:
        print(json.dumps({
            "status": "skip",
            "mode": "explicit-prose",
            "flags": sorted(flags),
            "prose": prose,
            "signals": signals,
            "confidence": signals["confidence"],
            "fallback": False,   # explicit args override the broad-load safety net
            "routing": None,
        }, indent=2))
        return

    # Auto or explicit-flags path
    fp = fingerprint(signals, flags or None)
    routing, corrupt = load_routing()

    if corrupt:
        # Component 8 — hard-failure fallback. The cache is unusable, but the
        # signals were gathered mechanically and are still trustworthy. Degrade
        # to greedy routing: the agent loads the P0 floor + every domain the
        # signals point at, broadly. Only the efficiency gain is lost.
        print(json.dumps({
            "status": "fallback",
            "fingerprint": fp,
            "signals": signals,
            "confidence": signals["confidence"],
            "fallback": True,
            "cache_corrupt": True,
            "routing": None,
        }, indent=2))
        return

    entry = routing["entries"].get(fp)

    if entry is None:
        status, payload = "miss", None
    elif entry_is_fresh(entry):
        status, payload = "hit", entry
    else:
        status, payload = "stale", None

    # Explicit-flags mode forces fallback: false — the user's flags are the load
    # surface regardless of what gather() could observe on the signal surface.
    mode = "explicit-flags" if flags else "auto"
    effective_fallback = False if flags else signals["fallback"]

    result = {
        "status": status,
        "mode": mode,
        "fingerprint": fp,
        "signals": signals,
        "confidence": signals["confidence"],
        "fallback": effective_fallback,
        "routing": payload,
    }
    if flags:
        result["flags"] = sorted(flags)
    print(json.dumps(result, indent=2))


def cmd_classify(args):
    """Mechanical alias matching: prose + signals -> canonical tags -> routes.

    Replaces the LLM's vocab read on the common miss path. The model is only
    needed when this returns needs_llm: true (no domain resolved), which keeps
    classification deterministic and vocab-file reads out of the context.
    """
    import re

    project = Path(args.project).resolve() if args.project else Path.cwd()
    signals = gather(args.path or [], project)
    prose = (args.prose or "").strip()

    hay = " ".join(
        [prose]
        + signals["files"]
        + signals["extensions"]
        + signals["frameworks"]
    ).lower()

    tags = json.loads(VOCAB_FILE.read_text())["tags"]
    matched: dict[str, dict] = {}
    for tag, data in tags.items():
        for needle in [tag] + data.get("aliases", []):
            n = needle.lower()
            if len(n) < 2:
                continue  # single-char aliases ('!') match everything — noise
            if re.search(r"(?<![a-z0-9])" + re.escape(n) + r"(?![a-z0-9])", hay):
                matched[tag] = {"routes_to": data["routes_to"], "matched_on": needle}
                break

    # Fold in mechanically derived hints even without a textual alias hit.
    for hint_key, kind in (("domain_hints", "domain_hint"),
                           ("concern_hints", "concern_hint")):
        for h in signals[hint_key]:
            if h in tags and h not in matched:
                matched[h] = {"routes_to": tags[h]["routes_to"],
                              "matched_on": f"signal:{kind}:{h}"}

    routes = sorted({r for m in matched.values() for r in m["routes_to"]})
    print(json.dumps({
        "canonical_tags": sorted(matched),
        "routes": routes,
        "matched": matched,
        "signals": signals,
        "needs_llm": not any(r.startswith("domain:") for r in routes),
    }, separators=(",", ":")))


def cmd_write(args):
    routing, _ = load_routing()           # a corrupt cache is overwritten fresh
    skills = [s for s in args.skills.split(",") if s]
    indexes = [i for i in (args.index or "").split(",") if i]
    flags = args.flag or []
    mode = args.mode if args.mode else ("explicit-flags" if flags else "auto")
    entry = {
        "intent": args.intent,
        "skills": skills,
        "canonical_tags": [t for t in (args.tags or "").split(",") if t],
        "confidence": args.confidence,
        "fallback": args.fallback,
        "degraded": [d for d in (args.degraded or "").split(",") if d],
        "vocab_checksum": sha256_file(VOCAB_FILE),
        "index_checksums": {i: sha256_file(COOK_ROOT / i) for i in indexes},
        "decided_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mode": mode,
    }
    if flags:
        entry["flags"] = sorted(flags)
    routing["entries"][args.fingerprint] = entry
    atomic_write(routing)
    print(json.dumps({"status": "written", "fingerprint": args.fingerprint}))


def cmd_heal(args):
    """Feature 7 self-heal. Reconcile the stored `degraded` flag with the list
    the compiler just produced, rewriting the entry only when the set changed.

    The routing decision itself (skills, tags, intent, confidence) is never
    touched — a content-read failure must not corrupt a correct routing. The
    compiler re-reads every path each run, so the fresh `degraded` list is
    ground truth: empty once the file is fixed (entry heals), or naming the new
    failure. Because the comparison happens here in code, the cache-hit caller
    stays model-free."""
    routing, corrupt = load_routing()
    if corrupt:
        print(json.dumps({"status": "noop", "reason": "cache-corrupt",
                          "fingerprint": args.fingerprint}))
        return
    entry = routing["entries"].get(args.fingerprint)
    if entry is None:
        print(json.dumps({"status": "noop", "reason": "no-entry",
                          "fingerprint": args.fingerprint}))
        return

    new_degraded = sorted({d for d in (args.degraded or "").split(",") if d})
    old_degraded = sorted(entry.get("degraded", []))
    if new_degraded == old_degraded:
        print(json.dumps({"status": "unchanged", "fingerprint": args.fingerprint,
                          "degraded": new_degraded}))
        return

    entry["degraded"] = new_degraded
    entry["healed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    routing["entries"][args.fingerprint] = entry
    atomic_write(routing)
    status = "healed" if not new_degraded else "degraded-updated"
    print(json.dumps({"status": status, "fingerprint": args.fingerprint,
                      "degraded": new_degraded, "previous": old_degraded}))


def main():
    p = argparse.ArgumentParser(description="cook resolver (Phase 1)")
    sub = p.add_subparsers(dest="cmd", required=True)

    lk = sub.add_parser("lookup")
    lk.add_argument("--path", action="append", help="explicit file path (repeatable)")
    lk.add_argument("--project", help="project dir to scan (default CWD)")
    lk.add_argument("--flag", action="append", metavar="NAME",
                    help="pin a concern or domain flag (repeatable); validated against vocab")
    lk.add_argument("--prose", metavar="TEXT",
                    help="prose argument; any non-empty value skips the cache (status: skip)")
    lk.set_defaults(func=cmd_lookup)

    cl = sub.add_parser("classify")
    cl.add_argument("--prose", metavar="TEXT", help="prose to match against the vocab")
    cl.add_argument("--path", action="append", help="explicit file path (repeatable)")
    cl.add_argument("--project", help="project dir to scan (default CWD)")
    cl.set_defaults(func=cmd_classify)

    wr = sub.add_parser("write")
    wr.add_argument("--fingerprint", required=True)
    wr.add_argument("--intent", default="unspecified",
                    help="diagnostic label recorded on the entry; never routes")
    wr.add_argument("--skills", required=True, help="comma-separated skill paths")
    wr.add_argument("--tags", help="comma-separated canonical tags")
    wr.add_argument("--confidence", default="high", choices=["high", "medium", "low"])
    wr.add_argument("--fallback", action="store_true")
    wr.add_argument("--degraded", help="comma-separated failed paths")
    wr.add_argument("--index", help="comma-separated _INDEX.md paths to checksum")
    wr.add_argument("--flag", action="append", metavar="NAME",
                    help="flags used for this lookup (repeatable; recorded on entry)")
    wr.add_argument("--mode", choices=["auto", "explicit-flags"],
                    help="mode recorded on entry (default: explicit-flags if --flag, else auto)")
    wr.set_defaults(func=cmd_write)

    hl = sub.add_parser("heal")
    hl.add_argument("--fingerprint", required=True)
    hl.add_argument("--degraded", default="",
                    help="comma-separated paths that failed THIS run (empty = all read OK)")
    hl.set_defaults(func=cmd_heal)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
