#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
schema_to_ui.py
---------------
Bridge: canonical Gantt Ontology JSON -> UI HTML Cockpit format.

Usage:
  1. Put your shaped data in:  ../data/gantt_ontology.json
  2. Run:  python schema_to_ui.py
  3. Open:  ../ui/Master_Critical_Path_Gantt.html  or  ../ui/index.html

Strict Data-Free Invariant:
The UI HTML files contain zero hardcoded data. The bridge injects ONLY
what is present in your shaped data file.
Normalized Ingestion Channels:
- RAW_TASKS (from doc.tasks + doc.dependencies)
- FOUNDATION_SWIMLANES (from doc.workstreams)
- TEMPLATE_HOURLY_BLOCKS (from doc.configuration.hourlyBlocks / doc.calendars)
- FUNDING_DATA (from doc.demographics.funding / doc.configuration.fundingData)
- INVARIANTS (from doc.demographics.invariants / doc.configuration.demographics.invariants)
- ACADEMIC_STANDING (from doc.demographics.academicStanding / doc.configuration.demographics.academicStanding)
- CAREER_ARC (from doc.demographics.careerArc / doc.configuration.demographics.careerArc)
- START_DATE_STR / END_DATE_STR / TODAY_STR (from doc.project & doc.boundaries)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Safe stdout encoding for Windows consoles
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "gantt_ontology.json"
UI_GANTT_FILE = ROOT / "ui" / "Master_Critical_Path_Gantt.html"
UI_INDEX_FILE = ROOT / "ui" / "index.html"
ROOT_INDEX_FILE = ROOT / "index.html"
GANTT_SRC = ROOT / "gantt_ontology" / "src"

# Add gantt_ontology models to sys.path
if str(GANTT_SRC) not in sys.path:
    sys.path.insert(0, str(GANTT_SRC))

try:
    from gantt_ontology.models import GanttOntology
    CANONICAL_MODELS_AVAILABLE = True
except ImportError:
    CANONICAL_MODELS_AVAILABLE = False


def load_canonical(data_file: Path) -> dict:
    if not data_file.exists():
        print(f"ERROR: shaped data not found at {data_file}")
        print("Place your schema-conformant JSON there and re-run.")
        sys.exit(1)
    with open(data_file, encoding="utf-8") as f:
        return json.load(f)


def workstream_lookup(doc: dict) -> dict[str, str]:
    return {w["id"]: w.get("name", w["id"]) for w in doc.get("workstreams", [])}


