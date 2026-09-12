from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from gantt_ontology.mcp_domain import (
    ApplicationWindow,
    Assertion,
    AuthorityTier,
    ClaimType,
    CourseOffering,
    Evidence,
    ImportArtifact,
    MCPDomainEnvelope,
    NotificationPolicy,
    ScholarshipProgram,
    Source,
    SourceKind,
    VerificationState,
)


NOW = datetime(2026, 9, 12, 20, 0, tzinfo=timezone.utc)


def source(source_id: str = "src-1") -> Source:
    return Source(
        id=source_id,
        kind=SourceKind.INSTITUTIONAL_RECORD,
        authorityTier=AuthorityTier.TIER_1_INSTITUTIONAL,
        title="Official transcript",
        issuer="Example University",
        acquiredAt=NOW,
        sha256="a" * 64,
    )


def evidence(evidence_id: str = "ev-1", source_id: str = "src-1") -> Evidence:
    return Evidence(
        id=evidence_id,
        sourceId=source_id,
        locator="course:HIST-341/final-grade",
        capturedValue="A",
        acquiredAt=NOW,
    )


def test_provisional_legacy_assertion_may_exist_without_evidence() -> None:
    assertion = Assertion(
        id="a-legacy",
        subjectId="course-1",
        predicate="finalGrade",
        objectValue="A",
        claimType=ClaimType.PROVISIONAL_ASSERTION,
        authorityTier=AuthorityTier.TIER_5_PROVISIONAL,
        verificationState=VerificationState.CLAIMED,
    )
    assert assertion.verification_state == VerificationState.CLAIMED


def test_institutionally_verified_assertion_requires_evidence() -> None:
    with pytest.raises(ValidationError):
        Assertion(
            id="a-grade",
            subjectId="course-1",
            predicate="finalGrade",
            objectValue="A",
            claimType=ClaimType.INSTITUTIONAL_FACT,
            authorityTier=AuthorityTier.TIER_1_INSTITUTIONAL,
            verificationState=VerificationState.INSTITUTIONALLY_VERIFIED,
        )


def test_derived_assertion_requires_lineage() -> None:
    with pytest.raises(ValidationError):
        Assertion(
            id="a-derived",
            subjectId="funding-1",
            predicate="requiresReevaluation",
            objectValue=True,
            claimType=ClaimType.DERIVED_ASSERTION,
            authorityTier=AuthorityTier.TIER_2_DERIVED,
            verificationState=VerificationState.DERIVED,
        )


def test_envelope_rejects_missing_evidence_reference() -> None:
    item = Assertion(
        id="a-grade",
        subjectId="course-1",
        predicate="finalGrade",
        objectValue="A",
        claimType=ClaimType.INSTITUTIONAL_FACT,
        authorityTier=AuthorityTier.TIER_1_INSTITUTIONAL,
        verificationState=VerificationState.INSTITUTIONALLY_VERIFIED,
        evidenceIds=["ev-missing"],
    )

    with pytest.raises(ValidationError):
        MCPDomainEnvelope(createdAt=NOW, sources=[source()], assertions=[item])


def test_envelope_accepts_verified_source_evidence_assertion_chain() -> None:
    item = Assertion(
        id="a-grade",
        subjectId="course-1",
        predicate="finalGrade",
        objectValue="A",
        claimType=ClaimType.INSTITUTIONAL_FACT,
        authorityTier=AuthorityTier.TIER_1_INSTITUTIONAL,
        verificationState=VerificationState.INSTITUTIONALLY_VERIFIED,
        evidenceIds=["ev-1"],
    )

    envelope = MCPDomainEnvelope(
        createdAt=NOW,
        sources=[source()],
        evidence=[evidence()],
        assertions=[item],
    )

    assert envelope.assertions[0].id == "a-grade"


def test_duplicate_ids_are_rejected_across_entity_types() -> None:
    item_source = source("dup")
    item_evidence = evidence("dup", "dup")

    with pytest.raises(ValidationError):
        MCPDomainEnvelope(
            createdAt=NOW,
            sources=[item_source],
            evidence=[item_evidence],
        )


def test_import_artifact_must_preserve_original() -> None:
    with pytest.raises(ValidationError):
        ImportArtifact(
            id="import-1",
            sourceId="src-1",
            originalFilename="syllabus.pdf",
            mediaType="application/pdf",
            sha256="b" * 64,
            acquiredAt=NOW,
            storedRef="evidence/sha256/bb/syllabus.pdf",
            originalPreserved=False,
        )


def test_notification_lead_times_must_be_unique_and_nonnegative() -> None:
    with pytest.raises(ValidationError):
        NotificationPolicy(
            id="notify-1",
            name="Deadline warnings",
            triggerPredicates=["dueAt"],
            leadTimesMinutes=[1440, 1440],
        )

    with pytest.raises(ValidationError):
        NotificationPolicy(
            id="notify-2",
            name="Invalid deadline warnings",
            triggerPredicates=["dueAt"],
            leadTimesMinutes=[-5],
        )


def test_application_window_rejects_reverse_dates() -> None:
    with pytest.raises(ValidationError):
        ApplicationWindow(
            id="window-1",
            opensAt="2026-12-31T00:00:00Z",
            closesAt="2026-10-01T00:00:00Z",
        )


def test_course_and_scholarship_can_be_modeled_without_claiming_verification() -> None:
    course = CourseOffering(
        id="course-f26",
        institutionId="uaf",
        courseCode="PHIL F102X",
        title="Introduction to Philosophy",
        term="Fall 2026",
    )
    scholarship = ScholarshipProgram(
        id="scholarship-1",
        sponsorEntityId="sponsor-1",
        name="Example Scholarship",
    )

    envelope = MCPDomainEnvelope(
        createdAt=NOW,
        courseOfferings=[course],
        scholarships=[scholarship],
    )

    assert envelope.course_offerings[0].verification_state == VerificationState.CLAIMED
    assert envelope.scholarships[0].verification_state == VerificationState.CLAIMED
