# Master Critical Path Architecture

**Status:** Working architecture for `project-owners/master-critical-path-v1`  
**Baseline:** `9e15068d453284e027cf6413ef9fc2871ee17f70`  
**Primary runtime target:** Tauri 2 desktop on Windows, Linux, and macOS  
**Future platform target:** Android through shared domain contracts and platform-specific adapters

## 1. Architectural Objective

Master Critical Path is an evidence-backed operational system, not a dashboard whose rendered state becomes truth.

The architecture separates five concerns that the baseline repository mixed together:

1. **source artifacts** — immutable material that says something;
2. **evidence** — an identified field/passage/value located in a source;
3. **assertions** — atomic claims with authority and verification state;
4. **rules/contracts** — deterministic or review-gated consequences of admissible assertions;
5. **presentation** — views of current operational state, never the authority for that state.

A UI control cannot directly manufacture an institutionally verified fact. A parser cannot verify its own extraction. A generated suggestion cannot become an assertion merely because it is useful.

## 2. System Context

```text
Institutional / user-provided artifacts
        │
        ▼
Source-preserving import adapters
        │
        ├── original artifact + SHA-256
        ├── field-level evidence
        └── provisional import candidates
        │
        ▼
Truth / provenance domain
Source → Evidence → Assertion → Derivation
        │
        ├── contradictions
        ├── supersession
        ├── verification state
        └── authority tier
        │
        ▼
Boundary / rule engine
        │
        ├── deterministic low-risk proposed effects
        └── high-impact review requirements
        │
        ▼
Operational projections
        │
        ├── critical path
        ├── next executable actions
        ├── funding / scholarship review
        ├── notification schedule
        └── proof requirements
        │
        ▼
Tauri application services
        │
        ▼
React / Material-3-semantic UI
```

The legacy Gantt document remains alongside this architecture during migration. It is imported as evidence of legacy claims, not as proof that those claims are correct.

## 3. Repository Boundaries

### `data/`

Legacy canonical scheduling document. During migration, its values are treated as Tier-5 provisional claims by default.

### `gantt_ontology/src/gantt_ontology/models.py`

Existing scheduling schema used for backward compatibility and strict validation of the legacy canonical document.

### `gantt_ontology/src/gantt_ontology/mcp_domain.py`

Authoritative schema definitions for the new provenance-first domain envelope:

- sources;
- evidence;
- assertions;
- boundary contracts;
- proof requirements;
- course offerings;
- syllabi;
- assignments;
- scholarship criteria/programs/documents/windows/formulas;
- notifications;
- import artifacts/candidates;
- suggestions.

### `gantt_ontology/src/gantt_ontology/legacy_adapter.py`

Non-destructive migration adapter. It emits stable Tier-5 provisional assertions from legacy fields while retaining locators to the original graph.

### `gantt_ontology/src/gantt_ontology/ingestion.py`

Source-preserving normalized syllabus ingestion. Raw PDF/DOCX/text parsers will feed this normalized boundary rather than writing directly into authoritative entities.

### `gantt_ontology/src/gantt_ontology/rule_engine.py`

Pure boundary-contract evaluator. It proposes consequences from admissible assertions and never mutates persisted truth by itself.

### `gantt_ontology/src/gantt_ontology/scholarship_engine.py`

Sponsor-independent tri-state criteria evaluator. Missing required facts produce `Unknown`, not false eligibility decisions.

### `app/`

New packaged local application. It is isolated from the baseline giant HTML cockpit until feature and reliability gates are met.

## 4. Truth Semantics

### 4.1 Authority and verification are separate dimensions

An authoritative-looking source and a verified assertion are not the same state.

Example:

```text
Official syllabus PDF
  authority: Tier 1 institutional
        │
        ▼
Parser extracts due date
  verification: Evidence Located
        │
        ▼
Identity/applicability review
        │
        ▼
Assertion promoted under corroboration policy
  verification: Institutionally Verified
```

This prevents extraction software from promoting its own parse as fact.

### 4.2 Contradictions are first-class

Conflicting assertions coexist with `CONTRADICTS` relationships until a stronger source/version/applicability rule resolves the conflict. A newer claim does not silently overwrite history.

### 4.3 Derivations retain lineage

A Tier-2 derived assertion requires explicit source assertion IDs.

Example:

```text
verified course final grade
verified course credit value
verified program GPA policy
        │
        ▼
Derived cumulative GPA
        │
        ▼
Scholarship / SAP reevaluation contracts
```

If an upstream assertion is superseded or contradicted, downstream derived state can be invalidated/recomputed without losing the prior historical state.

