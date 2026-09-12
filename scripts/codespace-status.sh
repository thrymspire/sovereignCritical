#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

branch="$(git branch --show-current)"
private_root="${MCP_PRIVATE_DATA:-/workspaces/.mcp-private/sovereignCritical}"
manifest="$private_root/manifest/artifacts.jsonl"

printf '\nMaster Critical Path workstation\n'
printf '  branch: %s\n' "$branch"
printf '  head:   %s\n' "$(git rev-parse --short=12 HEAD)"
printf '  data:   %s\n' "$private_root"
printf '  tree:   %s\n' "$(if [[ -z "$(git status --porcelain)" ]]; then echo clean; else echo dirty; fi)"

if [[ -f "$manifest" ]]; then
  count="$(grep -cve '^[[:space:]]*$' "$manifest" || true)"
  printf '  artifacts manifested: %s\n' "$count"
else
  printf '  artifacts manifested: 0\n'
fi

printf '  audit command: bash scripts/live-audit.sh --full\n'
printf '  intake command: bash scripts/intake-artifact.sh <file> <type> [issuer] [effective-date]\n\n'
