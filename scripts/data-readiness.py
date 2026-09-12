#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path

CORE_REQUIREMENTS = {
    "transcript": {"transcript", "official-transcript", "unofficial-transcript"},
    "degree-audit": {"degree-audit", "degree_audit"},
    "registration": {"registration", "course-registration", "fall-2026-registration"},
    "syllabus": {"syllabus"},
    "financial-aid": {"financial-aid", "financial-aid-award", "financial-aid-status"},
    "federal-loan-status": {"federal-loan-status", "loan-status", "rehabilitation-status"},
}

OPTIONAL_IF_APPLICABLE = {
    "scholarship": {
        "scholarship",
        "scholarship-record",
        "scholarship-application",
        "scholarship-award",
    }
}


def load_manifest(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records: list[dict] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Malformed JSON at {path}:{number}: {exc}") from exc
        if "artifactId" not in record or "artifactType" not in record:
            raise SystemExit(f"Missing artifactId/artifactType at {path}:{number}")
        records.append(record)
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description="Report MCP private-source data readiness.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()

    private_root = Path(
        os.environ.get("MCP_PRIVATE_DATA", "/workspaces/.mcp-private/sovereignCritical")
    )
    manifest = private_root / "manifest" / "artifacts.jsonl"
    records = load_manifest(manifest)
    types = Counter(str(r["artifactType"]).strip().lower() for r in records)

    core_status = {
        name: any(types[alias] > 0 for alias in aliases)
        for name, aliases in CORE_REQUIREMENTS.items()
    }
    optional_status = {
        name: any(types[alias] > 0 for alias in aliases)
        for name, aliases in OPTIONAL_IF_APPLICABLE.items()
    }

    result = {
        "privateRoot": str(private_root),
        "manifest": str(manifest),
        "artifactCount": len(records),
        "artifactTypes": dict(sorted(types.items())),
        "core": core_status,
        "optionalIfApplicable": optional_status,
        "coreReady": all(core_status.values()),
        "notes": [
            "Syllabus presence is necessary but not sufficient; active-course count must be reconciled against registration after parsing.",
            "Scholarship artifacts are required when a scholarship is being pursued, relied upon, or used in funding projections.",
            "Presence means the source has been ingested, not that its assertions are institutionally verified.",
        ],
    }

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("Master Critical Path data readiness")
        print(f"  manifest: {manifest}")
        print(f"  artifacts: {len(records)}")
        for name, present in core_status.items():
            print(f"  {'READY' if present else 'MISSING':7} {name}")
        for name, present in optional_status.items():
            print(f"  {'PRESENT' if present else 'IF-APPLICABLE':13} {name}")
        print(f"\n  core source bundle ready: {'YES' if result['coreReady'] else 'NO'}")
        print("  verification ready: NO until ingestion/parsing/corroboration completes")

    return 0 if result["coreReady"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
