#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

expected_branch="${MCP_WORKING_BRANCH:-project-owners/master-critical-path-codespace}"
branch="$(git branch --show-current)"
if [[ "$branch" != "$expected_branch" ]]; then
  echo "Refusing workstation bootstrap on '$branch'; expected '$expected_branch'." >&2
  echo "Create/open the Codespace from the working branch, not main or the preserved baseline." >&2
  exit 64
fi

private_root="${MCP_PRIVATE_DATA:-/workspaces/.mcp-private/sovereignCritical}"
install -d -m 700 \
  "$private_root/incoming" \
  "$private_root/incoming/transcripts" \
  "$private_root/incoming/degree-audits" \
  "$private_root/incoming/registration" \
  "$private_root/incoming/syllabi" \
  "$private_root/incoming/lms" \
  "$private_root/incoming/financial-aid" \
  "$private_root/incoming/loans" \
  "$private_root/incoming/scholarships" \
  "$private_root/incoming/university-account" \
  "$private_root/incoming/transfer-credit" \
  "$private_root/incoming/advisor-records" \
  "$private_root/incoming/other" \
  "$private_root/originals" \
  "$private_root/normalized" \
  "$private_root/quarantine" \
  "$private_root/exports" \
  "$private_root/backups" \
  "$private_root/audit" \
  "$private_root/manifest"

if [[ -e "$repo_root/.mcp-data" && ! -L "$repo_root/.mcp-data" ]]; then
  echo ".mcp-data exists and is not a symlink; refusing to replace it." >&2
  exit 65
fi
ln -sfn "$private_root" "$repo_root/.mcp-data"

python -m venv "$repo_root/gantt_ontology/.venv"
"$repo_root/gantt_ontology/.venv/bin/python" -m pip install --upgrade pip
(
  cd "$repo_root/gantt_ontology"
  .venv/bin/python -m pip install -e '.[dev]'
)

(
  cd "$repo_root/app"
  npm install --package-lock=false --no-audit --no-fund
)

cargo fetch --manifest-path "$repo_root/app/src-tauri/Cargo.toml"

bash "$repo_root/scripts/install-git-hooks.sh"
bash "$repo_root/scripts/live-audit.sh" --bootstrap

cat <<EOF

MCP Codespace bootstrap complete.
Private artifact vault: $private_root
Working branch: $branch

Drop source files under:
  $repo_root/.mcp-data/incoming/

Preferred typed folders:
  transcripts/ degree-audits/ registration/ syllabi/ lms/
  financial-aid/ loans/ scholarships/ university-account/
  transfer-credit/ advisor-records/ other/

Then scan all dropped files with:
  python scripts/intake-dropbox.py

Dates are reconciled from source evidence and metadata. Ingestion time is recorded
separately and is never substituted for a document/effective date.
EOF
