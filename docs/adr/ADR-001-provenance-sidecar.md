# ADR-001: Additive Provenance Sidecar Before Legacy Graph Migration

**Status:** Accepted  
**Date:** 2026-09-12  
**Decision owner:** Project owner / Master Critical Path governance  
**Baseline:** `9e15068d453284e027cf6413ef9fc2871ee17f70`

## Motion / Proposal

Introduce a versioned, provenance-first Master Critical Path domain envelope **alongside** the existing Gantt scheduling graph before changing or deleting legacy task data.

The new envelope will carry sources, evidence, assertions, verification states, contradiction/supersession links, boundary contracts, proof requirements, syllabus/course entities, scholarship criteria, notification policies, import artifacts, and non-authoritative suggestions.

Legacy repository values will initially enter this envelope as `Tier5Provisional` assertions unless stronger evidence is attached.

## Rationale

The current repository mixes scheduling facts, funding projections, personal-state claims, institutional rules, visual metadata, and hardcoded bridge defaults. Some claims conflict with one another and several public authoritative sources already contradict high-impact values.

A destructive schema rewrite at this stage would create three avoidable risks:

1. losing the original claim state needed for audit;
2. silently choosing one contradictory value before evidence exists;
3. breaking the existing cockpit before the replacement domain model and UI are validated.

An additive sidecar preserves the baseline while creating a controlled path from claim to evidence-backed truth.

## Evidence

Baseline inspection established:

- no first-class source/evidence/assertion provenance model;
- disagreement between README course claims and canonical JSON course claims;
- domain facts hardcoded in the bridge despite a stated data-free architecture;
- scholarship and syllabus concepts represented primarily as prose/task metadata;
- no baseline tests;
- three duplicated giant HTML deployment artifacts sharing the same Git blob.

Phase-1 public corroboration also established that several high-impact legacy claims require correction or private institutional records before promotion to authoritative state.

## Objections / Risks

### Objection 1: Temporary dual models increase complexity

True. The scheduling model and truth envelope coexist during migration.

**Mitigation:** the sidecar is deliberately reference-oriented. It does not duplicate scheduling algorithms and can be retired or merged after the desktop domain model reaches feature parity.

### Objection 2: Legacy IDs may not map cleanly to canonical entities

True. Existing IDs mix task, course, track, and strategic concepts.

**Mitigation:** the legacy adapter preserves original IDs and records them as provenance-bearing subject identifiers. Semantic reclassification is a later explicit migration step.

### Objection 3: A new schema can become speculative architecture

Possible.

**Mitigation:** every added entity is tied to an explicit project requirement: evidence, task proof, syllabus import, scholarship criteria, notifications, boundary propagation, or brainstorming isolation. No generalized semantic-web framework is being introduced for its own amusement.

## Decision

Accepted.

The project will:

1. preserve the untouched baseline branch;
2. keep the existing scheduling graph operational during migration;
3. wrap legacy facts as provisional assertions;
4. attach authoritative evidence without overwriting raw claims;
5. represent contradictions explicitly;
6. run deterministic boundary contracts only against assertions whose authority/verification state satisfies the contract rule;
7. migrate UI surfaces only after truth/evidence behavior is testable.

## Implementation

Initial implementation:

- `gantt_ontology/src/gantt_ontology/mcp_domain.py`
- `gantt_ontology/tests/test_mcp_domain.py`
- `gantt_ontology/tools/export_mcp_schema.py`
- `.github/workflows/ontology-ci.yml`

A deterministic legacy-to-sidecar adapter follows this ADR.

## Verification

GitHub Actions `Ontology CI` run `34718168825` completed successfully on commit `7cfae0893d7c730e10c64f50804b0a3eb453b35b`, validating:

- provenance-domain unit tests;
- strict validation of the current legacy canonical document;
- deterministic JSON-Schema generation;
- generated Draft 2020-12 schema validity.

## Supersession Rules

This ADR may be superseded only when all of the following are true:

1. authoritative and provisional assertions are represented in the primary persisted domain model;
2. source/evidence lineage survives migration;
3. contradiction history survives migration;
4. the legacy graph can be reproduced or migrated deterministically;
5. boundary-contract tests pass against migrated data;
6. desktop UI surfaces no longer depend on the legacy compiled-HTML data injection path;
7. rollback/recovery has been demonstrated.
