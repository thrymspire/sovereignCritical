#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 || $# -gt 4 ]]; then
  echo "usage: $0 <file> <type> [issuer] [effective-date]" >&2
  exit 64
fi

source_file="$1"
artifact_type="$2"
issuer="${3:-unknown}"
effective_date="${4:-}"

if [[ ! -f "$source_file" ]]; then
  echo "Artifact not found: $source_file" >&2
  exit 66
fi

private_root="${MCP_PRIVATE_DATA:-/workspaces/.mcp-private/sovereignCritical}"
manifest_dir="$private_root/manifest"
manifest="$manifest_dir/artifacts.jsonl"
year="$(date -u +%Y)"
sha="$(sha256sum "$source_file" | awk '{print $1}')"
artifact_id="ART-${sha:0:16}"
original_name="$(basename "$source_file")"
ext=""
if [[ "$original_name" == *.* ]]; then
  ext=".${original_name##*.}"
fi

target_dir="$private_root/originals/$year/$artifact_id"
target_file="$target_dir/source$ext"
metadata_file="$target_dir/metadata.json"

install -d -m 700 "$manifest_dir" "$target_dir"

if [[ -f "$target_file" ]]; then
  existing_sha="$(sha256sum "$target_file" | awk '{print $1}')"
  if [[ "$existing_sha" != "$sha" ]]; then
    echo "Hash collision/inconsistent artifact directory for $artifact_id" >&2
    exit 74
  fi
else
  cp -p "$source_file" "$target_file"
  chmod 600 "$target_file"
fi

ARTIFACT_ID="$artifact_id" \
ARTIFACT_SHA="$sha" \
ARTIFACT_TYPE="$artifact_type" \
ARTIFACT_ISSUER="$issuer" \
ARTIFACT_EFFECTIVE_DATE="$effective_date" \
ARTIFACT_ORIGINAL_NAME="$original_name" \
ARTIFACT_TARGET_FILE="$target_file" \
ARTIFACT_METADATA_FILE="$metadata_file" \
ARTIFACT_MANIFEST="$manifest" \
python - <<'PY'
import json
import mimetypes
import os
from datetime import datetime, timezone
from pathlib import Path

artifact_id = os.environ["ARTIFACT_ID"]
sha = os.environ["ARTIFACT_SHA"]
artifact_type = os.environ["ARTIFACT_TYPE"]
issuer = os.environ["ARTIFACT_ISSUER"]
effective_date = os.environ["ARTIFACT_EFFECTIVE_DATE"] or None
original_name = os.environ["ARTIFACT_ORIGINAL_NAME"]
target_file = Path(os.environ["ARTIFACT_TARGET_FILE"])
metadata_file = Path(os.environ["ARTIFACT_METADATA_FILE"])
manifest = Path(os.environ["ARTIFACT_MANIFEST"])

entry = {
    "artifactId": artifact_id,
    "sha256": sha,
    "originalFilename": original_name,
    "storedPath": str(target_file),
    "mimeType": mimetypes.guess_type(original_name)[0] or "application/octet-stream",
    "byteSize": target_file.stat().st_size,
    "artifactType": artifact_type,
    "issuer": issuer,
    "effectiveDate": effective_date,
    "acquiredAt": datetime.now(timezone.utc).isoformat(),
    "authorityTier": "unclassified",
    "verificationState": "Evidence Located",
    "sourceChannel": "codespace-manual-intake",
}

metadata_file.write_text(json.dumps(entry, indent=2, sort_keys=True) + "\n", encoding="utf-8")
metadata_file.chmod(0o600)

seen = set()
if manifest.exists():
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            seen.add(json.loads(line)["artifactId"])
        except (json.JSONDecodeError, KeyError):
            raise SystemExit(f"Malformed artifact manifest: {manifest}")

if artifact_id not in seen:
    with manifest.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")
    manifest.chmod(0o600)
    state = "INGESTED"
else:
    state = "ALREADY_PRESENT"

print(f"{state}: {artifact_id}")
print(f"sha256: {sha}")
print(f"stored: {target_file}")
print(f"manifest: {manifest}")
PY
