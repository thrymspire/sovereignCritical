#!/usr/bin/env bash
set -euo pipefail

mode="${1:---full}"
repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

case "$mode" in
  --bootstrap|--pre-push|--full) full=1 ;;
  --ci) full=0 ;;
  *) echo "usage: $0 [--bootstrap|--pre-push|--full|--ci]" >&2; exit 64 ;;
esac

audit_dir="${MCP_AUDIT_DIR:-$repo_root/.mcp-audit}"
mkdir -p "$audit_dir"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
report="$audit_dir/audit-$timestamp.log"

exec > >(tee -a "$report") 2>&1

failures=0
check() {
  local label="$1"
  shift
  printf '\n== %s ==\n' "$label"
  if "$@"; then
    echo "PASS: $label"
  else
    echo "FAIL: $label"
    failures=$((failures + 1))
  fi
}

branch="$(git branch --show-current)"
head="$(git rev-parse HEAD)"
printf 'MCP LIVE AUDIT\n'
printf 'timestamp: %s\nbranch: %s\nhead: %s\nmode: %s\n' "$timestamp" "$branch" "$head" "$mode"

branch_guard() {
  case "$branch" in
    project-owners/master-critical-path-v1|project-owners/master-critical-path-codespace) return 0 ;;
    *) echo "Audit refuses pushes from unexpected branch: $branch"; return 1 ;;
  esac
}

no_private_artifacts_tracked() {
  local hit
  hit="$(git ls-files | grep -E '(^|/)(\.mcp-data|\.mcp-audit|mcp-private|private-artifacts|artifact-vault|evidence/originals|archive/originals)(/|$)' || true)"
  if [[ -n "$hit" ]]; then
    echo "Private artifact paths are tracked by Git:"
    echo "$hit"
    return 1
  fi
  return 0
}

required_repo_contracts() {
  local missing=0
  for path in \
    docs/MASTER_CRITICAL_PATH_CONSTITUTION.md \
    docs/BASELINE_AUDIT.md \
    docs/CODESPACE_OPERATIONS.md \
    gantt_ontology/pyproject.toml \
    app/package.json \
    .devcontainer/devcontainer.json \
    scripts/intake-artifact.sh \
    scripts/intake-dropbox.py \
    scripts/reconcile-artifact-date.py \
    scripts/data-readiness.py; do
    if [[ ! -e "$path" ]]; then
      echo "missing: $path"
      missing=1
    fi
  done
  return "$missing"
}

clean_tree() {
  [[ -z "$(git status --porcelain)" ]]
}

intake_selftest() {
  local tmp manifest count
  tmp="$(mktemp -d)"
  printf 'historical source fixture\n' > "$tmp/record-2023-04-05.txt"

  MCP_PRIVATE_DATA="$tmp/vault" bash scripts/intake-artifact.sh \
    "$tmp/record-2023-04-05.txt" self-test "MCP CI" >/dev/null
  MCP_PRIVATE_DATA="$tmp/vault" bash scripts/intake-artifact.sh \
    "$tmp/record-2023-04-05.txt" self-test "MCP CI" >/dev/null

  manifest="$tmp/vault/manifest/artifacts.jsonl"
  count="$(grep -cve '^[[:space:]]*$' "$manifest" || true)"
  if [[ "$count" -ne 1 ]]; then
    echo "Expected one idempotent manifest entry, found $count"
    rm -rf "$tmp"
    return 1
  fi

  if ! python - "$manifest" <<'PY'
import json
import sys
from pathlib import Path
record = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8").strip())
assert record["documentDate"] == "2023-04-05", record
assert record["dateResolution"]["state"] == "resolved", record
assert record["storagePolicy"] == "content-addressed-sha256", record
assert "/originals/sha256/" in record["storedPath"], record
assert record["ingestedAt"] != record["documentDate"], record
PY
  then
    echo "Date reconciliation/content-addressed intake self-test failed"
    rm -rf "$tmp"
    return 1
  fi

  rm -rf "$tmp"
  return 0
}

check "working branch guard" branch_guard
check "no whitespace errors" git diff --check HEAD
check "private source artifacts excluded from Git" no_private_artifacts_tracked
check "required repository contracts present" required_repo_contracts
check "intake Python tools compile" python -m py_compile scripts/data-readiness.py scripts/intake-dropbox.py scripts/reconcile-artifact-date.py
check "artifact intake is idempotent and date-safe" intake_selftest

if command -v shellcheck >/dev/null 2>&1; then
  check "shell scripts pass shellcheck" shellcheck scripts/codespace-bootstrap.sh scripts/codespace-status.sh scripts/install-git-hooks.sh scripts/live-audit.sh scripts/intake-artifact.sh
fi

if [[ "$full" -eq 1 ]]; then
  if [[ ! -x gantt_ontology/.venv/bin/python ]]; then
    echo "Missing gantt_ontology/.venv. Run scripts/codespace-bootstrap.sh first."
    failures=$((failures + 1))
  else
    check "ontology tests" bash -lc 'cd gantt_ontology && .venv/bin/pytest -q'
    check "legacy canonical ontology validates" bash -lc 'cd gantt_ontology && .venv/bin/python - <<"PY"
import json
from pathlib import Path
from gantt_ontology import GanttOntology
p = Path("../data/gantt_ontology.json")
GanttOntology.model_validate(json.loads(p.read_text(encoding="utf-8")))
print("Legacy canonical ontology validates strictly.")
PY'
    check "MCP schema generation" bash -lc 'cd gantt_ontology && .venv/bin/python tools/export_mcp_schema.py'
    check "MCP JSON Schema syntax" bash -lc 'cd gantt_ontology && .venv/bin/python - <<"PY"
import json
from pathlib import Path
from jsonschema import Draft202012Validator
p = Path("schema/mcp_domain_schema.json")
Draft202012Validator.check_schema(json.loads(p.read_text(encoding="utf-8")))
print("MCP JSON Schema is valid Draft 2020-12.")
PY'
  fi

  if [[ ! -d app/node_modules ]]; then
    echo "Missing app/node_modules. Run scripts/codespace-bootstrap.sh first."
    failures=$((failures + 1))
  else
    check "frontend production build" bash -lc 'cd app && npm run build'
  fi

  check "Tauri Rust shell" cargo check --manifest-path app/src-tauri/Cargo.toml

  if [[ "$mode" == "--pre-push" ]]; then
    check "pre-push tree is clean" clean_tree
  fi
fi

printf '\nMCP-WM/AUDIT | branch:%s | head:%s | mode:%s | failures:%s | checkpoint:%s\n' \
  "$branch" "${head:0:12}" "$mode" "$failures" "$timestamp"
printf 'report: %s\n' "$report"

if [[ "$failures" -ne 0 ]]; then
  exit 1
fi
