#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
hook_dir="$(git -C "$repo_root" rev-parse --git-path hooks)"
mkdir -p "$hook_dir"

cat > "$hook_dir/pre-push" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
repo_root="$(git rev-parse --show-toplevel)"
exec bash "$repo_root/scripts/live-audit.sh" --pre-push
EOF
chmod 700 "$hook_dir/pre-push"

echo "Installed MCP pre-push audit hook at $hook_dir/pre-push"
