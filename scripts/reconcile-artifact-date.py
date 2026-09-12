#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree

MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}

ISO_DATE = re.compile(r"(?<!\d)(20\d{2}|19\d{2})[-_.](0?[1-9]|1[0-2])[-_.](0?[1-9]|[12]\d|3[01])(?!\d)")
US_DATE = re.compile(r"(?<!\d)(0?[1-9]|1[0-2])[/-](0?[1-9]|[12]\d|3[01])[/-]((?:19|20)\d{2})(?!\d)")
MONTH_DATE = re.compile(
    r"\b(" + "|".join(MONTHS) + r")\s+(0?[1-9]|[12]\d|3[01])(?:st|nd|rd|th)?[,]?\s+((?:19|20)\d{2})\b",
    re.IGNORECASE,
)
LABELLED = re.compile(
    r"\b(effective\s+date|issue(?:d)?\s+date|document\s+date|revision\s+date|revised\s+on|dated)\b\s*[:\-]?\s*([^\n\r]{0,48})",
    re.IGNORECASE,
)


def valid_date(year: int, month: int, day: int) -> str | None:
    try:
        return datetime(year, month, day).date().isoformat()
    except ValueError:
        return None


def first_date(text: str) -> str | None:
    match = ISO_DATE.search(text)
    if match:
        return valid_date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    match = US_DATE.search(text)
    if match:
        return valid_date(int(match.group(3)), int(match.group(1)), int(match.group(2)))
    match = MONTH_DATE.search(text)
    if match:
        return valid_date(int(match.group(3)), MONTHS[match.group(1).lower()], int(match.group(2)))
    return None


def add_candidate(candidates: list[dict], *, date: str | None, semantic: str, source: str, locator: str, confidence: float) -> None:
    if date is None:
        return
    candidate = {
        "date": date,
        "semantic": semantic,
        "source": source,
        "locator": locator[:240],
        "confidence": confidence,
    }
    key = (date, semantic, source, candidate["locator"])
    if all((item["date"], item["semantic"], item["source"], item["locator"]) != key for item in candidates):
        candidates.append(candidate)


def text_from_ooxml(path: Path) -> tuple[str, list[tuple[str, str]]]:
    text = ""
    metadata: list[tuple[str, str]] = []
    try:
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
            for name in ("word/document.xml", "xl/sharedStrings.xml"):
                if name not in names:
                    continue
                root = ElementTree.fromstring(archive.read(name))
                text += "\n" + " ".join(part.strip() for part in root.itertext() if part.strip())
            if "docProps/core.xml" in names:
                root = ElementTree.fromstring(archive.read("docProps/core.xml"))
                for element in root.iter():
                    local = element.tag.rsplit("}", 1)[-1]
                    if local in {"created", "modified"} and element.text:
                        metadata.append((local, element.text.strip()))
    except (zipfile.BadZipFile, ElementTree.ParseError, OSError):
        pass
    return text, metadata


