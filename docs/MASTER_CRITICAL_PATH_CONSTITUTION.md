# Master Critical Path
## Engineering Constitution v1.1

Repository: `git@github.com:thrymspire/sovereignCritical.git`  
Primary target: cross-platform desktop application  
Future target: Android application hooks and reusable platform-neutral core  
Truth posture: all legacy repository assertions are provisional until corroborated

## 1. Mission

Engineer **Master Critical Path** as the authoritative operational representation of the owner's forward life trajectory.

It is not primarily a journal, generic todo list, dashboard experiment, speculative roadmap, personality profiler, or visualization project. It is an evidence-backed execution system that answers:

1. What is true?
2. What must happen next?
3. What does that action affect?
4. What proves it happened?

The system must preserve forward progress, institutional obligations, proof of completion, and deterministic propagation of consequences across academic, funding, financial, employment, administrative, project, documentation, and other operational domains.

## 2. Owner Decisions

### 2.1 Existing data authority

Every existing assertion in the repository is provisional until corroborated.

Internal consistency is not evidence. Institutional records outrank repository assertions. Deterministic derived assertions may become trusted only when their complete provenance chain is retained. Unsupported legacy data must be flagged rather than silently discarded or promoted.

### 2.2 Runtime target

Build Master Critical Path as a cross-platform desktop application with first-class Windows, Linux, and macOS targets.

Design ontology, persistence, evidence, rules, imports, search, and notification interfaces so Android support can be added later without rebuilding the domain core.

Production use must not require an externally reachable HTTP service or require the owner to manually manage a development server. Prefer a packaged direct-launch runtime such as Tauri or an equivalent architecture if repository inspection confirms the architectural benefit.

### 2.3 Useful product capabilities

The system must support, where justified by evidence and workflow requirements:

- notifications and deadline escalation;
- drop-in data ingestion;
- syllabus ingestion;
- transcript and degree-audit ingestion;
- scholarship criteria, deadlines, paperwork, and application-state tracking;
- direct task-to-file/evidence presentation;
- proactive boundary-contract reevaluation;
- assignment and topic brainstorming;
- provenance-aware suggestions and recommendations;
- search across tasks, evidence, assertions, courses, scholarships, documents, rules, and source text;
- future mobile notification and capture hooks.

## 3. Repository and Change Control

The Git repository is the engineering source of record.

Before architecture or behavior changes:

1. inspect the repository;
2. identify default branch and HEAD;
3. record baseline commit SHA;
4. create an untouched project-owner baseline branch;
5. preserve that branch unchanged;
6. inventory current framework, data model, assertions, swim lanes, boundary contracts, features, defects, and unsupported claims;
7. implement only on a separate working branch.

No unrelated files may be modified merely to normalize formatting, rename things aesthetically, reorganize preferences, or satisfy implementation taste.

Every changed file must have a traceable relationship to a requirement, defect, data-integrity issue, architectural invariant, or validated usability need.

Use small coherent commits. Each material commit must record what changed, why, which requirement it satisfies, validation performed, evidence, contracts affected, migration impact, and rollback considerations.

## 4. Truth Hierarchy

### Tier 1: Institutional records

Highest authority. Examples include transcript, degree audit, registrar record, official syllabus, course catalog, official university calendar, financial-aid determination, scholarship award or eligibility notice, institutional policy, official billing/account record, official employment record, government record, signed agreement, and formally issued certification.

### Tier 2: Deterministic derived assertions

Assertions produced from validated evidence through explicit rules.

Example:

`Final grade = A`

may trigger reevaluation of course completion, degree requirements, earned credits, GPA, prerequisites, satisfactory academic progress, funding eligibility, scholarship criteria, and graduation path.

Derived assertions must retain complete source lineage.

### Tier 3: Authoritative external sources

Official sources required for rules not represented in local institutional evidence.

### Tier 4: Corroborated secondary evidence

Used only when higher-authority evidence is unavailable.

### Tier 5: Provisional assertions

Includes all current legacy repository assertions until audited, user-entered facts, manually imported data, remembered information, inferred data, incomplete records, and legacy data with missing provenance.

Provisional information may drive investigation, reminders, and candidate actions but may not silently become authoritative.