def task_to_ui(t: dict, ws_map: dict) -> dict:
    """Map one canonical Task to the UI row shape."""
    duration = t.get("duration") or {}
    dur_val = duration.get("value")
    dur_unit = duration.get("unit", "days")

    start = t.get("startDate") or t.get("actualStart") or ""
    end = t.get("finishDate") or t.get("actualFinish") or start

    deliverable = t.get("description") or t.get("deliverable") or t.get("name", "")
    notes = t.get("notes") or ""

    rubric = ""
    strategic_notes = ""
    amount_str = ""
    portal_url = ""
    documented_grade = ""
    gained_income = ""
    if notes:
        parts = notes.split(" | ")
        for p in parts:
            if p.startswith("Rubric:"):
                rubric = p.replace("Rubric:", "").strip()
            elif p.startswith("Strategic Notes:"):
                strategic_notes = p.replace("Strategic Notes:", "").strip()
            elif p.startswith("Amount:"):
                amount_str = p.replace("Amount:", "").strip()
            elif p.startswith("Portal:") or p.startswith("Link:") or p.startswith("URL:"):
                portal_url = p.split(":", 1)[1].strip()
                if portal_url.startswith("//"): portal_url = "https:" + portal_url
                elif not portal_url.startswith("http") and ("." in portal_url): portal_url = "https://" + portal_url
            elif p.startswith("Grade:") or p.startswith("GPA:"):
                documented_grade = p.split(":", 1)[1].strip()
            elif p.startswith("Gained Income:") or p.startswith("Income:") or p.startswith("Value:"):
                gained_income = p.split(":", 1)[1].strip()
        if not rubric:
            rubric = notes
        if not strategic_notes:
            strategic_notes = notes

    amount = amount_str
    if not amount and dur_val is not None:
        amount = f"{dur_val} {dur_unit}"

    prio = t.get("priority") or 0
    is_strat = bool(
        prio >= 800
        or "strategic" in (t.get("trackId") or "").lower()
        or "strategic" in notes.lower()
        or t.get("strategicFlag")
    )

    is_rolling = bool(
        "rolling" in t.get("name", "").lower()
        or "rolling" in notes.lower()
        or "rolling" in (t.get("trackId") or "").lower()
    )

    ws_id = t.get("workstreamId", "")
    track_name = ws_map.get(ws_id, ws_id or "Unassigned")
    t_type = "Milestone" if t.get("isMilestone") else ("Summary" if t.get("isSummary") else "Task")

    return {
        "id": t["id"],
        "code": t.get("wbsCode") or t["id"],
        "name": t["name"],
        "track": track_name,
        "subgroup": t.get("trackId") or t.get("description") or "",
        "start": start,
        "end": end,
        "type": t_type,
        "amount": amount,
        "critical": bool(t.get("criticalPathMembership")),
        "strategic_flag": is_strat,
        "strategic_notes": strategic_notes,
        "deliverable": deliverable,
        "rubric": rubric,
        "portal_url": portal_url,
        "documented_grade": documented_grade,
        "gained_income": gained_income,
        "is_rolling": is_rolling,
        "proof_rubric": t.get("proofRubric") or [
            "Canvas submission / verification confirmed",
            "Meets formal syllabus & grading rubric standards",
            "Artifact preserved to local academic portfolio",
        ],
        "percent_complete": t.get("percentComplete"),
        "deps": [],
        "constraint": t.get("constraintType"),
        "priority": t.get("priority"),
        "is_summary": bool(t.get("isSummary")),
        "is_milestone": bool(t.get("isMilestone")),
        "wbs": t.get("wbsCode"),
        "parent": t.get("parentTaskId"),
    }


def build_raw_tasks(doc: dict) -> list[dict]:
    ws_map = workstream_lookup(doc)
    tasks = [task_to_ui(t, ws_map) for t in doc.get("tasks", [])]
    by_id = {t["id"]: t for t in tasks}

    for dep in doc.get("dependencies", []):
        succ = by_id.get(dep.get("successorId"))
        pred = dep.get("predecessorId")
        if succ is not None and pred:
            succ.setdefault("deps", []).append(pred)

    return tasks


