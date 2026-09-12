from datetime import datetime, timezone

import pytest

from gantt_ontology.ingestion import (
    SyllabusAssignmentPayload,
    SyllabusImportPayload,
    ingest_syllabus_payload,
)
from gantt_ontology.mcp_domain import (
    AuthorityTier,
    SourceKind,
    VerificationState,
)


NOW = datetime(2026, 9, 12, 22, 0, tzinfo=timezone.utc)
HASH = "ab" * 32


def payload() -> SyllabusImportPayload:
    return SyllabusImportPayload(
        institutionId="institution-1",
        department="PHIL",
        courseCode="PHIL 341",
        section="001",
        title="Metaphysics",
        term="Fall 2026",
        credits=3,
        modality="In person",
        instructorNames=["Instructor Example"],
        gradingScale="A = 90–100",
        lateWorkPolicy="See institutional syllabus policy.",
        requiredMaterials=["Primary text"],
        assignments=[
            SyllabusAssignmentPayload(
                title="Ontology paper",
                assignmentType="Paper",
                dueAt="2026-10-20T23:59:00-08:00",
                weightPercent=25,
                submissionMethod="LMS",
            )
        ],
    )


def test_default_syllabus_import_does_not_promote_extracted_values() -> None:
    envelope = ingest_syllabus_payload(
        payload(),
        acquired_at=NOW,
        artifact_sha256=HASH,
        original_filename="syllabus.pdf",
        stored_ref="evidence/ab/syllabus.pdf",
        media_type="application/pdf",
    )

    assert envelope.sources[0].authority_tier == AuthorityTier.TIER_5_PROVISIONAL
    assert envelope.course_offerings[0].verification_state == VerificationState.EVIDENCE_LOCATED
    assert envelope.syllabi[0].verification_state == VerificationState.EVIDENCE_LOCATED
    assert envelope.assignments[0].verification_state == VerificationState.EVIDENCE_LOCATED
    assert all(
        item.verification_state == VerificationState.EVIDENCE_LOCATED
        for item in envelope.assertions
    )


def test_even_tier_one_source_extraction_is_not_automatically_verified() -> None:
    envelope = ingest_syllabus_payload(
        payload(),
        acquired_at=NOW,
        artifact_sha256=HASH,
        original_filename="official-syllabus.pdf",
        stored_ref="evidence/ab/official-syllabus.pdf",
        media_type="application/pdf",
        issuer="Example University",
        source_authority=AuthorityTier.TIER_1_INSTITUTIONAL,
        source_kind=SourceKind.INSTITUTIONAL_RECORD,
    )

    assert envelope.sources[0].authority_tier == AuthorityTier.TIER_1_INSTITUTIONAL
    assert all(
        item.verification_state == VerificationState.EVIDENCE_LOCATED
        for item in envelope.assertions
    )
    assert not any(
        item.verification_state == VerificationState.INSTITUTIONALLY_VERIFIED
        for item in envelope.assertions
    )


def test_assignment_deadline_and_provenance_are_preserved() -> None:
    envelope = ingest_syllabus_payload(
        payload(),
        acquired_at=NOW,
        artifact_sha256=HASH,
        original_filename="syllabus.pdf",
        stored_ref="evidence/ab/syllabus.pdf",
    )

    assignment = envelope.assignments[0]
    assert assignment.due_at is not None
    assert assignment.due_at.isoformat() == "2026-10-20T23:59:00-08:00"
    assert assignment.source_assertion_ids

    due_claim = next(
        item
        for item in envelope.assertions
        if item.id in assignment.source_assertion_ids and item.predicate == "dueAt"
    )
    evidence = next(item for item in envelope.evidence if item.id == due_claim.evidence_ids[0])
    assert evidence.locator == "syllabus.assignments[0].dueAt"


def test_original_artifact_metadata_is_retained() -> None:
    envelope = ingest_syllabus_payload(
        payload(),
        acquired_at=NOW,
        artifact_sha256=HASH,
        original_filename="syllabus.pdf",
        stored_ref="evidence/ab/syllabus.pdf",
        media_type="application/pdf",
    )

    artifact = envelope.import_artifacts[0]
    assert artifact.original_preserved is True
    assert artifact.sha256 == HASH
    assert artifact.original_filename == "syllabus.pdf"
    assert artifact.stored_ref == "evidence/ab/syllabus.pdf"


def test_same_syllabus_import_is_idempotent_for_domain_ids() -> None:
    first = ingest_syllabus_payload(
        payload(),
        acquired_at=NOW,
        artifact_sha256=HASH,
        original_filename="syllabus.pdf",
        stored_ref="evidence/ab/syllabus.pdf",
    )
    second = ingest_syllabus_payload(
        payload(),
        acquired_at=NOW,
        artifact_sha256=HASH,
        original_filename="syllabus.pdf",
        stored_ref="evidence/ab/syllabus.pdf",
    )

    assert [item.id for item in first.sources] == [item.id for item in second.sources]
    assert [item.id for item in first.evidence] == [item.id for item in second.evidence]
    assert [item.id for item in first.assertions] == [item.id for item in second.assertions]
    assert [item.id for item in first.assignments] == [item.id for item in second.assignments]


def test_invalid_artifact_hash_is_rejected() -> None:
    with pytest.raises(ValueError):
        ingest_syllabus_payload(
            payload(),
            acquired_at=NOW,
            artifact_sha256="not-a-sha256",
            original_filename="syllabus.pdf",
            stored_ref="evidence/bad/syllabus.pdf",
        )
