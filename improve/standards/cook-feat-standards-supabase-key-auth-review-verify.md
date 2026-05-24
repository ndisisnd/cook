---
# Allowed values: planned, complete
status: planned
---

# Verify plan - Supabase key/auth/review fixes

Scope: verify the follow-up fixes for four review findings on
`cook-feat-standards-supabase`:

1. Supabase key guidance covers current `sb_publishable_...` and `sb_secret_...`
   keys while retaining legacy `anon` / `service_role` compatibility.
2. Edge Function auth guidance distinguishes user JWT calls from API-key
   service/webhook calls.
3. Supabase review targets load the Supabase pre-deploy checklist.
4. Supabase key-leak / client-public-env language stacks with the global
   security concern.

Primary docs to re-check before signing off:

- https://supabase.com/docs/guides/getting-started/api-keys
- https://supabase.com/docs/guides/functions/auth

## 1. Changed files

Expected changed files for this follow-up:

- `SKILL.md`
- `standards/review/SKILL.md`
- `standards/supabase/SKILL.md`
- `standards/supabase/_INDEX.md`
- `standards/supabase/refs/keys-and-clients.md`
- `standards/supabase/refs/edge-functions.md`
- `standards/supabase/refs/checklist.md`
- `vocab/tag-vocabulary.json`
- this verify plan

Flag unrelated changes separately; the workspace may also contain the staged
Node.js domain work, which is not part of this verification scope.

## 2. Automated checks

Run from the cook root.

```bash
python3 -c "import json; json.load(open('vocab/tag-vocabulary.json'))"
python3 -c "import yaml; yaml.safe_load(open('SKILL.md').read().split('---')[1])"
python3 verify/check-vocab-parity.py
python3 scripts/check_index_routes.py
```

Expected:

- valid JSON/YAML
- vocab parity passes
- index route targets all resolve

## 3. Supabase vocab coverage

```bash
python3 - <<'PY'
import json
v = json.load(open("vocab/tag-vocabulary.json"))["tags"]
sup = {a.lower() for a in v["supabase"]["aliases"]}
sec = {a.lower() for a in v["security"]["aliases"]}

must_sup = {
  "publishable key", "secret key", "sb_publishable", "sb_secret",
  "supabase_publishable_keys", "supabase_secret_keys", "apikey",
  "service_role", "anon key", "verify_jwt",
}
must_sec = {
  "key leak", "leaked key", "public env", "client-public env",
  "client bundle secret", "public-prefixed env", "bearer token misuse",
}
assert must_sup <= sup, f"supabase missing: {must_sup - sup}"
assert must_sec <= sec, f"security missing: {must_sec - sec}"
print("ok")
PY
```

Expected: `ok`.

## 4. Supabase ref-routing precision

```bash
python3 - <<'PY'
import json, os, sys
rows = {}
for line in open("standards/supabase/_INDEX.md"):
    if not line.strip().startswith("|"):
        continue
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) < 3 or "->" not in cells[0].replace("→", "->"):
        continue
    ref = cells[0].replace("*", "").replace("→", "->").split("->")[1].strip()
    for kw in cells[-1].split(","):
        kw = kw.strip().lower()
        if kw:
            rows.setdefault(kw, set()).add(ref)

matrix = {
  "publishable key": "keys-and-clients",
  "secret key": "keys-and-clients",
  "sb_publishable": "keys-and-clients",
  "sb_secret": "keys-and-clients",
  "service_role": "keys-and-clients",
  "apikey": "edge-functions",
  "supabase_secret_keys": "edge-functions",
  "supabase_publishable_keys": "edge-functions",
  "verify_jwt": "edge-functions",
}
vocab = {a.lower() for a in json.load(open("vocab/tag-vocabulary.json"))["tags"]["supabase"]["aliases"]}
failures = []
for kw, exp in matrix.items():
    got = rows.get(kw, set())
    if got != {exp} or kw not in vocab or not os.access(f"standards/supabase/refs/{exp}.md", os.R_OK):
        failures.append((kw, sorted(got), exp))
if failures:
    for f in failures:
        print("FAIL", f)
    sys.exit(1)
print("ok")
PY
```

Expected: `ok`.

## 5. Content checks

```bash
rg -n "sb_publishable|sb_secret|SUPABASE_SECRET_KEYS|SUPABASE_PUBLISHABLE_KEYS|apikey|service_role|anon" \
  standards/supabase/SKILL.md \
  standards/supabase/refs/keys-and-clients.md \
  standards/supabase/refs/edge-functions.md \
  standards/supabase/refs/checklist.md

rg -n "verify_jwt = true|verify_jwt = false|Authorization: Bearer|not JWT|apikey" \
  standards/supabase/SKILL.md \
  standards/supabase/refs/edge-functions.md \
  standards/supabase/refs/checklist.md
```

Expected:

- public-client guidance says `sb_publishable_...` is preferred and legacy `anon`
  is compatibility.
- elevated-key guidance says `sb_secret_...` is preferred and legacy
  `service_role` is compatibility.
- secret/service keys are banned from client bundles, public env vars, URLs, query
  params, and unsafe logs.
- Edge Function guidance says user JWT calls keep `verify_jwt = true`.
- Edge Function guidance says API-key service calls and webhooks use
  `verify_jwt = false` plus in-code `apikey` or signature verification.
- Edge Function guidance says publishable/secret keys are API keys, not bearer
  JWTs.

## 6. Review routing checks

Manual protocol check:

1. Read `SKILL.md` Step 2. Confirm review-code paths with Supabase domain hints
   or Supabase terms load:
   - `standards/supabase/SKILL.md`
   - `standards/supabase/refs/checklist.md`
2. Read `standards/review/SKILL.md` Step 2. Confirm Supabase review targets load
   the same two files.
3. Confirm key-leak / client-public-env / bearer/API-key misuse text loads
   `standards/global/refs/security.md`.

Pass only if all three are explicit. Do not rely on model inference.

## 7. Compile checks

```bash
python3 scripts/cook_compile.py \
  --skills standards/global/SKILL.md,standards/review/SKILL.md,standards/supabase/SKILL.md,standards/supabase/refs/checklist.md \
  | python3 -c "import json,sys;d=json.load(sys.stdin);c=d['content'];assert d['degraded']==[];assert '## Supabase' in c;assert '## Supabase - Checklist' in c or '## Supabase — Checklist' in c;print('ok')"

python3 scripts/cook_compile.py \
  --skills standards/supabase/refs/keys-and-clients.md,standards/supabase/refs/edge-functions.md \
  | python3 -c "import json,sys;d=json.load(sys.stdin);assert d['degraded']==[];print('ok')"
```

Expected: both print `ok`.

## 8. Success criteria

- [ ] Automated checks in section 2 pass.
- [ ] Vocab coverage in section 3 passes.
- [ ] Ref-routing precision in section 4 passes.
- [ ] Content checks in section 5 match the current Supabase docs.
- [ ] Review routing checks in section 6 are explicit, not inference-based.
- [ ] Compile checks in section 7 pass with `degraded == []`.