def extract_text_and_metadata(path: Path) -> tuple[str, list[tuple[str, str]]]:
    suffix = path.suffix.lower()
    metadata: list[tuple[str, str]] = []

    if suffix == ".pdf":
        text = ""
        if shutil.which("pdftotext"):
            result = subprocess.run(
                ["pdftotext", "-f", "1", "-l", "4", str(path), "-"],
                check=False,
                capture_output=True,
                text=True,
                timeout=20,
            )
            if result.returncode == 0:
                text = result.stdout[:250_000]
        if shutil.which("pdfinfo"):
            result = subprocess.run(
                ["pdfinfo", str(path)],
                check=False,
                capture_output=True,
                text=True,
                timeout=20,
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if ":" not in line:
                        continue
                    key, value = line.split(":", 1)
                    if key.strip() in {"CreationDate", "ModDate"}:
                        metadata.append((key.strip(), value.strip()))
        return text, metadata

    if suffix in {".docx", ".xlsx", ".pptx"}:
        return text_from_ooxml(path)

    if suffix in {".txt", ".md", ".csv", ".json", ".html", ".htm", ".xml", ".ics"}:
        try:
            return path.read_text(encoding="utf-8", errors="replace")[:250_000], metadata
        except OSError:
            return "", metadata

    return "", metadata


def metadata_date(raw: str) -> str | None:
    # ISO-like OOXML timestamps are common and unambiguous.
    match = re.search(r"((?:19|20)\d{2})-(\d{2})-(\d{2})", raw)
    if match:
        return valid_date(int(match.group(1)), int(match.group(2)), int(match.group(3)))

    # PDF metadata commonly looks like: Sat Sep 12 14:30:00 2026 PDT.
    match = re.search(
        r"\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+([A-Z][a-z]{2})\s+(\d{1,2}).*?((?:19|20)\d{2})\b",
        raw,
    )
    if match:
        month_lookup = {name[:3].lower(): value for name, value in MONTHS.items()}
        month = month_lookup.get(match.group(1).lower())
        if month:
            return valid_date(int(match.group(3)), month, int(match.group(2)))
    return None


def reconcile(path: Path, supplied_effective_date: str | None) -> dict:
    candidates: list[dict] = []

    if supplied_effective_date:
        try:
            supplied = datetime.strptime(supplied_effective_date, "%Y-%m-%d").date().isoformat()
        except ValueError as exc:
            raise ValueError("supplied effective date must be YYYY-MM-DD") from exc
        add_candidate(
            candidates,
            date=supplied,
            semantic="effective",
            source="operator",
            locator="explicit intake argument",
            confidence=1.0,
        )

    filename_date = first_date(path.name)
    add_candidate(
        candidates,
        date=filename_date,
        semantic="document",
        source="filename",
        locator=path.name,
        confidence=0.80,
    )

    text, metadata = extract_text_and_metadata(path)
    for match in LABELLED.finditer(text):
        label = match.group(1).lower()
        date = first_date(match.group(2))
        semantic = "effective" if "effective" in label else "issued" if "issue" in label or label == "dated" else "document"
        confidence = 0.95 if semantic == "effective" else 0.90
        add_candidate(
            candidates,
            date=date,
            semantic=semantic,
            source="document-text",
            locator=(match.group(1) + ": " + match.group(2)).strip(),
            confidence=confidence,
        )

    for key, raw in metadata:
        add_candidate(
            candidates,
            date=metadata_date(raw),
            semantic="file-metadata",
            source="embedded-metadata",
            locator=f"{key}: {raw}",
            confidence=0.35,
        )

    strong = [candidate for candidate in candidates if candidate["confidence"] >= 0.80]
    strong_dates = sorted({candidate["date"] for candidate in strong})

    if supplied_effective_date:
        supplied_candidate = next(candidate for candidate in candidates if candidate["source"] == "operator")
        conflicting = sorted({candidate["date"] for candidate in strong if candidate["source"] != "operator" and candidate["date"] != supplied_candidate["date"]})
        state = "ambiguous" if conflicting else "resolved"
        resolved = supplied_candidate["date"] if not conflicting else None
        semantic = "effective" if resolved else None
        basis = "operator-supplied" if resolved else "operator-conflicts-with-strong-candidate"
    elif len(strong_dates) == 1:
        resolved = strong_dates[0]
        best = max((candidate for candidate in strong if candidate["date"] == resolved), key=lambda item: item["confidence"])
        state = "resolved"
        semantic = best["semantic"]
        basis = best["source"]
    elif len(strong_dates) > 1:
        resolved = None
        semantic = None
        state = "ambiguous"
        basis = "conflicting-strong-candidates"
    else:
        resolved = None
        semantic = None
        state = "unresolved"
        basis = "no-strong-date-candidate"

    return {
        "state": state,
        "resolvedDate": resolved,
        "resolvedSemantic": semantic,
        "basis": basis,
        "candidates": sorted(candidates, key=lambda item: (-item["confidence"], item["date"], item["source"])),
        "policy": "MCP-DATE/1 conservative; ingestion time is never used as document/effective date",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Conservatively reconcile an artifact's document/effective date.")
    parser.add_argument("file", type=Path)
    parser.add_argument("--supplied-effective-date", default=None)
    args = parser.parse_args()

    if not args.file.is_file():
        parser.error(f"artifact not found: {args.file}")

    try:
        result = reconcile(args.file, args.supplied_effective_date)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 64

    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