## 5. Boundary Contract Architecture

Boundary contracts answer: **what must be reconsidered when an admissible fact changes?**

A contract contains:

- trigger predicates;
- explicit conditions;
- source and target swim lanes;
- impact level;
- deterministic/non-deterministic flag;
- human-review requirement;
- proposed effects;
- source assertion lineage.

The rule engine currently obeys these constraints:

1. provisional claims do not trigger authoritative propagation;
2. missing condition evidence produces `Unknown`;
3. unmet conditions produce no effects;
4. high/critical impact effects require review;
5. the engine proposes effects instead of mutating persisted truth itself.

This keeps a valid rule such as `verified grade changed → reevaluate funding` distinct from an invalid leap such as `verified grade A → scholarship awarded`.

## 6. Scholarship Architecture

Scholarships are represented as structured programs rather than prose in a funding row.

Core entities:

```text
ScholarshipProgram
 ├── EligibilityCriterion[]
 ├── RequiredDocument[]
 ├── ApplicationWindow[]
 └── AwardFormula
```

Evaluation produces:

- `EligibleCandidate` — every represented required criterion is satisfied;
- `Ineligible` — at least one represented required criterion is unmet;
- `Unknown` — a required fact or rule is absent/unsafe to evaluate.

`EligibleCandidate` is deliberately not `Awarded`.

Deadline types remain distinct:

- opening date;
- priority deadline;
- final deadline;
- document deadline;
- award/notification date.

## 7. Syllabus Drop-In Architecture

### 7.1 Raw artifact stage

The final desktop file service will:

1. copy/preserve the selected artifact into application evidence storage;
2. compute SHA-256 of the original bytes;
3. record acquisition metadata;
4. never modify the original stored artifact.

### 7.2 Parser stage

Format-specific parsers convert PDF/DOCX/text into a normalized `SyllabusImportPayload`.

Parsing is intentionally outside the truth domain. A parser is replaceable infrastructure.

### 7.3 Normalization stage

The syllabus adapter creates:

- `Source`;
- `ImportArtifact`;
- field-level `Evidence`;
- provisional/evidence-located `Assertion` records;
- `ImportCandidate` records;
- `CourseOffering`;
- `Syllabus`;
- `Assignment` records.

Stable identifiers are content/source-derived so an identical re-import does not create a second semantic record set.

### 7.4 Corroboration stage

Promotion policy checks:

- institution;
- course;
- section;
- term;
- document/version applicability;
- contradiction with existing authoritative assertions.

Only then can candidate assertions reach a stronger verification state.

## 8. Application Runtime

### 8.1 Tauri boundary

Tauri owns privileged platform operations. The webview receives narrow commands/capabilities rather than broad filesystem/shell access.

Initial capabilities are intentionally limited to:

- Tauri core defaults;
- native notifications.

Filesystem, dialog, persistence, or shell capabilities must be added only with the feature that requires them and with a documented path/permission boundary.

### 8.2 Frontend

React + TypeScript + Vite provide stateful operational surfaces.

The frontend never owns business truth. It consumes application/query projections and submits commands.

Current surfaces:

- Command;
- Critical Path;
- Swim Lanes;
- Courses;
- Scholarships;
- Evidence;
- Truth;
- Changes.

The Critical Path surface currently withholds computed results until evidence-aware inputs exist rather than displaying contradictory legacy scheduling data as authoritative.

### 8.3 Material 3 design contract

Material 3 is encoded as semantic design tokens and interaction rules:

- primary/secondary/tertiary/error roles;
- surface/container roles;
- typography hierarchy;
- shape roles;
- state layers;
- visible keyboard focus;
- reduced-motion handling;
- responsive navigation/density.

No external component library owns the product's domain or design semantics.

## 9. Persistence Target

Persistence is the next major service boundary and is **not yet implemented**.

Target requirements:

- local transactional store;
- explicit schema version;
- migrations;
- append-preserving audit history;
- source artifact references and hashes;
- queryable assertion/evidence graph;
- deterministic backup/export;
- recovery validation;
- safe concurrent read/write semantics;
- platform-neutral storage service interface where practical.

SQLite is the leading implementation candidate because it provides a local transactional relational store with mature desktop/mobile support, but adoption must be recorded in an ADR before implementation.

## 10. File / Evidence Service Target

The file service is **not yet implemented**.

Required operations:

```text
select/import artifact
        │
        ├── validate supported type / size
        ├── compute SHA-256
        ├── copy into managed evidence storage
        ├── persist Source + ImportArtifact metadata
        └── route to parser adapter

open task
        │
        └── query linked proof requirements/evidence
                 │
                 └── read-only preview from managed evidence store
```