## 5. Assertion Model

Every material assertion should support:

- stable ID;
- subject, predicate, and value;
- source and source tier;
- source location;
- acquisition timestamp;
- effective and expiration dates where applicable;
- confidence;
- verification state;
- provenance chain;
- issuing institution/entity;
- applicable academic term or policy version;
- affected ontology nodes;
- affected boundary contracts;
- contradiction and supersession relationships;
- reviewer where required;
- audit history.

Verification states:

- Unknown
- Claimed
- Evidence Located
- Corroborated
- Institutionally Verified
- Derived
- Contradicted
- Superseded
- Expired
- Needs Review

Do not reduce this model to a generic `verified: true/false`.

## 6. Core Ontology

The system is an explicit graph. Tasks are not isolated checklist rows.

Minimum entity classes include:

- Goal
- Outcome
- Milestone
- Task
- Action
- Requirement
- Dependency
- Constraint
- Institution
- Person
- Course
- CourseOffering
- Assignment
- Topic
- LearningObjective
- Syllabus
- Program
- Credential
- Grade
- FundingSource
- FundingRequirement
- FinancialObligation
- Scholarship
- ScholarshipCriterion
- ScholarshipApplication
- EmploymentRequirement
- Document
- Evidence
- Artifact
- Event
- Deadline
- Decision
- Assertion
- Source
- Risk
- Blocker
- BoundaryContract
- SwimLane
- StateTransition
- Verification
- Review
- Exception
- Notification
- ReminderPolicy
- ImportJob
- DataAdapter
- ExternalReference
- Suggestion
- Recommendation
- BrainstormSession

Minimum relationships include:

- REQUIRES
- SATISFIES
- BLOCKS
- UNBLOCKS
- DEPENDS_ON
- PRECEDES
- PRODUCES
- PROVES
- CORROBORATES
- CONTRADICTS
- DERIVED_FROM
- GOVERNED_BY
- FUNDED_BY
- AFFECTS
- TRIGGERS
- INVALIDATES
- SUPERSEDES
- BELONGS_TO
- VERIFIED_BY
- OWNED_BY
- ASSIGNED_IN
- DUE_ON
- HAS_CRITERION
- REQUIRES_DOCUMENT
- ELIGIBLE_IF
- INELIGIBLE_IF
- REMINDS
- ESCALATES
- IMPORTED_FROM
- SUGGESTS
- REFERENCES
- SUPPORTS
- CONFLICTS_WITH

Relationships may themselves require provenance and verification metadata.

## 7. Critical Path Model

Each task must expose purpose, parent goal, primary and secondary swim lanes, upstream dependencies, downstream dependents, deadline, earliest actionable date, expected effort, criticality, failure consequence, blocker state, completion criteria, proof requirements, associated evidence/files, verification method, institutions, inbound/outbound boundary contracts, next executable action, notification state, and history.

Operational states must distinguish critical, near-critical, supporting, blocked, waiting external, ready, completed unverified, completed verified, contradicted, and needs review.

Clicking a checkbox is not sufficient evidence of material completion.

## 8. Swim Lanes

Initial operational lanes:

- Academic
- Financial Aid / Funding
- Scholarships
- Personal Finance
- Employment
- Institutional Administration
- Documentation
- Transportation / Logistics
- Projects / Research
- Legal / Compliance
- Personal Operations

Every task has one primary lane and may have multiple secondary lanes. Cross-lane dependencies must remain visible. A task cannot disappear merely because responsibility crosses a lane boundary.

## 9. Boundary Contracts

Boundary contracts are explicit propagation rules between domains.

### Academic to Degree Progress

Verified course completion updates earned credits, mapped requirements, prerequisite chains, remaining credits, critical path, and graduation projection.

### Academic to Funding

Verified grade or enrollment changes trigger applicable GPA, attempted/completed-credit, satisfactory-academic-progress, financial-aid, and scholarship eligibility reevaluation. High-impact ambiguous consequences require human review.

### Syllabus to Academic Execution

When a syllabus is ingested:

- preserve the source artifact;
- identify course offering;
- extract candidate assignments, exams, due dates, grade weights, attendance rules, late-work rules, instructor references, readings/materials, and learning objectives;
- create candidate tasks and reminder schedules;
- define completion evidence where appropriate;
- detect conflicts with existing assertions;
- retain field-level provenance where practical.

Parsed text is not automatically authoritative. Extracted values enter an appropriate provisional/evidence-located state until corroboration rules are met.

### Scholarship to Academic / Funding / Documentation

Each scholarship should model sponsor, award amount, renewable status, eligibility criteria, GPA threshold, enrollment requirements, residency/citizenship requirements where applicable, field/program restrictions, class standing, financial need, essay prompts, recommendation letters, transcripts, FAFSA or equivalent requirements, enrollment proof, additional paperwork, opening date, priority deadline, final deadline, notification date, award conditions, renewal conditions, authoritative source, and verification state.

Derive candidate eligibility, unmet criteria, missing documents, next action, lead time, deadline risk, dependencies on transcript/grades/enrollment, and funding effects if awarded.

Incomplete data produces candidate derived assertions, never guarantees.

### Employment to Finance / Academic Scheduling

Verified employment events may affect income, working hours, course scheduling, transportation, funding need, available capacity, and dependent deadlines.

### Completion to Evidence History

Verified completion preserves evidence, freezes historical state, retains provenance, updates downstream nodes, and does not silently reopen unless a valid reopening condition occurs.

## 10. Drop-In Data Architecture

Incoming data must enter through documented adapters.

Initial adapter categories should anticipate syllabus PDF/DOCX/text, transcript, degree audit, course catalog data, financial-aid letter, scholarship notice, scholarship source capture, institutional email, calendar export, CSV, JSON, manually entered structured facts, and future mobile capture.

Every adapter must preserve the original artifact, hash it where practical, identify source/acquisition metadata, parse candidate facts, map them to canonical entities, retain provenance, validate, detect contradictions, support idempotent re-import, expose an import report, support dry-run where practical, create review tasks for ambiguous high-impact mappings, and never destroy the original source.

Schemas must be versioned and migrations documented.

## 11. Syllabus Ontology

Expected syllabus data should include, where available:

- institution, department, course code, section, title, term, credits, modality, location, meeting schedule;
- instructor identity/contact, office hours, communication expectations;
- grading scale, weighted categories, attendance, late-work, makeup, participation, integrity, and accessibility/support references;
- assignments with title, type, description, due date/time, weight/points, submission method, prerequisite reading, rubric reference, required artifact, completion evidence, and learning-objective mapping;
- quizzes, exams, presentations, projects, papers, labs, and finals;
- textbooks, readings, links, software, equipment, and files.

Import should generate candidate tasks, deadlines, evidence requirements, and reminders while preserving uncertainty where the source is ambiguous.

## 12. Intelligence and Brainstorming Layer

Generated assistance must remain distinct from truth.

Supported suggestion types may include topic brainstorming, thesis alternatives, argument maps, research questions, counterarguments, reading plans, decomposition of large papers into executable tasks, research terms, evidence-gap identification, and rubric-to-outline mapping.

Generated items are `Suggestion` or `Recommendation` entities, not `Assertion` entities. Suggestions may reference verified course data, assignment prompts, rubrics, and learning objectives. They do not alter authoritative state without an explicit accepted transition.

## 13. Notifications and Escalation

Notifications are an operational subsystem.

Triggers should support upcoming deadlines, unmet prerequisites, missing completion evidence, scholarship opening dates and deadlines, paperwork lead time, enrollment events, funding requirements, conflicting deadlines, stale waiting-on-external tasks, contradictions, boundary-contract review requirements, expiring evidence/policies, and critical-path changes.

Severity:

- Informational
- Upcoming
- Action Required
- Critical
- Blocked
- Verification Required

Notifications must support configurable lead times, deduplication, grouping, obsolete-alert suppression, and traceability from notification to rule to assertion to source.

The notification domain model must be reusable by a future Android implementation.

## 14. Evidence and File Presentation

A task detail view must make supporting evidence immediately inspectable.

A user opening a task must be able to answer: **What proves this happened?**

Evidence should retain file reference, source, source tier, immutable hash where practical, acquisition date, document date, associated task/assertion, verification state, reviewer, notes, and extracted references.

