<div align="center">

<img src="./asset/readme.jpeg">

# 🧠 Cook

__Optimising the vibe in vibecoding.__

You've got brilliant ideas (that definitely are original and unique). You set up Claude Code, crack your joints, and fire up your favourite IDE (VSCode). You ask Claude, politely, to write the code for this feature that you believe is game-changing. 

*But wait, how do you know that Claude is writing... right?*

With little to zero software engineering knowledge, expertise, and skills, you can now outsource the blood, sweat, and tears of learning discrete mathematics, algorithms, and programming languages to this simple skill: `/cook`. Now, your coding agent can write the highest-quality code.

</div>

___

`cook` is the knowledge layer. Before your coding agent starts planning or writing code changes, ask it to fire up `cook`. The skill checks your codebase, searches the most relevant coding references, compresses them, and outputs to your coding agent ready to be used.

Every run is saved — if the code changes are on the same programming languages, matches file extensions (e.g. `.tsx`), or similar tpyes (e.g. creating a component), `cook` won't call the entire library of references again but simply refers to a cache of existing runs so it's faster and cheaper.

## Installation

Run this in your terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/ndisisnd/cook/main/install.sh | bash
```

This installs cook to `~/.claude/skills/cook/`. To install somewhere else:

```bash
COOK_DIR=/path/to/destination bash install.sh
```

**Requirements:** `curl`, `python3`

## How it Works

1. **Ask your coding agent to invoke `/cook`:** `cook` will check file paths, prose descriptions, git context.
2. **Building a fingerprint:** these raw signals are hashed and kept cached. Cook will check if it has been loaded before.
3. **Determine intent:** If it's new, `cook` will match the intent (e.g. "review code"). If it's a review, it'll then figure out what surface it's reviewing and skip the other steps.
4. **Load global rules**: Global rules will alway be loaded first (e.g. SOLID principles, DRY).
5. **Load concern rules**: Concern rules are cross-cutting rules like security, error handling, performance, and API design. 
6. **Load domain rules**: Domain rules for your programming language are loaded. Multiple domains can match at once.
7. **Cache the result**: Routing decisions are cached so that next time it'll just load straight from the cache. 
8. **Compile and output**: A Python compiler stitches all the loaded rule files into one markdown blob for your agent to ingest. `cook` ends here!
   

## Available Standards

| Standards | What's covered | 
| --- | --- |
| Global | Test | 
| Dart | Test |
| Database | Test |
| Flutter | Test |
| GraphQL | Test |
| NextJS | Test |
| React | Test |
| Supabase | Test |
| Typescript | Test |

## FAQ