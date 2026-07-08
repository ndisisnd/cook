#!/usr/bin/env bash
# cook install script
# Usage: curl -fsSL https://raw.githubusercontent.com/ndisisnd/cook/main/install.sh | bash
# Override destination: COOK_DIR=~/.claude/skills/cook bash install.sh
# Install from a local clone (no network): COOK_SRC=/path/to/cook bash install.sh

set -euo pipefail

REPO="https://raw.githubusercontent.com/ndisisnd/cook/main"
DEST="${COOK_DIR:-$HOME/.claude/skills/cook}"
# Install from a local clone instead of the CDN (no network; instant, reliable).
# Usage: COOK_SRC=/path/to/cook bash install.sh
SRC="${COOK_SRC:-}"

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

FILES=(
  SKILL.md
  refs/protocol-cook.md
  refs/protocol-explicit.md
  refs/telemetry.md
  scripts/check_index_routes.py
  scripts/cook_cache.py
  scripts/cook_compile.py
  scripts/cook_telemetry.py
  scripts/gen_install_files.py
  standards/css/SKILL.md
  standards/css/_INDEX.md
  standards/css/refs/accessibility.md
  standards/css/refs/architecture.md
  standards/css/refs/layout.md
  standards/css/refs/performance.md
  standards/css/refs/security.md
  standards/css/refs/tailwind.md
  standards/css/refs/theming.md
  standards/css/refs/tooling.md
  standards/dart/SKILL.md
  standards/dart/_INDEX.md
  standards/dart/refs/testing.md
  standards/dart/refs/tooling.md
  standards/database/SKILL.md
  standards/database/_INDEX.md
  standards/database/refs/postgresql-anti-patterns.md
  standards/database/refs/postgresql-best-practices.md
  standards/database/refs/postgresql-checklist.md
  standards/database/refs/postgresql-implementation.md
  standards/database/refs/redis-best-practices.md
  standards/database/refs/redis-checklist.md
  standards/database/refs/sql-gotchas.md
  standards/flutter/SKILL.md
  standards/flutter/_INDEX.md
  standards/flutter/refs/architecture.md
  standards/flutter/refs/cicd.md
  standards/flutter/refs/concurrency.md
  standards/flutter/refs/dependency-injection.md
  standards/flutter/refs/design-system.md
  standards/flutter/refs/error-handling.md
  standards/flutter/refs/localization.md
  standards/flutter/refs/navigation.md
  standards/flutter/refs/networking.md
  standards/flutter/refs/notifications.md
  standards/flutter/refs/security.md
  standards/flutter/refs/state-management.md
  standards/flutter/refs/testing.md
  standards/global/SKILL.md
  standards/global/_INDEX.md
  standards/global/refs/api-design.md
  standards/global/refs/architecture.md
  standards/global/refs/auth.md
  standards/global/refs/cicd.md
  standards/global/refs/debug.md
  standards/global/refs/error-handling.md
  standards/global/refs/performance.md
  standards/global/refs/security.md
  standards/graphql/SKILL.md
  standards/graphql/_INDEX.md
  standards/graphql/refs/conventions.md
  standards/graphql/refs/performance.md
  standards/graphql/refs/schema-design.md
  standards/graphql/refs/security.md
  standards/graphql/refs/testing.md
  standards/graphql/refs/tooling.md
  standards/macos/SKILL.md
  standards/macos/_INDEX.md
  standards/macos/refs/architecture-and-state.md
  standards/macos/refs/distribution.md
  standards/macos/refs/hig-conventions.md
  standards/macos/refs/localization.md
  standards/macos/refs/performance-accessibility.md
  standards/macos/refs/sandbox-and-tcc.md
  standards/macos/refs/windows-and-scenes.md
  standards/nextjs/SKILL.md
  standards/nextjs/_INDEX.md
  standards/nextjs/refs/app-router.md
  standards/nextjs/refs/architecture.md
  standards/nextjs/refs/data-fetching.md
  standards/nextjs/refs/i18n.md
  standards/nextjs/refs/pages-router.md
  standards/nextjs/refs/rendering-and-caching.md
  standards/nextjs/refs/security.md
  standards/nextjs/refs/server-actions.md
  standards/nextjs/refs/server-components.md
  standards/nextjs/refs/state-management.md
  standards/nextjs/refs/styling-and-optimization.md
  standards/nextjs/refs/testing.md
  standards/nextjs/refs/tooling.md
  standards/nodejs/SKILL.md
  standards/nodejs/_INDEX.md
  standards/nodejs/refs/async-errors.md
  standards/nodejs/refs/runtime-safety.md
  standards/nodejs/refs/testing.md
  standards/nodejs/refs/tooling.md
  standards/react/SKILL.md
  standards/react/_INDEX.md
  standards/react/refs/component-patterns.md
  standards/react/refs/hooks.md
  standards/react/refs/performance.md
  standards/react/refs/security.md
  standards/react/refs/state-management.md
  standards/react/refs/testing.md
  standards/react/refs/tooling.md
  standards/supabase/SKILL.md
  standards/supabase/_INDEX.md
  standards/supabase/refs/checklist.md
  standards/supabase/refs/database-functions.md
  standards/supabase/refs/edge-functions.md
  standards/supabase/refs/keys-and-clients.md
  standards/supabase/refs/migrations.md
  standards/supabase/refs/rls.md
  standards/swift/SKILL.md
  standards/swift/_INDEX.md
  standards/swift/refs/concurrency.md
  standards/swift/refs/interop.md
  standards/swift/refs/language-conventions.md
  standards/swift/refs/memory-management.md
  standards/swift/refs/performance.md
  standards/swift/refs/testing.md
  standards/swift/refs/tooling.md
  standards/typescript/SKILL.md
  standards/typescript/_INDEX.md
  standards/typescript/refs/security.md
  standards/typescript/refs/testing.md
  standards/typescript/refs/tooling.md
  vocab/intent-vocabulary.json
  vocab/tag-vocabulary.json
)