The UI should support inline PDF/document/image/text inspection where technically practical, together with metadata, provenance, linked assertions, source location, verification controls, and contradiction display.

Historical evidence remains accessible after task completion.

## 15. User Interface

Use current Material 3 principles where appropriate while prioritizing density, visible causality, responsiveness, and operational usefulness over decorative whitespace.

Required surfaces:

- command/overview;
- critical path/dependency graph;
- swim lanes;
- task inspector;
- course surface;
- scholarship surface;
- evidence inspector;
- truth/provenance inspector;
- notification center;
- change history;
- global search.

The truth inspector should expose:

`Source -> Evidence -> Assertion -> Derivation -> Boundary Contract -> Dependent Decision`

## 16. Local Execution and Platform Architecture

Production must launch as a packaged local application.

Requirements:

- no LAN-exposed production HTTP service;
- no manual development-server requirement for normal use;
- local persistent storage;
- documented backup and recovery;
- reproducible build;
- explicit separation of development tooling from production runtime;
- platform-neutral domain logic where reasonable;
- Android-compatible service boundaries reserved for later implementation.

Separate ontology/domain model, rule engine, evidence/provenance service, import adapters, persistence, search/indexing, notification service, UI/application layer, and platform integration layer.

Platform-specific code must not own authoritative business rules.

## 17. Engineering Workflow

Use engineering methods where they improve reliability rather than ceremonially applying terminology.

### Critical Path Method

Identify the dependency chain controlling important outcomes.

### Six Sigma / DMAIC

**Define:** state the failure being prevented.  
**Measure:** measure assertion coverage, provenance completeness, evidence quality, orphan nodes, contract coverage, workflow friction, dropped obligations, and notification precision.  
**Analyze:** find unsupported assertions, contradictions, broken contracts, bottlenecks, duplicated data, false completion, and import ambiguity.  
**Improve:** change the smallest effective architectural surface.  
**Control:** add validation preventing recurrence.

### Robert's Rules-inspired ADR governance

Material decisions use structured ADRs containing proposal/motion, rationale, evidence, objections/risks, decision, implementation, verification, and supersession rules.

INTJ/ENTJ traits, learning-style models, and attachment-style concepts may influence optional communication/interface heuristics but are not authoritative psychological facts and never outrank evidence.

## 18. SOP: Truth Corroboration

For each material claim:

1. express the claim atomically;
2. classify the claim;
3. locate the strongest available source;
4. extract source evidence;
5. verify identity and applicability;
6. verify date/version/term;
7. search for contradiction;
8. record provenance;
9. update verification state;
10. derive consequences;
11. execute applicable boundary contracts;
12. require human review for high-impact ambiguous consequences;
13. freeze verified historical state;
14. record proof of work.

No contradiction may be invisibly overwritten.

## 19. Proof of Completion

Each important task must define completion criteria, required evidence, verification method, verifier where applicable, downstream consequences, and reopening conditions.

Evidence may include official PDFs, transcript entries, institutional email, receipts, confirmation numbers, screenshots, submitted forms, signed documents, Git commits, generated artifacts, grade records, exported reports, and uploaded-assignment confirmations.

Completion state is distinct from verification state.

## 20. Forward-Progress Contract

Completed and verified nodes become historical evidence.

They reenter active work only when authoritative evidence contradicts prior state, institutional conditions change, a dependency is invalidated, or review establishes that the prior assertion was incorrect.

No silent regression, disappearing commitments, orphaned downstream dependencies, UI-induced dropped work, or accidental resurrection of obsolete tasks.

## 21. Context-Drift Watermark

Use semantic context accounting rather than pretending to possess an exact model token counter when the runtime cannot provide one.

Format:

`MCP-WM/<version> | baseline:<sha> | branch:<branch> | phase:<phase> | decision:<ADR> | evidence:<state> | critical:<node> | drift:<0-3> | checkpoint:<timestamp>`

Drift scale:

- 0: directly supported by constitution/current evidence
- 1: minor exploration
- 2: material divergence requiring justification
- 3: stop and reconcile

At substantial checkpoints record current objective, completed work, evidence gained, assertions changed, contracts triggered, unresolved questions, and next critical action.

