# Master Critical Path Baseline Audit

**Audit date:** 2026-09-12  
**Repository:** `thrymspire/sovereignCritical`  
**Default branch:** `main`  
**Baseline HEAD:** `9e15068d453284e027cf6413ef9fc2871ee17f70`  
**Baseline tree:** `2f1869208ecad26727ac958eecacb929e62bb366`  
**Untouched baseline branch:** `project-owners/master-critical-path-baseline-2026-09-12`  
**Working branch:** `project-owners/master-critical-path-v1`

## 1. Baseline Preservation

The baseline branch was created directly from `main` at commit `9e15068d453284e027cf6413ef9fc2871ee17f70` before project-owner implementation changes.

The baseline branch is a preservation branch and must remain untouched.

All project-owner engineering changes begin on `project-owners/master-critical-path-v1`.

## 2. Repository Inventory

Observed repository structure at baseline:

```text
.gitignore
.nojekyll
README.md
bridge/
  schema_to_ui.py
data/
  gantt_ontology.json
gantt_ontology/
  README.md
  pyproject.toml
  schema/
    gantt_ontology_schema.json
  src/gantt_ontology/
    __init__.py
    models.py
  uv.lock
index.html
linkedin.html
ui/
  Master_Critical_Path_Gantt.html
  index.html
```

Binary image assets are also present at repository root and under `ui/`.

## 3. Existing Architecture

### 3.1 Canonical data

`data/gantt_ontology.json` is the current shaped data document. It identifies schema version `1.0.0`, project ID `mcp-project-sovereign`, and a hybrid scheduling model.

Under the owner-approved truth policy, all domain assertions in this file are **provisional until corroborated**, regardless of the labels currently embedded in the data.

### 3.2 Canonical schema / model package

`gantt_ontology/` provides:

- JSON Schema;
- Pydantic models;
- serialization/validation shape;
- task, dependency, resource, workstream, boundary, baseline, configuration, demographic, and funding structures.

The package documentation explicitly states that it has no ingestion/ETL layer and is intended as a target normalization shape.

### 3.3 Bridge

`bridge/schema_to_ui.py` currently:

1. reads `data/gantt_ontology.json`;
2. optionally validates against the Pydantic model;
3. maps canonical tasks/workstreams/configuration into UI-specific JavaScript structures;
4. performs regex replacement inside static HTML output files;
5. rewrites three HTML targets.

### 3.4 UI

The production UI is currently a giant single-file browser application.

At the baseline commit:

- `index.html`
- `ui/index.html`
- `ui/Master_Critical_Path_Gantt.html`

all resolve to the **same Git blob SHA**: `2dd1e58cf4e06d2ea086733764b091a5e39cda48`.

This indicates three duplicated deployment paths for one generated artifact.

The README describes the visual system as an Alien Purple / Material 3-inspired single-file cockpit that can be opened directly from disk without a local web server.

## 4. Confirmed Baseline Defects / Contract Violations

### DEFECT-001 — Legacy data is represented as authoritative without provenance

The current schema/model has no first-class `Evidence`, `Source`, `Assertion`, provenance lineage, contradiction state, or verification-state graph.

Repository searches for `provenance` and `Evidence` return no implementation matches at baseline.

**Consequence:** important facts cannot currently answer, in machine-readable form, “what source proves this?”

**Required direction:** introduce source/evidence/assertion lineage before promoting legacy facts beyond provisional state.

### DEFECT-002 — README and canonical data contradict each other about the active course set

The README presents a Fall 2026 active-course set containing:

- `COMM F180X`
- `PHIL F102X`
- `PLS F101`
- `RELG F110X`

The canonical JSON instead defines the Academic workstream around:

- `COMM 131`
- `CITS F205`
- `PLS F102`
- `RELG F221X`

and begins task records using those latter course identities.

**Consequence:** the repository cannot currently be treated as one authoritative source of truth.

**Required direction:** preserve both claims as conflicting provisional assertions until institutional records identify the applicable courses/term.

### DEFECT-003 — “Strict data-free architecture” is false at the bridge boundary

The README says the UI contains zero hardcoded data and that all operational data is dynamically injected from the canonical ontology.

However, `bridge/schema_to_ui.py` contains hardcoded `SWIMLANE_METADATA` and `DEFAULT_TEMPLATE_HOURLY_BLOCKS` populated with domain-specific facts and claims, including course identities, debt values, funding values, housing narrative, GPA goals, and dated outcomes.

**Consequence:** domain truth exists outside the purported canonical data source and can diverge silently.

**Required direction:** remove domain facts from executable bridge code. Defaults must be structural only. Domain content belongs in provenance-aware data.

### DEFECT-004 — Validation failure does not fail the validation command

The bridge wraps `GanttOntology.model_validate(doc)` in `try/except`, prints a `WARNING` on validation failure, and continues. When invoked with `--validate-only`, it then prints completion and returns normally.