check_deps() {
  # curl is only needed for the CDN path; a local-source install skips it.
  if [[ -z "$SRC" ]] && ! command -v curl &>/dev/null; then
    echo -e "${RED}Error: curl is required but not found.${RESET}" >&2
    exit 1
  fi
  if ! command -v python3 &>/dev/null; then
    echo -e "${RED}Error: python3 is required but not found.${RESET}" >&2
    exit 1
  fi
}

# Per-file curl retry flags. --retry-all-errors (curl 7.71+) rides out the
# transient 404/5xx window right after a push while raw.githubusercontent
# propagates; guarded so older curl still works with plain --retry.
CURL_RETRY=(--retry 5 --retry-delay 2 --connect-timeout 10)
# Detect with a full read (grep >/dev/null), not `grep -q`: -q early-exits and
# closes the pipe, racing curl's write and flaking to a false negative.
if curl --help all 2>/dev/null | grep -F -- '--retry-all-errors' >/dev/null 2>&1; then
  CURL_RETRY+=(--retry-all-errors)
fi

fetch_file() {
  local rel="$1"
  local dest="$DEST/$rel"
  mkdir -p "$(dirname "$dest")"
  if [[ -n "$SRC" ]]; then
    if cp "$SRC/$rel" "$dest" 2>/dev/null; then
      echo -e "  ${GREEN}✓${RESET} $rel"
      return 0
    fi
    echo -e "${RED}  ✗ Missing in source: $rel${RESET}" >&2
    return 1
  fi
  if curl -fsSL "${CURL_RETRY[@]}" "$REPO/$rel" -o "$dest"; then
    echo -e "  ${GREEN}✓${RESET} $rel"
    return 0
  fi
  echo -e "${RED}  ✗ Failed: $rel${RESET}" >&2
  return 1
}

main() {
  check_deps

  echo -e "\n${BOLD}cook installer${RESET}"
  echo -e "Destination: ${CYAN}$DEST${RESET}"
  if [[ -n "$SRC" ]]; then
    echo -e "Source: ${CYAN}$SRC${RESET} (local, no network)"
  fi
  echo ""

  if [[ -d "$DEST" && -f "$DEST/SKILL.md" ]]; then
    echo -e "Updating existing install at ${CYAN}$DEST${RESET}\n"
  fi

  # Track failures as a space-separated list (repo paths never contain spaces)
  # so we can retry ONLY the failed files, not re-roll all of them. bash 3.2
  # safe — no empty-array-under-set-u traps.
  local failed=""
  for f in "${FILES[@]}"; do
    fetch_file "$f" || failed="$failed $f"
  done

  # Retry only the still-failed subset with backoff (CDN path only; a local
  # source that's missing a file won't heal by waiting).
  if [[ -z "$SRC" && -n "${failed// }" ]]; then
    local attempt todo f2
    for attempt in 1 2 3; do
      [[ -z "${failed// }" ]] && break
      todo="$failed"; failed=""
      echo -e "\n${CYAN}Retrying$(echo "$todo" | wc -w | tr -d ' ') file(s) after CDN lag (attempt $attempt)...${RESET}"
      sleep $((attempt * 3))
      for f2 in $todo; do
        fetch_file "$f2" || failed="$failed $f2"
      done
    done
  fi

  local fail_count=0
  for f in $failed; do fail_count=$((fail_count + 1)); done

  # cache directory (writable by cook_cache.py at runtime)
  mkdir -p "$DEST/.agent-skills"

  # make scripts executable
  chmod +x "$DEST/scripts/cook_cache.py" \
            "$DEST/scripts/cook_compile.py" \
            "$DEST/scripts/cook_telemetry.py" \
            "$DEST/scripts/check_index_routes.py"

  echo ""
  if [[ $fail_count -gt 0 ]]; then
    echo -e "${RED}Install finished with $fail_count failed file(s):${RESET}$failed" >&2
    if [[ -z "$SRC" ]]; then
      echo -e "${RED}The CDN may still be propagating a recent push — re-run in a minute, or install from a local clone: COOK_SRC=/path/to/cook bash install.sh${RESET}" >&2
    fi
    exit 1
  fi

  local total="${#FILES[@]}"
  echo -e "${GREEN}${BOLD}Installed $total files to $DEST${RESET}"
  echo ""
  echo -e "${BOLD}Usage${RESET}"
  echo "  Ask your coding agent to run /cook (or 'cook') before any coding task."
  echo "  Cook detects your stack, loads the matching standards, and returns a"
  echo "  compiled rules payload — no manual setup required."
  echo ""
  echo -e "${BOLD}Skill path${RESET}"
  echo "  $DEST/SKILL.md"
  echo ""
  echo -e "${CYAN}Dedicated to JC ♥${RESET}"
  echo ""
}

main "$@"