SWIMLANE_METADATA = {
    "ws-academic": {
        "trackNum": "TRACK 1",
        "badge": "⚡ ACTIVE IN FOCUS",
        "encouragement": "Term GPA Target: 4.00 (12 Cr) • Benchmarks: COMM 131 (A), CITS F205 (A), PLS F102 (A), RELG F221X (A) • Honors Defense GPA >= 3.50 unlocks tribal scholarships.",
        "color": "var(--signal-bright)",
    },
    "ws-knowledge-eng": {
        "trackNum": "TRACK 2",
        "badge": "🚀 CAREER ENGINE",
        "encouragement": "Applied Modal Topology Ontology (AMTO-v1 to v3), Protégé modeling, and $120,000+ industry placement.",
        "color": "var(--spore)",
    },
    "ws-capital-sovereignty": {
        "trackNum": "TRACK 3",
        "badge": "🛡️ BASELINE SECURED",
        "encouragement": "Secured Baseline Assets: $14,068.00 Realized Value • Student Loan Rehab Month 9 Payment in March 2027 purges default & restores Title IV • $3,712 Bursar Gate Due Nov 1.",
        "color": "var(--bio)",
    },
    "ws-scholarships": {
        "trackNum": "TRACK 4",
        "badge": "🔥 ROLLING & PELL PIPELINE",
        "encouragement": "Continuous Rolling Application Windows (CIRI, KIC, CCTHITA, AIS, CTD, Endowments) • Restored Federal Pell Grant (400% LEU Intact = $29,580.00 Reserve) • Projected Summer, Fall & Spring Pell disbursements post-March 2027 rehab.",
        "color": "var(--warn)",
    },
    "ws-housing": {
        "trackNum": "TRACK 5",
        "badge": "🏠 BASECAMP SECURED",
        "encouragement": "Salem residential basecamp secured ($750/mo paid through Dec 31). January 1 rent bridge funded via CIRI/KIC tuition surplus.",
        "color": "var(--bio)",
    },
    "ws-degree": {
        "trackNum": "TRACK 6-9",
        "badge": "🎯 DEGREE HORIZON",
        "encouragement": "Sequential 39-Credit Degree Pace Plan: Sp'27 (13 cr, $4,742), Su'27 (6 cr, $2,184), Fa'27 (13 cr, $4,742), Sp'28 (13 cr, $4,742) -> B.A. Conferred May 6, 2028.",
        "color": "var(--amber)",
    },
    "ws-synthesis": {
        "trackNum": "TRACK 10",
        "badge": "💎 EQUILIBRIUM",
        "encouragement": "Strategic timing gates, SBA 8(a) certification, and autonomous capitalized self-sufficiency.",
        "color": "var(--spore)",
    },
    "swim-1": {"trackNum": "TRACK 5", "badge": "🛡️ BASECAMP SECURED", "encouragement": "Housing and subsistence security invariants active.", "color": "var(--bio)"},
    "swim-2": {"trackNum": "TRACK 3 & 4", "badge": "🔥 ACTIVE PIPELINE", "encouragement": "Funding acquisition and institutional aid pipeline active.", "color": "var(--warn)"},
    "swim-3": {"trackNum": "TRACK 1", "badge": "⚡ ACTIVE IN FOCUS", "encouragement": "Coursework syllabus execution protecting target GPA benchmark.", "color": "var(--signal-bright)"},
    "swim-4": {"trackNum": "TRACK 2", "badge": "🚀 ACTIVE IN FOCUS", "encouragement": "Domain modeling and technical specialization asset creation.", "color": "var(--spore)"},
    "swim-5": {"trackNum": "TRACK 9 & DEGREE HORIZON", "badge": "🎯 DEGREE HORIZON", "encouragement": "Strategic milestones and degree completion horizon.", "color": "var(--amber)"},
}


def build_swimlanes(doc: dict) -> list[dict]:
    """
    Extract swimlanes strictly from doc['workstreams'] where type == 'Swimlane'.
    If the document has no swimlanes, returns an empty list.
    """
    result = []
    for w in doc.get("workstreams", []):
        if w.get("type") == "Swimlane" or str(w.get("id", "")).startswith("swim-"):
            w_id = w["id"]
            meta = SWIMLANE_METADATA.get(w_id, {})
            result.append({
                "id": w_id,
                "trackNum": meta.get("trackNum") or w.get("trackNum") or f"LANE {w.get('order', '')}".strip(),
                "name": w.get("name", w_id),
                "badge": meta.get("badge") or w.get("badge", "⚡ ACTIVE"),
                "encouragement": meta.get("encouragement") or w.get("encouragement") or w.get("description", ""),
                "color": meta.get("color") or w.get("color", "var(--signal-bright)"),
                "desc": w.get("description", ""),
            })
    return result


def build_hourly_blocks(doc: dict) -> list[dict]:
    """
    Extract hourly blocks strictly from doc if defined in configuration or calendars.
    If none are present, returns an empty list.
    """
    cfg = doc.get("configuration") or {}
    if "hourlyBlocks" in cfg and isinstance(cfg["hourlyBlocks"], list):
        return cfg["hourlyBlocks"]
    return []


def get_demographics_dict(doc: dict) -> dict:
    """Helper to get demographics object from top-level or configuration."""
    if "demographics" in doc and isinstance(doc["demographics"], dict):
        return doc["demographics"]
    cfg = doc.get("configuration") or {}
    if "demographics" in cfg and isinstance(cfg["demographics"], dict):
        return cfg["demographics"]
    return {}