**Consequence:** repository governance says changes to `main` should pass `python bridge/schema_to_ui.py --validate-only`, but malformed canonical data can produce a warning while the process still exits successfully.

**Required direction:** schema-validation failure must exit non-zero. Warnings must be reserved for non-fatal conditions.

### DEFECT-005 — `TODAY_STR` has a stale executable fallback

`extract_dates()` defaults the cutline/today value to `2026-09-06` when no Cutline boundary is found.

**Consequence:** missing data can silently manufacture an incorrect “today” state.

**Required direction:** current time must come from a platform clock service or an explicit evidence/state boundary. A hardcoded historical fallback is invalid.

### DEFECT-006 — UI generation mutates three duplicate large HTML files

The bridge rewrites `ui/Master_Critical_Path_Gantt.html`, `ui/index.html`, and root `index.html` through regex replacement.

**Consequence:** build output is duplicated, diffs become enormous, and data is compiled into presentation artifacts rather than resolved through a clean runtime data boundary.

**Required direction:** preserve existing behavior until replacement is validated, then move toward a packaged desktop runtime with one UI source and a versioned domain/persistence boundary.

### DEFECT-007 — No repository tests were present in the baseline tree

`pyproject.toml` lists `pytest` and `jsonschema` as development dependencies, but the recursive baseline tree contains no test directory or test modules.

**Consequence:** graph integrity, import idempotency, contradiction detection, contract propagation, validation behavior, and UI/data boundaries are not presently protected by automated repository tests.

**Required direction:** tests become mandatory as ontology and boundary behavior are normalized.

### DEFECT-008 — Scholarship concepts are represented primarily as prose/tasks/funding rows rather than criteria contracts

Scholarship references exist in README text, task notes, funding data, and workstreams, but the canonical model has no first-class Scholarship, ScholarshipCriterion, ScholarshipApplication, RequiredDocument, or eligibility-rule entities.

**Consequence:** deadlines and eligibility cannot yet propagate rigorously from grades, enrollment, documentation, or institutional changes.

**Required direction:** model scholarship criteria and required paperwork as explicit nodes/contracts before relying on funding projections.

### DEFECT-009 — Syllabus references exist but there is no syllabus ingestion model

Syllabus-related text appears in tasks and bridge defaults, while the ontology package explicitly omits ingestion.

**Consequence:** course assignment/deadline data cannot currently be dropped in as an auditable source artifact and deterministically mapped to course tasks.

**Required direction:** introduce source-preserving adapters plus CourseOffering, Syllabus, Assignment, Assessment, LearningObjective, and extraction provenance.

## 5. Claims Not Yet Accepted as Truth

The following classes of legacy claims require corroboration before authoritative use:

- course enrollment/course identity;
- completed assignments and percent-complete values;
- grades and GPA assertions;
- degree audit/remaining-credit assertions;
- commencement/conferral dates;
- tuition amounts/rates;
- student-loan balances, rehabilitation status, payment schedule, and legal effects;
- Pell lifetime eligibility and projected grant values;
- scholarship amounts, eligibility, windows, and projected totals;
- housing status and funding bridges;
- career compensation projections;
- any assertion labeled “secured”, “verified”, “baseline asset”, “guaranteed”, “mandate”, “unlocked”, or equivalent without attached evidence.

These records remain useful as **claims to investigate**, not as authoritative truth.

## 6. Existing Strengths Worth Preserving

The baseline contains several useful structural ideas:

- an explicit task/dependency graph rather than a plain todo list;
- Pydantic plus JSON Schema validation intent;
- workstream/swim-lane concepts;
- scheduling constraints and dependency types;
- a direct-from-disk UI execution path;
- a clear separation, at least conceptually, between canonical data shape and UI rendering;
- Git branch governance intent;
- a data-driven direction rather than manual UI-only editing.

The project-owner architecture should preserve these strengths while repairing provenance, truth status, evidence, boundary propagation, importability, and packaging.

## 7. Phase 0 Exit Criteria

Phase 0 is considered complete when:

- untouched baseline branch exists;
- working branch exists;
- baseline SHA/tree are recorded;
- architecture is inventoried;
- known initial defects are recorded;
- constitution is committed;
- proof-of-work record exists;
- no application behavior has been altered before the baseline record.

## 8. Current Watermark

`MCP-WM/1.1 | baseline:9e15068d453284e027cf6413ef9fc2871ee17f70 | branch:project-owners/master-critical-path-v1 | phase:BASELINE-AUDIT | decision:OWNER-CLARIFICATIONS-ACCEPTED | evidence:LEGACY-PROVISIONAL | critical:TRUTH-AUDIT | drift:0 | checkpoint:2026-09-12T13:41-07:00`

## 9. Next Critical Action

Begin **Phase 1: Truth Audit** without changing legacy claim values prematurely.

The first engineering target should be the truth/evidence envelope around existing data, because correcting UI presentation before the system can distinguish fact from claim would merely make contradictions easier to admire.
