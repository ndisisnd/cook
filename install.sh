#!/usr/bin/env bash
# cook install script
# Usage: curl -fsSL https://raw.githubusercontent.com/ndisisnd/cook/main/install.sh | bash
# Override destination: COOK_DIR=~/.claude/skills/cook bash install.sh

set -euo pipefail

REPO="https://raw.githubusercontent.com/ndisisnd/cook/main"
DEST="${COOK_DIR:-$HOME/.claude/skills/cook}"

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

FILES=(
  SKILL.md
  refs/protocol-cook.md
  vocab/intent-vocabulary.json
  vocab/tag-vocabulary.json
  scripts/cook_cache.py
  scripts/cook_compile.py
  scripts/check_index_routes.py
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
  standards/graphql/refs/performance.md
  standards/graphql/refs/schema-design.md
  standards/graphql/refs/security.md
  standards/graphql/refs/testing.md
  standards/graphql/refs/tooling.md
  standards/macos/SKILL.md
  standards/macos/_INDEX.md
  standards/macos/refs/architecture-and-state.md
  standards/macos/refs/distribution.md
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
  standards/swift/refs/memory-management.md
  standards/swift/refs/performance.md
  standards/swift/refs/testing.md
  standards/swift/refs/tooling.md
  standards/typescript/SKILL.md
  standards/typescript/_INDEX.md
  standards/typescript/refs/security.md
  standards/typescript/refs/testing.md
  standards/typescript/refs/tooling.md
)

check_deps() {
  if ! command -v curl &>/dev/null; then
    echo -e "${RED}Error: curl is required but not found.${RESET}" >&2
    exit 1
  fi
  if ! command -v python3 &>/dev/null; then
    echo -e "${RED}Error: python3 is required but not found.${RESET}" >&2
    exit 1
  fi
}

download_file() {
  local rel="$1"
  local url="$REPO/$rel"
  local dest="$DEST/$rel"
  mkdir -p "$(dirname "$dest")"
  if ! curl -fsSL "$url" -o "$dest"; then
    echo -e "${RED}  ✗ Failed: $rel${RESET}" >&2
    return 1
  fi
  echo -e "  ${GREEN}✓${RESET} $rel"
}

main() {
  check_deps

  echo -e "\n${BOLD}cook installer${RESET}"
  echo -e "Destination: ${CYAN}$DEST${RESET}\n"

  if [[ -d "$DEST" && -f "$DEST/SKILL.md" ]]; then
    echo -e "Updating existing install at ${CYAN}$DEST${RESET}\n"
  fi

  local failed=0
  for f in "${FILES[@]}"; do
    download_file "$f" || ((failed++))
  done

  # cache directory (writable by cook_cache.py at runtime)
  mkdir -p "$DEST/.agent-skills"

  # make scripts executable
  chmod +x "$DEST/scripts/cook_cache.py" \
            "$DEST/scripts/cook_compile.py" \
            "$DEST/scripts/check_index_routes.py"

  echo ""
  if [[ $failed -gt 0 ]]; then
    echo -e "${RED}Install finished with $failed failed file(s). Check your network and try again.${RESET}"
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