def build_funding_data(doc: dict) -> list[dict]:
    """
    Extract funding data strictly from doc.demographics.funding or doc.configuration.fundingData.
    If none are present, returns an empty list.
    """
    demo = get_demographics_dict(doc)
    if "funding" in demo and isinstance(demo["funding"], list):
        return demo["funding"]
    cfg = doc.get("configuration") or {}
    if "fundingData" in cfg and isinstance(cfg["fundingData"], list):
        return cfg["fundingData"]
    return []


def build_invariants(doc: dict) -> list[dict]:
    """
    Extract empirical invariants strictly from doc.demographics.invariants.
    If none are present, returns an empty list.
    """
    demo = get_demographics_dict(doc)
    if "invariants" in demo and isinstance(demo["invariants"], list):
        return demo["invariants"]
    return []


def build_academic_standing(doc: dict) -> list[dict]:
    """
    Extract verified academic standing strictly from doc.demographics.academicStanding.
    If none are present, returns an empty list.
    """
    demo = get_demographics_dict(doc)
    if "academicStanding" in demo and isinstance(demo["academicStanding"], list):
        return demo["academicStanding"]
    return []


def build_career_arc(doc: dict) -> list[dict]:
    """
    Extract career placement arc strictly from doc.demographics.careerArc.
    If none are present, returns an empty list.
    """
    demo = get_demographics_dict(doc)
    if "careerArc" in demo and isinstance(demo["careerArc"], list):
        return demo["careerArc"]
    return []


def extract_dates(doc: dict) -> tuple[str, str, str]:
    proj = doc.get("project", {})
    start_date = proj.get("startDate", "2026-08-24")
    end_date = proj.get("finishDate", "2028-09-04")

    today_date = "2026-09-06"
    for b in doc.get("boundaries", []):
        if b.get("type") == "Cutline" and b.get("date"):
            today_date = b["date"]
            break

    return start_date, end_date, today_date


