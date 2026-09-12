from datetime import datetime, timezone

from gantt_ontology.legacy_adapter import (
    legacy_document_sha256,
    legacy_gantt_to_mcp_envelope,
)
from gantt_ontology.mcp_domain import AuthorityTier, VerificationState


NOW = datetime(2026, 9, 12, 21, 0, tzinfo=timezone.utc)


LEGACY = {
    "meta": {"schemaVersion": "1.0.0"},
    "project": {
        "id": "mcp-project",
        "name": "Master Critical Path",
        "startDate": "2026-08-24",
    },
    "tasks": [
        {
            "id": "course-task-1",
            "name": "Example assignment",
            "percentComplete": 100.0,
            "notes": "STATUS: SECURED BASELINE ASSET [100% COMPLETE]",
            "duration": {"value": 6.0, "unit": "days"},
        }
    ],
    "dependencies": [],
}


def test_same_document_has_stable_normalized_hash() -> None:
    reordered = {
        "dependencies": [],
        "tasks": LEGACY["tasks"],
        "project": LEGACY["project"],
        "meta": LEGACY["meta"],
    }
    assert legacy_document_sha256(LEGACY) == legacy_document_sha256(reordered)


def test_legacy_complete_claim_is_not_promoted_to_verified_truth() -> None:
    envelope = legacy_gantt_to_mcp_envelope(LEGACY, acquired_at=NOW)

    percent_claim = next(
        item
        for item in envelope.assertions
        if item.subject_id == "legacy:tasks:course-task-1"
        and item.predicate == "percentComplete"
    )

    assert percent_claim.object_value == 100.0
    assert percent_claim.authority_tier == AuthorityTier.TIER_5_PROVISIONAL
    assert percent_claim.verification_state == VerificationState.CLAIMED
    assert percent_claim.confidence == 0.0
    assert len(percent_claim.evidence_ids) == 1


def test_legacy_evidence_proves_repository_claim_only() -> None:
    envelope = legacy_gantt_to_mcp_envelope(LEGACY, acquired_at=NOW)
    claim = next(
        item
        for item in envelope.assertions
        if item.subject_id == "legacy:tasks:course-task-1"
        and item.predicate == "notes"
    )
    evidence = next(item for item in envelope.evidence if item.id == claim.evidence_ids[0])

    assert evidence.verification_state == VerificationState.EVIDENCE_LOCATED
    assert "not proof that the claim is true" in (evidence.notes or "")


def test_nested_duration_fields_become_separate_claims() -> None:
    envelope = legacy_gantt_to_mcp_envelope(LEGACY, acquired_at=NOW)
    predicates = {
        item.predicate
        for item in envelope.assertions
        if item.subject_id == "legacy:tasks:course-task-1"
    }

    assert "duration.value" in predicates
    assert "duration.unit" in predicates


def test_adapter_is_idempotent_for_ids() -> None:
    first = legacy_gantt_to_mcp_envelope(LEGACY, acquired_at=NOW)
    second = legacy_gantt_to_mcp_envelope(LEGACY, acquired_at=NOW)

    assert [item.id for item in first.sources] == [item.id for item in second.sources]
    assert [item.id for item in first.evidence] == [item.id for item in second.evidence]
    assert [item.id for item in first.assertions] == [item.id for item in second.assertions]


def test_source_retains_original_graph_reference() -> None:
    envelope = legacy_gantt_to_mcp_envelope(
        LEGACY,
        acquired_at=NOW,
        source_version="9e15068d453284e027cf6413ef9fc2871ee17f70",
    )

    source = envelope.sources[0]
    assert source.original_artifact_ref == "data/gantt_ontology.json"
    assert source.version == "9e15068d453284e027cf6413ef9fc2871ee17f70"
