#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

FOLDER_TYPES = {
    "transcripts": "transcript",
    "degree-audits": "degree-audit",
    "registration": "registration",
    "syllabi": "syllabus",
    "lms": "lms-export",
    "financial-aid": "financial-aid",
    "loans": "federal-loan-status",
    "scholarships": "scholarship-record",
    "university-account": "university-account",
    "transfer-credit": "transfer-credit-evaluation",
    "advisor-records": "advisor-record",
    "other": "unclassified",
}

IGNORED_NAMES = {".gitkeep", "README", "README.md", "README.txt"}


def artifact_type_for(path: Path, incoming: Path) -> str:
    try:
        relative = path.relative_to(incoming)
    except ValueError:
        return "unclassified"
    if len(relative.parts) < 2:
        return "unclassified"
    return FOLDER_TYPES.get(relative.parts[0].lower(), "unclassified")


def candidates(incoming: Path) -> list[Path]:
    return sorted(
        path
        for path in incoming.rglob("*")
        if path.is_file() and path.name not in IGNORED_NAMES and not path.name.startswith(".")
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ingest all private artifacts dropped into the MCP incoming tree."
    )
    parser.add_argument(
        "--incoming",
        type=Path,
        default=None,
        help="Override the private incoming directory.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show classification without ingesting files.",
    )
    args = parser.parse_args()

    private_root = Path(
        os.environ.get("MCP_PRIVATE_DATA", "/workspaces/.mcp-private/sovereignCritical")
    )
    incoming = args.incoming or private_root / "incoming"
    repo_root = Path(__file__).resolve().parents[1]
    intake = repo_root / "scripts" / "intake-artifact.sh"

    incoming.mkdir(parents=True, exist_ok=True, mode=0o700)
    files = candidates(incoming)
    if not files:
        print(f"No source artifacts found under {incoming}")
        return 0

    failures = 0
    for path in files:
        artifact_type = artifact_type_for(path, incoming)
        relative = path.relative_to(incoming)
        if args.dry_run:
            print(f"{artifact_type:28} {relative}")
            continue

        print(f"\n== {relative} [{artifact_type}] ==")
        result = subprocess.run(
            ["bash", str(intake), str(path), artifact_type],
            cwd=repo_root,
            check=False,
        )
        if result.returncode != 0:
            failures += 1

    if args.dry_run:
        return 0

    print(f"\nScanned {len(files)} artifact(s); failures: {failures}")
    if any(artifact_type_for(path, incoming) == "unclassified" for path in files):
        print(
            "NOTE: files placed directly in incoming/ or unknown subfolders remain unclassified; "
            "their bytes are preserved but classification requires later reconciliation."
        )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
