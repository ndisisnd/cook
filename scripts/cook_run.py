#!/usr/bin/env python3
"""cook single-call resolver (v1.2.0 Phase 3).

One process does what the protocol used to do in five or six bash calls:
lookup -> (hit: stored payload) -> classify -> derive skills -> compile with
--manifest -> write --payload -> telemetry record. Stdlib only, no subprocess:
it imports cook_cache, cook_compile, cook_route and cook_telemetry as modules.
Every old subcommand still works on its own (Codex fallback, debugging).

Usage
-----
  cook_run.py [--project DIR] [--path P ...] [--flag NAME ...] [--prose TEXT]
              [--task TEXT] [--budget BYTES] [--intent LABEL] [--show-skills]
              [--explain] [--args RAW]
  cook_run.py --resume FINGERPRINT --tags t1,t2

  --flag NAME   a flag without its leading dashes (react, security, react:hooks).
                Flags only = explicit-flags mode (cacheable, no P0).
  --prose TEXT  explicit-prose mode: uncacheable, compiled to payload-prose.md,
                nothing written to the routing cache.
  --task TEXT   auto mode only: the task summary. Used to match _INDEX.md
                keywords and to classify; it is NOT part of the fingerprint.
  --intent      diagnostic label for the cache entry and telemetry.
  --args RAW    the raw text after `/cook`, unchanged. The script splits it into
                flags and prose, so the caller needs no flag grammar. A token that
                starts with `--` is a flag until a bare `--`; every other token is
                prose (joined with single spaces). `--args -` reads stdin. Flags
                merge with any --flag; prose joins any --prose. An invalid flag
                fails exactly as --flag does (exit 1, valid list on stderr).
  --show-skills adds the skill list to the envelope (debugging, tests).
  --explain     adds an `explain` object: per loaded skill file why it loaded
                (route tag + matched alias, file pattern, keyword, or flag), and
                per dropped sibling why not. No other envelope field changes.
  --resume/--tags
                finish a run that stopped with needs_llm. --tags are canonical
                tags from vocab/tag-vocabulary.json; they are added to the
                mechanically matched tags. Unknown tags are dropped and listed
                as ignored_tags.

Output: one compact JSON envelope on stdout:
  mode, status (hit|miss|stale|skip|needs_llm), fingerprint,
  payload {path, bytes, sections}, manifest_path, degraded,
  dropped_for_budget, needs_llm, platform_ambiguous,
  stale_reason (when stale), fallback_reason ("no_file_signals" when a bare
  domain flag had no prose and no touched files, so it loaded the full shelf),
  llm_input (only when needs_llm), explain (only with --explain).

Exit codes: 0 ok, 1 invalid flag (message on stderr), 2 usage or internal error.
Telemetry is best-effort: a failure there never changes the exit code or envelope.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import cook_cache  # noqa: E402
import cook_compile  # noqa: E402
import cook_route  # noqa: E402
import cook_telemetry  # noqa: E402


def parse_raw_args(raw: str) -> tuple[list[str], str]:
    """Split the text after `/cook` into (flags, prose). Flags keep no dashes.
    `--x` tokens are flags until a bare `--`; everything else is prose."""
    flags: list[str] = []
    prose: list[str] = []
    rest = False
    for tok in raw.split():
        if rest:
            prose.append(tok)
        elif tok == "--":
            rest = True
        elif tok.startswith("--") and tok.strip("-"):
            flags.append(tok.lstrip("-"))
        else:
            prose.append(tok)
    return flags, " ".join(prose)


def build_explain(ctx: dict, skills, fallback: bool) -> dict:
    """Why-loaded report for `skills`; mirrors how the list was derived."""
    flags = ctx["flags"]
    sig = ctx["signals"]
    text = ctx["prose"] if flags else (ctx["prose"] or ctx["task"])
    matched = {}
    if not flags:
        matched = cook_cache.do_classify(text, sig, ctx.get("resume_tags"))["matched"]
    paths = sig["files"]
    return cook_route.explain(list(skills), flags=flags, text=text, paths=paths,
                              matched=matched, fallback=fallback,
                              hits=sig.get("content_hits"))


def pending_file(fp: str) -> Path:
    return cook_cache.STATE_DIR / f"pending-{fp}.json"


def manifest_of(payload_path: str) -> str | None:
    mf = Path(payload_path).with_suffix(".json")
    return str(mf) if mf.is_file() else None


def fallback_reason(ctx: dict) -> str | None:
    """`no_file_signals` when a bare domain flag had no prose and no touched files."""
    if ctx["flags"] and not ctx["prose"] and cook_route.explicit_fallbacks(
            ctx["flags"], "", ctx["signals"]["files"], ctx["signals"].get("content_hits")):
        return "no_file_signals"
    return None


def envelope(*, mode, status, fp, payload, manifest, degraded, dropped,
             platform_ambiguous=False, stale_reason=None, skills=None,
             fallback_reason=None):
    env = {
        "mode": mode,
        "status": status,
        "fingerprint": fp,
        "payload": payload,
        "manifest_path": manifest,
        "degraded": degraded,
        "dropped_for_budget": dropped,
        "needs_llm": False,
        "platform_ambiguous": platform_ambiguous,
    }
    if stale_reason:
        env["stale_reason"] = stale_reason
    if fallback_reason:
        env["fallback_reason"] = fallback_reason
    if skills is not None:
        env["skills"] = skills
    return env


def from_compile(comp: dict) -> dict:
    return {"path": comp["path"], "bytes": comp["bytes"], "sections": comp["sections"]}


def record_telemetry(project: Path, intent: str, prompt: str, skills, mode: str):
    """Best-effort: never raises, never alters the envelope."""
    try:
        store, _scope = cook_telemetry.resolve_store(cook_cache.COOK_ROOT, project)
        cook_telemetry.record_fire(store, intent=intent, prompt=prompt,
                                   skills=list(skills), mode=mode)
    except Exception:  # noqa: BLE001 - telemetry must never block a fire
        pass


def derive_auto(cl: dict, signals: dict, task: str, p0: bool):
    """Skills for a classified task. Returns (skills, confidence, fallback)."""
    routes = cl["routes"]
    if any(r.startswith("domain:") for r in routes):
        return (cook_route.skill_list_auto(routes, signals["files"], task, p0=p0,
                                           hits=signals.get("content_hits")),
                signals["confidence"], False)
    # nothing resolved even after the model's tags: load broad, never empty-handed
    routes = cook_route.broad_routes(routes, signals["domain_hints"])
    return (cook_route.skill_list_auto(routes, signals["files"], task, p0=p0,
                                           hits=signals.get("content_hits")),
            "low", True)


def do_compile(skills, out: Path, budget):
    return cook_compile.compile_to_file(skills, cook_cache.COOK_ROOT, str(out),
                                        budget=budget, manifest="auto")


def finish(ctx: dict, *, status, fp, skills, tags, confidence, fallback,
           stale_reason=None, platform_ambiguous=False, cacheable=True):
    """Compile, persist (when cacheable), record telemetry, build the envelope."""
    prose_mode = ctx["mode"] == "explicit-prose"
    out = cook_cache.STATE_DIR / ("payload-prose.md" if prose_mode else f"payload-{fp}.md")
    comp = do_compile(skills, out, ctx["budget"])
    cache_error = None
    if cacheable and not prose_mode:
        try:
            cook_cache.do_write(
                fingerprint=fp, skills=",".join(skills), intent=ctx["intent"],
                tags=",".join(tags), confidence=confidence, fallback=fallback,
                degraded=",".join(comp["degraded"]),
                index=",".join(cook_route.index_paths(skills)),
                flags=ctx["flags"], mode=ctx["mode"], payload=comp["path"],
                payload_budget=ctx["budget"])
        except (cook_cache.CookError, OSError) as exc:
            cache_error = str(exc)
    record_telemetry(ctx["project"], ctx["intent"], ctx["prompt"], skills, ctx["mode"])
    env = envelope(mode=ctx["mode"], status=status, fp=fp, payload=from_compile(comp),
                   manifest=comp.get("manifest_path"), degraded=comp["degraded"],
                   dropped=comp["metadata"]["dropped_for_budget"],
                   platform_ambiguous=platform_ambiguous, stale_reason=stale_reason,
                   skills=skills if ctx["show_skills"] else None,
                   fallback_reason=fallback_reason(ctx))
    if cache_error:
        env["cache_error"] = cache_error
    if ctx.get("explain"):
        env["explain"] = build_explain(ctx, skills, fallback)
    return env


def needs_llm_envelope(ctx, fp, cl, signals):
    cook_cache.STATE_DIR.mkdir(parents=True, exist_ok=True)
    pending_file(fp).write_text(json.dumps({
        "project": str(ctx["project"]), "paths": ctx["paths"], "flags": ctx["flags"],
        "prose": ctx["prose"], "task": ctx["task"], "budget": ctx["budget"],
        "intent": ctx["intent"], "show_skills": ctx["show_skills"],
        "explain": ctx.get("explain", False),
    }), encoding="utf-8")
    env = envelope(mode=ctx["mode"], status="needs_llm", fp=fp, payload=None,
                   manifest=None, degraded=[], dropped=[],
                   platform_ambiguous=cl["platform_ambiguous"])
    env["needs_llm"] = True
    env["llm_input"] = {
        "vocab": str(cook_cache.VOCAB_FILE),
        "task": ctx["prose"] or ctx["task"],
        "files": signals["files"],
        "extensions": signals["extensions"],
        "frameworks": signals["frameworks"],
        "domain_hints": signals["domain_hints"],
        "concern_hints": signals["concern_hints"],
        "matched_tags": cl["canonical_tags"],
        "platform_ambiguous": cl["platform_ambiguous"],
        "resume": f"cook_run.py --resume {fp} --tags <canonical tags, comma separated>",
    }
    return env


def run(ctx: dict, resume_tags=None, resume_fp: str | None = None) -> dict:
    project = ctx["project"]
    flags = ctx["flags"]
    prose = ctx["prose"]
    signals = cook_cache.gather(ctx["paths"], project)
    ctx["signals"] = signals
    ctx["resume_tags"] = resume_tags
    ctx["mode"] = ("explicit-prose" if prose else
                   "explicit-flags" if flags else "auto")

    # ----- explicit-prose: uncacheable, one call --------------------------------
    if prose:
        lk = cook_cache.do_lookup(ctx["paths"], project, flags, prose,
                                  ctx["budget"], signals=signals)
        fp = resume_fp or cook_cache.fingerprint(signals, flags or None)
        ctx["prompt"] = prose
        if flags:
            skills = cook_route.skill_list_explicit(flags, prose, signals["files"],
                                                  signals.get("content_hits"))
            return finish(ctx, status=lk["status"], fp=fp, skills=skills, tags=[],
                          confidence=lk["confidence"], fallback=False, cacheable=False)
        cl = cook_cache.do_classify(prose, signals, resume_tags)
        if cl["needs_llm"] and resume_tags is None:
            return needs_llm_envelope(ctx, fp, cl, signals)
        skills, conf, fb = derive_auto(cl, signals, prose, p0=False)
        return finish(ctx, status=lk["status"], fp=fp, skills=skills,
                      tags=cl["canonical_tags"], confidence=conf, fallback=fb,
                      platform_ambiguous=cl["platform_ambiguous"], cacheable=False)

    ctx["prompt"] = ctx["task"]

    # ----- resume: classify from the model's tags, then finish ------------------
    if resume_tags is not None:
        fp = resume_fp
        cl = cook_cache.do_classify(ctx["task"], signals, resume_tags)
        if flags:
            skills, tags, conf, fb = (cook_route.skill_list_explicit(
                                          flags, "", signals["files"],
                                          signals.get("content_hits")), [],
                                      signals["confidence"], False)
        else:
            skills, conf, fb = derive_auto(cl, signals, ctx["task"], p0=True)
            tags = cl["canonical_tags"]
        env = finish(ctx, status="miss", fp=fp, skills=skills, tags=tags,
                     confidence=conf, fallback=fb,
                     platform_ambiguous=cl["platform_ambiguous"])
        if cl.get("ignored_tags"):
            env["ignored_tags"] = cl["ignored_tags"]
        return env

    # ----- auto / explicit-flags: cache first -----------------------------------
    lk = cook_cache.do_lookup(ctx["paths"], project, flags, "", ctx["budget"],
                              signals=signals)
    status, fp = lk["status"], lk["fingerprint"]

    if status == "hit" and lk["compile_needed"] is False:
        p = lk["payload"]
        env = envelope(mode=ctx["mode"], status="hit", fp=fp,
                       payload={"path": p["path"], "bytes": p["bytes"],
                                "sections": p["sections"]},
                       manifest=manifest_of(p["path"]), degraded=p["degraded"],
                       dropped=p["metadata"].get("dropped_for_budget", []),
                       skills=lk["routing"]["skills"] if ctx["show_skills"] else None,
                       fallback_reason=fallback_reason(ctx))
        record_telemetry(project, ctx["intent"], ctx["prompt"],
                         lk["routing"]["skills"], ctx["mode"])
        if ctx.get("explain"):
            env["explain"] = build_explain(ctx, lk["routing"]["skills"],
                                           lk["routing"].get("fallback", False))
        return env

    if status == "fallback":                      # corrupt cache: greedy, no write
        if flags:
            skills = cook_route.skill_list_explicit(flags, "", signals["files"],
                                                    signals.get("content_hits"))
        else:
            routes = cook_route.broad_routes([], signals["domain_hints"])
            skills = cook_route.skill_list_auto(routes, signals["files"],
                                                ctx["task"], p0=True,
                                                hits=signals.get("content_hits"))
        env = finish(ctx, status="miss", fp=fp, skills=skills, tags=[],
                     confidence="low", fallback=True, cacheable=False)
        env["cache_corrupt"] = True
        return env

    if status == "hit":                           # legacy entry: compile + upgrade
        e = lk["routing"]
        return finish(ctx, status="hit", fp=fp, skills=e["skills"],
                      tags=e.get("canonical_tags", []),
                      confidence=e.get("confidence", "high"),
                      fallback=e.get("fallback", False))

    # miss | stale
    stale_reason = lk.get("stale_reason")
    if flags:
        return finish(ctx, status=status, fp=fp,
                      skills=cook_route.skill_list_explicit(
                          flags, "", signals["files"],
                          signals.get("content_hits")), tags=[],
                      confidence=signals["confidence"], fallback=False,
                      stale_reason=stale_reason)
    cl = cook_cache.do_classify(ctx["task"], signals)
    if cl["needs_llm"]:
        return needs_llm_envelope(ctx, fp, cl, signals)
    skills, conf, fb = derive_auto(cl, signals, ctx["task"], p0=True)
    return finish(ctx, status=status, fp=fp, skills=skills,
                  tags=cl["canonical_tags"], confidence=conf, fallback=fb,
                  stale_reason=stale_reason,
                  platform_ambiguous=cl["platform_ambiguous"])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="cook single-call resolver")
    ap.add_argument("--project")
    ap.add_argument("--path", action="append", default=[])
    ap.add_argument("--flag", action="append", default=[], metavar="NAME")
    ap.add_argument("--prose", default="")
    ap.add_argument("--task", default="")
    ap.add_argument("--budget", type=int, default=None)
    ap.add_argument("--intent", default="unspecified")
    ap.add_argument("--show-skills", action="store_true")
    ap.add_argument("--explain", action="store_true")
    ap.add_argument("--args", dest="raw_args", default=None, metavar="RAW")
    ap.add_argument("--resume", metavar="FINGERPRINT")
    ap.add_argument("--tags", default="")
    argv = list(sys.argv[1:] if argv is None else argv)
    for i, a in enumerate(argv):                 # `--args --react x` would parse as a flag
        if a == "--args" and i + 1 < len(argv):
            argv[i:i + 2] = [f"--args={argv[i + 1]}"]
            break
    args = ap.parse_args(argv)

    try:
        resume_tags = resume_fp = None
        if args.resume:
            pf = pending_file(args.resume)
            try:
                pend = json.loads(pf.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                print(f"Error: no pending run for fingerprint {args.resume} "
                      f"(run cook_run.py without --resume first)", file=sys.stderr)
                return 2
            resume_fp = args.resume
            resume_tags = [t.strip() for t in args.tags.split(",") if t.strip()]
            ctx = {"project": Path(pend["project"]), "paths": pend["paths"],
                   "flags": pend["flags"], "prose": pend["prose"],
                   "task": pend["task"], "budget": pend["budget"],
                   "intent": pend["intent"],
                   "show_skills": pend["show_skills"] or args.show_skills,
                   "explain": pend.get("explain", False) or args.explain}
        else:
            raw_flags, raw_prose = [], ""
            if args.raw_args is not None:
                raw = sys.stdin.read() if args.raw_args == "-" else args.raw_args
                raw_flags, raw_prose = parse_raw_args(raw)
            ctx = {
                "project": Path(args.project).resolve() if args.project else Path.cwd(),
                "paths": args.path,
                "flags": sorted({f.lstrip("-") for f in args.flag + raw_flags
                                 if f.strip("-")}),
                "prose": " ".join(x for x in (args.prose.strip(), raw_prose) if x),
                "task": args.task.strip(),
                "budget": args.budget, "intent": args.intent,
                "show_skills": args.show_skills, "explain": args.explain,
            }
            if ctx["flags"]:
                cook_cache.check_flags(ctx["flags"])
        env = run(ctx, resume_tags, resume_fp)
        if args.resume:
            try:
                pending_file(args.resume).unlink()
            except OSError:
                pass
    except cook_cache.CookError as exc:
        for line in exc.lines:
            print(line, file=sys.stderr)
        return exc.code
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(env, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