## 22. Proof-of-Work Ledger

Maintain machine-readable and human-readable proof of work.

Record timestamp, branch, commit, task/issue, requirement, files changed, reason, validation, evidence, affected contracts, remaining risks, and next action. Generate from repository metadata where practical instead of manually duplicating facts.

## 23. Validation

Minimum automated or repeatable validation:

- graph integrity;
- cycle handling;
- orphan tasks/evidence;
- dangling contract references;
- contradictory assertions;
- provenance completeness;
- evidence linkage;
- immutable completion history;
- reopening conditions;
- grade propagation;
- funding propagation;
- scholarship rule propagation;
- syllabus import and re-import idempotency;
- generic import idempotency;
- deadline extraction;
- notification deduplication;
- schema migrations;
- persistence;
- backup/recovery;
- search;
- document viewing;
- local-only network exposure;
- navigation;
- platform packaging;
- deterministic rule behavior.

Important ontology invariants must be machine-tested.

## 24. Initial Execution Sequence

### Phase 0: Baseline

Inspect repository, preserve untouched baseline, establish working branch, record watermark, and document existing architecture.

### Phase 1: Truth Audit

Inventory assertions, classify legacy data as provisional, locate provenance, identify unsupported claims and contradictions, audit swim lanes, boundary contracts, and evidence coverage.

### Phase 2: Ontology Normalization

Formalize entities, relationships, assertion/provenance model, scholarship ontology, syllabus/course ontology, notification ontology, and propagation rules.

### Phase 3: Evidence Architecture

Implement evidence store, task/file linkage, source preservation, file preview, provenance views, and contradiction handling.

### Phase 4: Critical Path / Rule Engine

Implement dependency evaluation, blocked/unblocked state, criticality, next-action calculation, boundary propagation, and review generation.

### Phase 5: Drop-In Data

Prioritize syllabus, transcript/degree audit, scholarship record, financial-aid documentation, then generic structured import.

### Phase 6: UI

Build overview, graph, swim lanes, task inspector, course surface, scholarship surface, evidence inspector, truth inspector, notifications, search, and change history.

### Phase 7: Intelligence Layer

Add clearly non-authoritative assignment brainstorming, topic suggestions, argument decomposition, rubric mapping, research prompts, and suggested next actions.

### Phase 8: Platform Control

Validate packaged desktop execution on Windows/Linux/macOS and preserve Android service/API hooks.

### Phase 9: Control

Complete tests, documentation, reproducibility, recovery, proof-of-work reconciliation, performance review, and audit against this constitution.

## 25. Definition of Done

A feature is complete only when:

1. requirement is explicit;
2. implementation exists;
3. tests or repeatable validation demonstrate behavior;
4. provenance requirements are satisfied;
5. affected boundary contracts are evaluated;
6. non-obvious behavior is documented;
7. unrelated regressions are absent;
8. proof of work is recorded;
9. migration/rollback concerns are addressed;
10. resulting state is committed and pushed to the authorized working branch.

Rendering successfully is not completion.

## 26. Anti-Goals

Do not treat legacy content as authoritative merely because it exists; invent missing facts; silently reconcile contradictions; convert generated suggestions into facts; allow AI brainstorming to mutate authoritative state without explicit transition; mark high-impact tasks complete without evidence; hide missing provenance; let UI state become ontology truth; duplicate authoritative data without synchronization rules; create unnecessary files; refactor unrelated areas; expose production to the LAN; optimize visual polish before operational correctness; add abstractions without demonstrated use; create notification spam; reduce scholarship requirements to vague prose when they can be modeled; destroy original imported artifacts; or let Master Critical Path become more work than the life-critical work it coordinates.

## 27. Operating Constraint

Target approximately 85-90% execution and 10-15% system maintenance. During stabilization, cap ordinary tinkering at roughly three hours per week for four to six weeks unless a reliability-critical defect justifies more. After stabilization, target 45-60 minutes per week plus a periodic architecture/audit review.

Prioritize a feature when it prevents a dropped obligation, improves evidence/truth quality, or reduces decision latency.

The system exists to protect forward motion, not provide an endlessly reorganizable model of forward motion.