No task should require directory archaeology to answer “what proves this happened?”

## 11. Notifications

Notification policy lives in the domain, while delivery is platform-specific.

Domain representation includes:

- trigger predicates;
- lead times;
- severity;
- channel set;
- dedupe key;
- enabled state.

Tauri's native notification plugin is the initial desktop delivery mechanism. Android can consume the same notification-policy records through an Android-specific implementation later.

Delivery state must eventually record why a notification exists:

```text
notification
  → policy/rule
  → assertion/deadline
  → evidence/source
```

## 12. Intelligence / Brainstorming Boundary

Generated brainstorming is outside authoritative truth.

`Suggestion` objects can represent:

- topics;
- theses;
- research questions;
- counterarguments;
- argument maps;
- reading plans;
- paper decomposition;
- research terms;
- evidence gaps;
- rubric mapping;
- candidate next actions.

An accepted suggestion may create a planning/task entity through an explicit command, but it does not become an institutional fact.

## 13. Mobile Boundary

Android is a future presentation/platform target, not a separate truth model.

Shared contracts:

- IDs and ontology schema;
- verification semantics;
- boundary-contract representation;
- notification-policy representation;
- import metadata;
- task/proof query DTOs;
- persistence migration format where practical.

Likely Android-first use cases:

- next executable action;
- alerts;
- evidence capture/import;
- task inspection;
- document checklist;
- quick status/proof submission.

Desktop remains better suited to large graph inspection, bulk corroboration, and architecture/audit views.

## 14. Security and Network Invariants

Production invariants:

- no application HTTP service bound to LAN interfaces;
- no unrestricted shell capability;
- no unrestricted filesystem capability;
- remote network access is opt-in by feature and constrained by explicit policy;
- imported artifacts are treated as untrusted input;
- parsing must not execute embedded document content;
- UI-rendered source text must be escaped/sanitized;
- hashes identify artifacts but do not establish truth;
- authoritative consequences require admissible assertion state, not UI state.

The Vite development server binds only to `127.0.0.1`. It is development infrastructure and not part of the packaged production operating model.

## 15. Testing Strategy

### Domain tests

Current CI covers:

- verified assertion evidence requirements;
- derived assertion lineage;
- cross-entity reference integrity;
- source-artifact preservation;
- import ID stability;
- syllabus extraction non-promotion;
- boundary propagation admission rules;
- unknown/unmet condition semantics;
- scholarship tri-state evaluation;
- generated JSON Schema validity;
- strict validation of the legacy canonical document.

### Application tests

Current CI covers:

- strict TypeScript production frontend build;
- Tauri/Rust compilation gate.

Future gates must add:

- persistence migrations;
- file import/hash behavior;
- document preview security;
- notification deduplication;
- graph cycle/orphan detection;
- critical-path calculation;
- backup/restore round trip;
- packaged builds on Windows/Linux/macOS;
- proof/evidence navigation;
- accessibility/keyboard flow;
- production network-listener test.

## 16. Migration Strategy

The baseline cockpit will not be deleted merely because the new shell exists.

Migration gates:

1. truth/evidence sidecar tested;
2. legacy adapter tested;
3. source-preserving import tested;
4. persistence operational;
5. boundary contracts operational;
6. task/evidence inspector operational;
7. critical-path projection operational from admissible facts;
8. notifications operational;
9. packaged desktop build validated;
10. backup/recovery validated;
11. parity/replacement review completed through ADR.

Only after those gates may the giant generated HTML output be retired.

## 17. Current Architectural Watermark

`MCP-WM/1.2 | baseline:9e15068d453284e027cf6413ef9fc2871ee17f70 | branch:project-owners/master-critical-path-v1 | phase:ONTOLOGY-NORMALIZATION | decision:ADR-002 | evidence:MIXED-PUBLIC-VERIFIED-PRIVATE-PENDING | critical:TAURI-BUILD-GATE | drift:0 | checkpoint:2026-09-12T14:03-07:00`

## 18. Next Architectural Gate

Resolve the Tauri/Rust CI compilation failure using captured compiler diagnostics. Once green, the next critical implementation sequence is:

1. persistence ADR and local transactional store;
2. managed evidence-file service;
3. query/application service connecting the Python/domain schema contract to the packaged runtime;
4. real institutional artifact ingestion;
5. boundary-contract catalog populated from corroborated rules;
6. evidence-aware critical-path calculation and UI projection.
