#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 || $# -gt 4 ]]; then
  echo "usage: $0 <file> <type> [issuer] [effective-date]" >&2
  exit 64
fi

source_file="$(realpath "$1")"
artifact_type="$2"
issuer="${3:-unknown}"
supplied_effective_date="${4:-}"

if [[ ! -f "$source_file" ]]; then
  echo "Artifact not found: $source_file" >&2
  exit 66
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
private_root="${MCP_PRIVATE_DATA:-/workspaces/.mcp-private/sovereignCritical}"
manifest_dir="$private_root/manifest"
manifest="$manifest_dir/artifacts.jsonl"
sha="$(sha256sum "$source_file" | awk '{print $1}')"
artifact_id="ART-${sha:0:16}"
original_name="$(basename "$source_file")"
ext=""
if [[ "$original_name" == *.* ]]; then
  ext=".${original_name##*.}"
fi

# Content-addressed storage intentionally contains no calendar partition. A file
# ingested in 2026 may describe 2023; archive layout must not invent chronology.
target_dir="$private_root/originals/sha256/${sha:0:2}/$artifact_id"
target_file="$target_dir/source$ext"
metadata_file="$target_dir/metadata.json"

install -d -m 700 "$manifest_dir" "$target_dir"

existing_record="$(python - "$manifest" "$artifact_id" <<'PY'
import json
import sys
from pathlib import Path

manifest = Path(sys.argv[1])
artifact_id = sys.argv[2]
if manifest.exists():
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if record.get("artifactId") == artifact_id:
            print(json.dumps(record, sort_keys=True))
            break
PY
)"

if [[ -n "$existing_record" ]]; then
  echo "ALREADY_PRESENT: $artifact_id"
  echo "sha256: $sha"
  python - "$existing_record" <<'PY'
import json
import sys
record = json.loads(sys.argv[1])
print(f"stored: {record.get('storedPath', 'unknown')}")
PY
  exit 0
fi

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

date_args=("$source_file")
if [[ -n "$supplied_effective_date" ]]; then
  date_args+=("--supplied-effective-date" "$supplied_effective_date")
fi
date_resolution="$(python "$script_dir/reconcile-artifact-date.py" "${date_args[@]}")"

ARTIFACT_ID="$artifact_id" \
ARTIFACT_SHA="$sha" \
ARTIFACT_TYPE="$artifact_type" \
ARTIFACT_ISSUER="$issuer" \
ARTIFACT_ORIGINAL_NAME="$original_name" \
ARTIFACT_TARGET_FILE="$target_file" \
ARTIFACT_METADATA_FILE="$metadata_file" \
ARTIFACT_MANIFEST="$manifest" \
ARTIFACT_DATE_RESOLUTION="$date_resolution" \
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
original_name = os.environ["ARTIFACT_ORIGINAL_NAME"]
target_file = Path(os.environ["ARTIFACT_TARGET_FILE"])
metadata_file = Path(os.environ["ARTIFACT_METADATA_FILE"])
manifest = Path(os.environ["ARTIFACT_MANIFEST"])
date_resolution = json.loads(os.environ["ARTIFACT_DATE_RESOLUTION"])
ingested_at = datetime.now(timezone.utc).isoformat()
resolved_date = date_resolution.get("resolvedDate")
resolved_semantic = date_resolution.get("resolvedSemantic")

entry = {
    "artifactId": artifact_id,
    "sha256": sha,
    "originalFilename": original_name,
    "storedPath": str(target_file),
    "storagePolicy": "content-addressed-sha256",
    "mimeType": mimetypes.guess_type(original_name)[0] or "application/octet-stream",
    "byteSize": target_file.stat().st_size,
    "artifactType": artifact_type,
    "issuer": issuer,
    "documentDate": resolved_date,
    "effectiveDate": resolved_date if resolved_semantic == "effective" else None,
    "dateResolution": date_resolution,
    "ingestedAt": ingested_at,
    "acquiredAt": ingested_at,
    "authorityTier": "unclassified",
    "verificationState": "Evidence Located",
    "sourceChannel": "codespace-drop-in-intake",
    "preservedOriginal": True,
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
        except (json.JSONDecodeError, KeyError) as exc:
            raise SystemExit(f"Malformed artifact manifest: {manifest}: {exc}") from exc

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
print(f"document-date: {resolved_date or 'UNRESOLVED'} ({date_resolution['state']})")
print(f"manifest: {manifest}")
PY
