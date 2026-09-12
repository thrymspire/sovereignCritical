"""Source-preserving drop-in ingestion helpers for Master Critical Path.

The first supported normalized payload is a syllabus. Raw PDF/DOCX/text parsing is
intentionally a separate concern: parsers produce this structured payload, while
this module turns the payload into provenance-bearing MCP records.

Key invariant: extraction is not verification. Even an apparently official
syllabus enters as located evidence and claimed assertions until the applicable
corroboration policy promotes it.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import List, Optional

from pydantic import Field

from .mcp_domain import (
    Assignment,
    Assertion,
    AuthorityTier,
    ClaimType,
    CourseOffering,
    Evidence,
    ImportArtifact,
    ImportCandidate,
    ImportCandidateState,
    MCPDomainEnvelope,
    MCPModel,
    Source,
    SourceKind,
    Syllabus,
    VerificationState,
)


class SyllabusAssignmentPayload(MCPModel):
    title: str
    assignment_type: Optional[str] = Field(default=None, alias="assignmentType")
    description: Optional[str] = None
    due_at: Optional[datetime] = Field(default=None, alias="dueAt")
    points: Optional[float] = Field(default=None, ge=0)
    weight_percent: Optional[float] = Field(default=None, ge=0, le=100, alias="weightPercent")
    submission_method: Optional[str] = Field(default=None, alias="submissionMethod")
    rubric_ref: Optional[str] = Field(default=None, alias="rubricRef")
    prerequisite_reading_refs: List[str] = Field(
        default_factory=list,
        alias="prerequisiteReadingRefs",
    )


class SyllabusImportPayload(MCPModel):
    institution_id: str = Field(alias="institutionId")
    department: Optional[str] = None
    course_code: str = Field(alias="courseCode")
    section: Optional[str] = None
    title: str
    term: str
    credits: Optional[float] = Field(default=None, ge=0)
    modality: Optional[str] = None
    location: Optional[str] = None
    meeting_schedule: Optional[str] = Field(default=None, alias="meetingSchedule")
    instructor_names: List[str] = Field(default_factory=list, alias="instructorNames")
    office_hours: Optional[str] = Field(default=None, alias="officeHours")
    grading_scale: Optional[str] = Field(default=None, alias="gradingScale")
    attendance_policy: Optional[str] = Field(default=None, alias="attendancePolicy")
    late_work_policy: Optional[str] = Field(default=None, alias="lateWorkPolicy")
    makeup_policy: Optional[str] = Field(default=None, alias="makeupPolicy")
    integrity_policy_ref: Optional[str] = Field(default=None, alias="integrityPolicyRef")
    required_materials: List[str] = Field(default_factory=list, alias="requiredMaterials")
    learning_objective_ids: List[str] = Field(default_factory=list, alias="learningObjectiveIds")
    assignments: List[SyllabusAssignmentPayload] = Field(default_factory=list)


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()[:20]
    return f"{prefix}-{digest}"


def _claim_type(authority_tier: AuthorityTier) -> ClaimType:
    if authority_tier == AuthorityTier.TIER_1_INSTITUTIONAL:
        return ClaimType.INSTITUTIONAL_FACT
    if authority_tier == AuthorityTier.TIER_3_AUTHORITATIVE_EXTERNAL:
        return ClaimType.EXTERNAL_RULE
    return ClaimType.PROVISIONAL_ASSERTION


def _course_subject(payload: SyllabusImportPayload) -> str:
    section = payload.section or "unspecified-section"
    return (
        f"course-offering:{payload.institution_id}:"
        f"{payload.course_code}:{section}:{payload.term}"
    ).replace(" ", "-")


def ingest_syllabus_payload(
    payload: SyllabusImportPayload,
    *,
    acquired_at: datetime,
    artifact_sha256: str,
    original_filename: str,
    stored_ref: str,
    media_type: Optional[str] = None,
    issuer: Optional[str] = None,
    source_authority: AuthorityTier = AuthorityTier.TIER_5_PROVISIONAL,
    source_kind: SourceKind = SourceKind.USER_SUPPLIED_DOCUMENT,
    source_uri: Optional[str] = None,
) -> MCPDomainEnvelope:
    """Convert a normalized syllabus into an auditable MCP import envelope.

    ``artifact_sha256`` is the hash of the original bytes. The caller is
    responsible for storing those bytes at ``stored_ref`` before invoking this
    function. This function never mutates or deletes the original artifact.
    """

    if len(artifact_sha256) != 64 or any(c not in "0123456789abcdefABCDEF" for c in artifact_sha256):
        raise ValueError("artifact_sha256 must be a 64-character hexadecimal SHA-256")

    artifact_sha256 = artifact_sha256.lower()
    source_id = f"source-syllabus-{artifact_sha256[:20]}"
    artifact_id = f"artifact-syllabus-{artifact_sha256[:20]}"
    course_id = _stable_id(
        "course",
        payload.institution_id,
        payload.course_code,
        payload.section or "",
        payload.term,
    )
    syllabus_id = _stable_id("syllabus", artifact_sha256, course_id)

    source = Source(
        id=source_id,
        kind=source_kind,
        authorityTier=source_authority,
        title=f"Syllabus: {payload.course_code} — {payload.title}",
        issuer=issuer,
        uri=source_uri,
        acquiredAt=acquired_at,
        sha256=artifact_sha256,
        originalArtifactRef=stored_ref,
        notes="Source artifact preserved. Extraction is not equivalent to verification.",
    )

    artifact = ImportArtifact(
        id=artifact_id,
        sourceId=source_id,
        originalFilename=original_filename,
        mediaType=media_type,
        sha256=artifact_sha256,
        acquiredAt=acquired_at,
        storedRef=stored_ref,
        originalPreserved=True,
        schemaHint="mcp.syllabus.v1",
    )

    evidence_records: list[Evidence] = []
    assertions: list[Assertion] = []
    import_candidates: list[ImportCandidate] = []

    def add_claim(subject_id: str, predicate: str, value: object, locator: str) -> str:
        serialized = _canonical_json(value)
        assertion_id = _stable_id(
            "assertion-syllabus",
            artifact_sha256,
            subject_id,
            predicate,
            serialized,
        )
        evidence_id = _stable_id("evidence-syllabus", assertion_id, locator)
        candidate_id = _stable_id("candidate-syllabus", assertion_id)

        evidence = Evidence(
            id=evidence_id,
            sourceId=source_id,
            locator=locator,
            capturedValue=value,
            acquiredAt=acquired_at,
            verificationState=VerificationState.EVIDENCE_LOCATED,
            notes="Value extracted from preserved syllabus artifact; applicability still reviewable.",
        )
        assertion = Assertion(
            id=assertion_id,
            subjectId=subject_id,
            predicate=predicate,
            objectValue=value,
            claimType=_claim_type(source_authority),
            authorityTier=source_authority,
            verificationState=VerificationState.EVIDENCE_LOCATED,
            evidenceIds=[evidence_id],
            confidence=None,
            notes="Extracted syllabus claim. Not institutionally verified by extraction alone.",
        )
        candidate = ImportCandidate(
            id=candidate_id,
            importArtifactId=artifact_id,
            proposedAssertion=assertion,
            locator=locator,
            extractionMethod="normalized-syllabus-adapter-v1",
            state=ImportCandidateState.EXTRACTED,
        )

        evidence_records.append(evidence)
        assertions.append(assertion)
        import_candidates.append(candidate)
        return assertion_id

    course_subject = _course_subject(payload)
    course_claim_ids: list[str] = []
    course_fields = {
        "institutionId": payload.institution_id,
        "department": payload.department,
        "courseCode": payload.course_code,
        "section": payload.section,
        "title": payload.title,
        "term": payload.term,
        "credits": payload.credits,
        "modality": payload.modality,
        "location": payload.location,
        "meetingSchedule": payload.meeting_schedule,
        "instructorNames": payload.instructor_names,
    }
    for field_name, value in course_fields.items():
        if value is not None and value != []:
            course_claim_ids.append(
                add_claim(course_subject, field_name, value, f"syllabus.course.{field_name}")
            )

    syllabus_claim_ids: list[str] = []
    syllabus_subject = f"syllabus:{syllabus_id}"
    syllabus_fields = {
        "officeHours": payload.office_hours,
        "gradingScale": payload.grading_scale,
        "attendancePolicy": payload.attendance_policy,
        "lateWorkPolicy": payload.late_work_policy,
        "makeupPolicy": payload.makeup_policy,
        "integrityPolicyRef": payload.integrity_policy_ref,
        "requiredMaterials": payload.required_materials,
        "learningObjectiveIds": payload.learning_objective_ids,
    }
    for field_name, value in syllabus_fields.items():
        if value is not None and value != []:
            syllabus_claim_ids.append(
                add_claim(syllabus_subject, field_name, value, f"syllabus.policy.{field_name}")
            )

    course = CourseOffering(
        id=course_id,
        institutionId=payload.institution_id,
        department=payload.department,
        courseCode=payload.course_code,
        section=payload.section,
        title=payload.title,
        term=payload.term,
        credits=payload.credits,
        modality=payload.modality,
        location=payload.location,
        meetingSchedule=payload.meeting_schedule,
        sourceAssertionIds=course_claim_ids,
        verificationState=VerificationState.EVIDENCE_LOCATED,
    )

    syllabus = Syllabus(
        id=syllabus_id,
        courseOfferingId=course_id,
        sourceId=source_id,
        gradingScale=payload.grading_scale,
        attendancePolicy=payload.attendance_policy,
        lateWorkPolicy=payload.late_work_policy,
        makeupPolicy=payload.makeup_policy,
        integrityPolicyRef=payload.integrity_policy_ref,
        officeHours=payload.office_hours,
        requiredMaterials=payload.required_materials,
        learningObjectiveIds=payload.learning_objective_ids,
        verificationState=VerificationState.EVIDENCE_LOCATED,
    )

    assignments: list[Assignment] = []
    for index, item in enumerate(payload.assignments):
        assignment_id = _stable_id(
            "assignment",
            artifact_sha256,
            course_id,
            str(index),
            item.title,
        )
        assignment_subject = f"assignment:{assignment_id}"
        assignment_claim_ids: list[str] = []
        assignment_fields = {
            "title": item.title,
            "assignmentType": item.assignment_type,
            "description": item.description,
            "dueAt": item.due_at.isoformat() if item.due_at else None,
            "points": item.points,
            "weightPercent": item.weight_percent,
            "submissionMethod": item.submission_method,
            "rubricRef": item.rubric_ref,
            "prerequisiteReadingRefs": item.prerequisite_reading_refs,
        }
        for field_name, value in assignment_fields.items():
            if value is not None and value != []:
                assignment_claim_ids.append(
                    add_claim(
                        assignment_subject,
                        field_name,
                        value,
                        f"syllabus.assignments[{index}].{field_name}",
                    )
                )

        assignments.append(
            Assignment(
                id=assignment_id,
                courseOfferingId=course_id,
                syllabusId=syllabus_id,
                title=item.title,
                assignmentType=item.assignment_type,
                description=item.description,
                dueAt=item.due_at,
                points=item.points,
                weightPercent=item.weight_percent,
                submissionMethod=item.submission_method,
                rubricRef=item.rubric_ref,
                prerequisiteReadingRefs=item.prerequisite_reading_refs,
                sourceAssertionIds=assignment_claim_ids,
                verificationState=VerificationState.EVIDENCE_LOCATED,
            )
        )

    # ``syllabus_claim_ids`` intentionally exist as assertions even though the
    # Syllabus entity points directly to its immutable Source. They allow each
    # policy field to be contradicted/superseded independently.
    _ = syllabus_claim_ids

    return MCPDomainEnvelope(
        createdAt=acquired_at,
        sources=[source],
        evidence=evidence_records,
        assertions=assertions,
        courseOfferings=[course],
        syllabi=[syllabus],
        assignments=assignments,
        importArtifacts=[artifact],
        importCandidates=import_candidates,
    )