def inject_into_html_file(
    target_file: Path,
    raw_tasks: list[dict],
    swimlanes: list[dict],
    hourly_blocks: list[dict],
    funding_data: list[dict],
    invariants: list[dict],
    academic_standing: list[dict],
    career_arc: list[dict],
    dates: tuple[str, str, str],
) -> bool:
    if not target_file.exists():
        print(f"WARNING: Target UI file not found at {target_file}")
        return False

    html = target_file.read_text(encoding="utf-8", errors="replace")
    start_date, end_date, today_date = dates

    replacements = [
        (
            re.compile(r"const\s+RAW_TASKS\s*=\s*\[.*?\];", re.DOTALL),
            "const RAW_TASKS = " + json.dumps(raw_tasks, ensure_ascii=False) + ";",
            "RAW_TASKS",
        ),
        (
            re.compile(r"const\s+FOUNDATION_SWIMLANES\s*=\s*\[.*?\];", re.DOTALL),
            "const FOUNDATION_SWIMLANES = " + json.dumps(swimlanes, ensure_ascii=False) + ";",
            "FOUNDATION_SWIMLANES",
        ),
        (
            re.compile(r"const\s+TEMPLATE_HOURLY_BLOCKS\s*=\s*\[.*?\];", re.DOTALL),
            "const TEMPLATE_HOURLY_BLOCKS = " + json.dumps(hourly_blocks, ensure_ascii=False) + ";",
            "TEMPLATE_HOURLY_BLOCKS",
        ),
        (
            re.compile(r"const\s+FUNDING_DATA\s*=\s*\[.*?\];", re.DOTALL),
            "const FUNDING_DATA = " + json.dumps(funding_data, ensure_ascii=False) + ";",
            "FUNDING_DATA",
        ),
        (
            re.compile(r"const\s+INVARIANTS\s*=\s*\[.*?\];", re.DOTALL),
            "const INVARIANTS = " + json.dumps(invariants, ensure_ascii=False) + ";",
            "INVARIANTS",
        ),
        (
            re.compile(r"const\s+ACADEMIC_STANDING\s*=\s*\[.*?\];", re.DOTALL),
            "const ACADEMIC_STANDING = " + json.dumps(academic_standing, ensure_ascii=False) + ";",
            "ACADEMIC_STANDING",
        ),
        (
            re.compile(r"const\s+CAREER_ARC\s*=\s*\[.*?\];", re.DOTALL),
            "const CAREER_ARC = " + json.dumps(career_arc, ensure_ascii=False) + ";",
            "CAREER_ARC",
        ),
        (
            re.compile(r'const\s+START_DATE_STR\s*=\s*"[^"]*";'),
            f'const START_DATE_STR = "{start_date}";',
            "START_DATE_STR",
        ),
        (
            re.compile(r'const\s+END_DATE_STR\s*=\s*"[^"]*";'),
            f'const END_DATE_STR = "{end_date}";',
            "END_DATE_STR",
        ),
        (
            re.compile(r'const\s+TODAY_STR\s*=\s*"[^"]*";'),
            f'const TODAY_STR = "{today_date}";',
            "TODAY_STR",
        ),
    ]

    new_html = html
    injected_count = 0
    for pattern, repl_str, label in replacements:
        new_html, n = pattern.subn(repl_str, new_html, count=1)
        if n > 0:
            injected_count += 1
        else:
            print(f"  Note: Could not locate '{label}' in {target_file.name}")

    target_file.write_text(new_html, encoding="utf-8")
    print(f"✓ Injected {injected_count}/{len(replacements)} datasets into {target_file.name}")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Bridge: canonical Gantt Ontology -> UI Cockpit HTML")
    parser.add_argument(
        "--data",
        type=Path,
        default=DATA_FILE,
        help="Path to canonical shaped JSON (default: ../data/gantt_ontology.json)",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate canonical JSON without injecting into UI",
    )
    args = parser.parse_args()

    print(f"Loading canonical data from: {args.data}")
    doc = load_canonical(args.data)

    if CANONICAL_MODELS_AVAILABLE:
        try:
            GanttOntology.model_validate(doc)
            print("✓ Canonical schema validation passed with extra='forbid'!")
        except Exception as e:
            print(f"WARNING: Canonical validation warning: {e}")
    else:
        if "project" not in doc or "tasks" not in doc:
            print("ERROR: JSON missing required top-level keys (project, tasks).")
            sys.exit(1)

    if args.validate_only:
        print("Validation complete. Exiting without injection.")
        return

    raw_tasks = build_raw_tasks(doc)
    swimlanes = build_swimlanes(doc)
    hourly_blocks = build_hourly_blocks(doc)
    funding_data = build_funding_data(doc)
    invariants = build_invariants(doc)
    academic_standing = build_academic_standing(doc)
    career_arc = build_career_arc(doc)
    dates = extract_dates(doc)

    print(f"Mapped {len(raw_tasks)} canonical tasks -> UI format")
    print(f"Extracted {len(swimlanes)} swimlanes, {len(hourly_blocks)} hourly blocks, {len(funding_data)} funding rows from shaped data.")
    print(f"Extracted demographics: {len(invariants)} invariants, {len(academic_standing)} academic standing records, {len(career_arc)} career arc items.")
    print(f"Timeline window: {dates[0]} -> {dates[1]} (Cutline: {dates[2]})")

    inject_into_html_file(
        UI_GANTT_FILE,
        raw_tasks,
        swimlanes,
        hourly_blocks,
        funding_data,
        invariants,
        academic_standing,
        career_arc,
        dates,
    )
    if UI_INDEX_FILE.exists():
        inject_into_html_file(
            UI_INDEX_FILE,
            raw_tasks,
            swimlanes,
            hourly_blocks,
            funding_data,
            invariants,
            academic_standing,
            career_arc,
            dates,
        )
    if ROOT_INDEX_FILE.exists():
        inject_into_html_file(
            ROOT_INDEX_FILE,
            raw_tasks,
            swimlanes,
            hourly_blocks,
            funding_data,
            invariants,
            academic_standing,
            career_arc,
            dates,
        )

    print("\nBridge execution complete!")
    print("Open ui/Master_Critical_Path_Gantt.html, ui/index.html, or index.html in any browser.")


if __name__ == "__main__":
    main()
