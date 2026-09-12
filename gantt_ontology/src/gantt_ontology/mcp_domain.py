"""Master Critical Path provenance-first domain ontology.

This module is intentionally additive to the legacy Gantt scheduling model.
It defines the truth/evidence envelope required to distinguish institutional
facts, deterministic derivations, external rules, provisional legacy claims,
and generated suggestions without prematurely rewriting the existing schedule.

Design invariants
-----------------
1. Legacy claims may exist as PROVISIONAL without evidence.
2. Institutionally verified assertions require Tier-1 authority and evidence.
3. Derived assertions require explicit assertion lineage.
4. Contradictions are represented, never silently overwritten.
5. Suggestions are separate entities and cannot become assertions implicitly.
6. Drop-in imports preserve the original artifact and field-level candidates.
7. Scholarship, syllabus, proof, and notification rules are first-class data.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MCPModel(BaseModel):
    """Strict base model for all MCP domain records."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class AuthorityTier(str, Enum):
    TIER_1_INSTITUTIONAL = "Tier1Institutional"
    TIER_2_DERIVED = "Tier2Derived"
    TIER_3_AUTHORITATIVE_EXTERNAL = "Tier3AuthoritativeExternal"
    TIER_4_CORROBORATED_SECONDARY = "Tier4CorroboratedSecondary"
    TIER_5_PROVISIONAL = "Tier5Provisional"


class VerificationState(str, Enum):
    UNKNOWN = "Unknown"
    CLAIMED = "Claimed"
    EVIDENCE_LOCATED = "EvidenceLocated"
    CORROBORATED = "Corroborated"
    INSTITUTIONALLY_VERIFIED = "InstitutionallyVerified"
    DERIVED = "Derived"
    CONTRADICTED = "Contradicted"
    SUPERSEDED = "Superseded"
    EXPIRED = "Expired"
    NEEDS_REVIEW = "NeedsReview"


class ClaimType(str, Enum):
    INSTITUTIONAL_FACT = "InstitutionalFact"
    DERIVED_ASSERTION = "DerivedAssertion"
    EXTERNAL_RULE = "ExternalRule"
    PROVISIONAL_ASSERTION = "ProvisionalAssertion"
    PREDICTION = "Prediction"


class SourceKind(str, Enum):
    INSTITUTIONAL_RECORD = "InstitutionalRecord"
    OFFICIAL_WEB = "OfficialWeb"
    OFFICIAL_EMAIL = "OfficialEmail"
    SIGNED_AGREEMENT = "SignedAgreement"
    GOVERNMENT_RECORD = "GovernmentRecord"
    USER_SUPPLIED_DOCUMENT = "UserSuppliedDocument"
    SECONDARY_SOURCE = "SecondarySource"
    MANUAL_ENTRY = "ManualEntry"
    LEGACY_REPOSITORY = "LegacyRepository"


class ImpactLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class ConditionOperator(str, Enum):
    EQ = "eq"
    NE = "ne"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    IN = "in"
    NOT_IN = "notIn"
    EXISTS = "exists"


class BoundaryAction(str, Enum):
    SET = "Set"
    RECALCULATE = "Recalculate"
    CREATE_REVIEW = "CreateReview"
    CREATE_TASK = "CreateTask"
    NOTIFY = "Notify"
    INVALIDATE = "Invalidate"
    REOPEN = "Reopen"


class NotificationSeverity(str, Enum):
    INFORMATIONAL = "Informational"
    UPCOMING = "Upcoming"
    ACTION_REQUIRED = "ActionRequired"
    CRITICAL = "Critical"
    BLOCKED = "Blocked"
    VERIFICATION_REQUIRED = "VerificationRequired"


class ImportCandidateState(str, Enum):
    EXTRACTED = "Extracted"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    CONFLICT = "Conflict"
    NEEDS_REVIEW = "NeedsReview"


class SuggestionKind(str, Enum):
    TOPIC = "Topic"
    THESIS = "Thesis"
    RESEARCH_QUESTION = "ResearchQuestion"
    COUNTERARGUMENT = "Counterargument"
    ARGUMENT_MAP = "ArgumentMap"
    READING_PLAN = "ReadingPlan"
    TASK_DECOMPOSITION = "TaskDecomposition"
    RESEARCH_TERM = "ResearchTerm"
    EVIDENCE_GAP = "EvidenceGap"
    RUBRIC_MAPPING = "RubricMapping"
    NEXT_ACTION = "NextAction"


class SuggestionState(str, Enum):
    PROPOSED = "Proposed"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    ARCHIVED = "Archived"


class EntityRef(MCPModel):
    entity_id: str = Field(alias="entityId")
    entity_type: str = Field(alias="entityType")
    label: Optional[str] = None


class Source(MCPModel):
    id: str
    kind: SourceKind
    authority_tier: AuthorityTier = Field(alias="authorityTier")
    title: str
    issuer: Optional[str] = None
    uri: Optional[str] = None
    acquired_at: datetime = Field(alias="acquiredAt")
    document_date: Optional[date] = Field(default=None, alias="documentDate")
    effective_from: Optional[date] = Field(default=None, alias="effectiveFrom")
    effective_to: Optional[date] = Field(default=None, alias="effectiveTo")
    version: Optional[str] = None
    sha256: Optional[str] = None
    original_artifact_ref: Optional[str] = Field(default=None, alias="originalArtifactRef")
    notes: Optional[str] = None


class Evidence(MCPModel):
    id: str
    source_id: str = Field(alias="sourceId")
    locator: Optional[str] = None
    captured_value: Optional[Any] = Field(default=None, alias="capturedValue")
    captured_text_hash: Optional[str] = Field(default=None, alias="capturedTextHash")
    acquired_at: datetime = Field(alias="acquiredAt")
    verification_state: VerificationState = Field(
        default=VerificationState.EVIDENCE_LOCATED,
        alias="verificationState",
    )
    reviewer: Optional[str] = None
    notes: Optional[str] = None


class Assertion(MCPModel):
    id: str
    subject_id: str = Field(alias="subjectId")
    predicate: str
    object_value: Optional[Any] = Field(default=None, alias="objectValue")
    object_entity_id: Optional[str] = Field(default=None, alias="objectEntityId")
    claim_type: ClaimType = Field(alias="claimType")
    authority_tier: AuthorityTier = Field(alias="authorityTier")
    verification_state: VerificationState = Field(alias="verificationState")
    evidence_ids: List[str] = Field(default_factory=list, alias="evidenceIds")
    derived_from_assertion_ids: List[str] = Field(
        default_factory=list,
        alias="derivedFromAssertionIds",
    )
    contradicts_assertion_ids: List[str] = Field(
        default_factory=list,
        alias="contradictsAssertionIds",
    )
    supersedes_assertion_ids: List[str] = Field(
        default_factory=list,
        alias="supersedesAssertionIds",
    )
    effective_from: Optional[datetime] = Field(default=None, alias="effectiveFrom")
    effective_to: Optional[datetime] = Field(default=None, alias="effectiveTo")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    responsible_entity_id: Optional[str] = Field(default=None, alias="responsibleEntityId")
    affected_entity_ids: List[str] = Field(default_factory=list, alias="affectedEntityIds")
    affected_contract_ids: List[str] = Field(default_factory=list, alias="affectedContractIds")
    human_review_required: bool = Field(default=False, alias="humanReviewRequired")
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_truth_semantics(self) -> "Assertion":
        if self.object_value is None and self.object_entity_id is None:
            raise ValueError("Assertion requires objectValue or objectEntityId")

        if self.claim_type == ClaimType.DERIVED_ASSERTION:
            if self.authority_tier != AuthorityTier.TIER_2_DERIVED:
                raise ValueError("DerivedAssertion must use Tier2Derived authority")
            if not self.derived_from_assertion_ids:
                raise ValueError("DerivedAssertion requires derivedFromAssertionIds")
            if self.verification_state != VerificationState.DERIVED:
                raise ValueError("DerivedAssertion must use Derived verification state")

        if self.verification_state == VerificationState.INSTITUTIONALLY_VERIFIED:
            if self.authority_tier != AuthorityTier.TIER_1_INSTITUTIONAL:
                raise ValueError(
                    "InstitutionallyVerified assertion must use Tier1Institutional authority"
                )
            if not self.evidence_ids:
                raise ValueError("InstitutionallyVerified assertion requires evidenceIds")

        if self.authority_tier in {
            AuthorityTier.TIER_1_INSTITUTIONAL,
            AuthorityTier.TIER_3_AUTHORITATIVE_EXTERNAL,
            AuthorityTier.TIER_4_CORROBORATED_SECONDARY,
        } and self.verification_state in {
            VerificationState.CORROBORATED,
            VerificationState.INSTITUTIONALLY_VERIFIED,
        }:
            if not self.evidence_ids:
                raise ValueError("Corroborated/verified assertions require evidenceIds")

        return self


class RuleCondition(MCPModel):
    subject_id: Optional[str] = Field(default=None, alias="subjectId")
    predicate: str
    operator: ConditionOperator
    expected_value: Optional[Any] = Field(default=None, alias="expectedValue")
    source_assertion_ids: List[str] = Field(default_factory=list, alias="sourceAssertionIds")


class BoundaryEffect(MCPModel):
    action: BoundaryAction
    target_entity_id: Optional[str] = Field(default=None, alias="targetEntityId")
    target_predicate: Optional[str] = Field(default=None, alias="targetPredicate")
    value: Optional[Any] = None
    description: str


class BoundaryContract(MCPModel):
    id: str
    name: str
    description: Optional[str] = None
    source_lane: Optional[str] = Field(default=None, alias="sourceLane")
    target_lanes: List[str] = Field(default_factory=list, alias="targetLanes")
    trigger_predicates: List[str] = Field(default_factory=list, alias="triggerPredicates")
    conditions: List[RuleCondition] = Field(default_factory=list)
    effects: List[BoundaryEffect] = Field(default_factory=list)
    deterministic: bool = True
    impact_level: ImpactLevel = Field(default=ImpactLevel.MEDIUM, alias="impactLevel")
    human_review_required: bool = Field(default=False, alias="humanReviewRequired")
    source_assertion_ids: List[str] = Field(default_factory=list, alias="sourceAssertionIds")
    enabled: bool = True

    @model_validator(mode="after")
    def require_review_for_nondeterministic_high_impact(self) -> "BoundaryContract":
        if not self.deterministic and self.impact_level in {
            ImpactLevel.HIGH,
            ImpactLevel.CRITICAL,
        } and not self.human_review_required:
            raise ValueError(
                "High-impact non-deterministic contracts must require human review"
            )
        return self


class ProofRequirement(MCPModel):
    id: str
    label: str
    description: Optional[str] = None
    accepted_source_kinds: List[SourceKind] = Field(
        default_factory=list,
        alias="acceptedSourceKinds",
    )
    minimum_authority_tier: Optional[AuthorityTier] = Field(
        default=None,
        alias="minimumAuthorityTier",
    )
    requires_human_review: bool = Field(default=False, alias="requiresHumanReview")
    required: bool = True


class CourseOffering(MCPModel):
    id: str
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
    instructor_entity_ids: List[str] = Field(default_factory=list, alias="instructorEntityIds")
    source_assertion_ids: List[str] = Field(default_factory=list, alias="sourceAssertionIds")
    verification_state: VerificationState = Field(
        default=VerificationState.CLAIMED,
        alias="verificationState",
    )


class Syllabus(MCPModel):
    id: str
    course_offering_id: str = Field(alias="courseOfferingId")
    source_id: str = Field(alias="sourceId")
    grading_scale: Optional[str] = Field(default=None, alias="gradingScale")
    attendance_policy: Optional[str] = Field(default=None, alias="attendancePolicy")
    late_work_policy: Optional[str] = Field(default=None, alias="lateWorkPolicy")
    makeup_policy: Optional[str] = Field(default=None, alias="makeupPolicy")
    integrity_policy_ref: Optional[str] = Field(default=None, alias="integrityPolicyRef")
    office_hours: Optional[str] = Field(default=None, alias="officeHours")
    required_materials: List[str] = Field(default_factory=list, alias="requiredMaterials")
    learning_objective_ids: List[str] = Field(default_factory=list, alias="learningObjectiveIds")
    verification_state: VerificationState = Field(
        default=VerificationState.EVIDENCE_LOCATED,
        alias="verificationState",
    )


class Assignment(MCPModel):
    id: str
    course_offering_id: str = Field(alias="courseOfferingId")
    syllabus_id: Optional[str] = Field(default=None, alias="syllabusId")
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
    learning_objective_ids: List[str] = Field(default_factory=list, alias="learningObjectiveIds")
    proof_requirement_ids: List[str] = Field(default_factory=list, alias="proofRequirementIds")
    source_assertion_ids: List[str] = Field(default_factory=list, alias="sourceAssertionIds")
    verification_state: VerificationState = Field(
        default=VerificationState.CLAIMED,
        alias="verificationState",
    )


class EligibilityCriterion(MCPModel):
    id: str
    label: str
    subject_field: str = Field(alias="subjectField")
    operator: ConditionOperator
    expected_value: Optional[Any] = Field(default=None, alias="expectedValue")
    required: bool = True
    source_assertion_ids: List[str] = Field(default_factory=list, alias="sourceAssertionIds")


class RequiredDocument(MCPModel):
    id: str
    label: str
    description: Optional[str] = None
    accepted_media_types: List[str] = Field(default_factory=list, alias="acceptedMediaTypes")
    submission_channel: Optional[str] = Field(default=None, alias="submissionChannel")
    required: bool = True
    source_assertion_ids: List[str] = Field(default_factory=list, alias="sourceAssertionIds")


class ApplicationWindow(MCPModel):
    id: str
    term_label: Optional[str] = Field(default=None, alias="termLabel")
    opens_at: Optional[datetime] = Field(default=None, alias="opensAt")
    priority_deadline: Optional[datetime] = Field(default=None, alias="priorityDeadline")
    closes_at: Optional[datetime] = Field(default=None, alias="closesAt")
    rolling: bool = False
    source_assertion_ids: List[str] = Field(default_factory=list, alias="sourceAssertionIds")

    @model_validator(mode="after")
    def validate_window_order(self) -> "ApplicationWindow":
        if self.opens_at and self.closes_at and self.closes_at < self.opens_at:
            raise ValueError("Application window closesAt cannot precede opensAt")
        if (
            self.priority_deadline
            and self.opens_at
            and self.priority_deadline < self.opens_at
        ):
            raise ValueError("priorityDeadline cannot precede opensAt")
        if (
            self.priority_deadline
            and self.closes_at
            and self.priority_deadline > self.closes_at
        ):
            raise ValueError("priorityDeadline cannot follow closesAt")
        return self


class AwardFormula(MCPModel):
    currency: str = "USD"
    per_credit_amount: Optional[float] = Field(default=None, ge=0, alias="perCreditAmount")
    max_per_term: Optional[float] = Field(default=None, ge=0, alias="maxPerTerm")
    max_per_year: Optional[float] = Field(default=None, ge=0, alias="maxPerYear")
    lifetime_max: Optional[float] = Field(default=None, ge=0, alias="lifetimeMax")
    fixed_amount: Optional[float] = Field(default=None, ge=0, alias="fixedAmount")
    notes: Optional[str] = None
    source_assertion_ids: List[str] = Field(default_factory=list, alias="sourceAssertionIds")


class ScholarshipProgram(MCPModel):
    id: str
    sponsor_entity_id: str = Field(alias="sponsorEntityId")
    name: str
    program_url: Optional[str] = Field(default=None, alias="programUrl")
    renewable: Optional[bool] = None
    criterion_ids: List[str] = Field(default_factory=list, alias="criterionIds")
    required_document_ids: List[str] = Field(
        default_factory=list,
        alias="requiredDocumentIds",
    )
    application_windows: List[ApplicationWindow] = Field(
        default_factory=list,
        alias="applicationWindows",
    )
    award_formula: Optional[AwardFormula] = Field(default=None, alias="awardFormula")
    source_assertion_ids: List[str] = Field(default_factory=list, alias="sourceAssertionIds")
    verification_state: VerificationState = Field(
        default=VerificationState.CLAIMED,
        alias="verificationState",
    )


class NotificationPolicy(MCPModel):
    id: str
    name: str
    trigger_predicates: List[str] = Field(default_factory=list, alias="triggerPredicates")
    lead_times_minutes: List[int] = Field(default_factory=list, alias="leadTimesMinutes")
    severity: NotificationSeverity = NotificationSeverity.UPCOMING
    channels: List[str] = Field(default_factory=lambda: ["desktop"])
    dedupe_key_template: Optional[str] = Field(default=None, alias="dedupeKeyTemplate")
    enabled: bool = True

    @model_validator(mode="after")
    def validate_lead_times(self) -> "NotificationPolicy":
        if any(value < 0 for value in self.lead_times_minutes):
            raise ValueError("Notification lead times must be non-negative")
        if len(self.lead_times_minutes) != len(set(self.lead_times_minutes)):
            raise ValueError("Notification lead times must be unique")
        return self


class ImportArtifact(MCPModel):
    id: str
    source_id: str = Field(alias="sourceId")
    original_filename: str = Field(alias="originalFilename")
    media_type: Optional[str] = Field(default=None, alias="mediaType")
    sha256: str
    acquired_at: datetime = Field(alias="acquiredAt")
    stored_ref: str = Field(alias="storedRef")
    original_preserved: bool = Field(default=True, alias="originalPreserved")
    schema_hint: Optional[str] = Field(default=None, alias="schemaHint")

    @model_validator(mode="after")
    def require_original_preservation(self) -> "ImportArtifact":
        if not self.original_preserved:
            raise ValueError("ImportArtifact must preserve the original artifact")
        return self


class ImportCandidate(MCPModel):
    id: str
    import_artifact_id: str = Field(alias="importArtifactId")
    proposed_assertion: Assertion = Field(alias="proposedAssertion")
    locator: Optional[str] = None
    extraction_method: Optional[str] = Field(default=None, alias="extractionMethod")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    state: ImportCandidateState = ImportCandidateState.EXTRACTED
    conflict_assertion_ids: List[str] = Field(default_factory=list, alias="conflictAssertionIds")
    notes: Optional[str] = None


class Suggestion(MCPModel):
    id: str
    kind: SuggestionKind
    title: str
    body: str
    based_on_assertion_ids: List[str] = Field(default_factory=list, alias="basedOnAssertionIds")
    source_entity_ids: List[str] = Field(default_factory=list, alias="sourceEntityIds")
    generated_at: datetime = Field(alias="generatedAt")
    state: SuggestionState = SuggestionState.PROPOSED
    accepted_as_entity_id: Optional[str] = Field(default=None, alias="acceptedAsEntityId")


class MCPDomainEnvelope(MCPModel):
    """Versioned truth/evidence sidecar for the legacy scheduling graph.

    The envelope can be introduced before migrating legacy task storage. It is
    deliberately reference-oriented so institutional source artifacts remain
    immutable while claims and derived consequences evolve.
    """

    schema_version: str = Field(default="2.0.0", alias="schemaVersion")
    created_at: datetime = Field(alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")
    legacy_graph_ref: Optional[str] = Field(default=None, alias="legacyGraphRef")

    sources: List[Source] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)
    assertions: List[Assertion] = Field(default_factory=list)
    boundary_contracts: List[BoundaryContract] = Field(
        default_factory=list,
        alias="boundaryContracts",
    )
    proof_requirements: List[ProofRequirement] = Field(
        default_factory=list,
        alias="proofRequirements",
    )

    course_offerings: List[CourseOffering] = Field(default_factory=list, alias="courseOfferings")
    syllabi: List[Syllabus] = Field(default_factory=list)
    assignments: List[Assignment] = Field(default_factory=list)

    scholarship_criteria: List[EligibilityCriterion] = Field(
        default_factory=list,
        alias="scholarshipCriteria",
    )
    required_documents: List[RequiredDocument] = Field(
        default_factory=list,
        alias="requiredDocuments",
    )
    scholarships: List[ScholarshipProgram] = Field(default_factory=list)

    notification_policies: List[NotificationPolicy] = Field(
        default_factory=list,
        alias="notificationPolicies",
    )
    import_artifacts: List[ImportArtifact] = Field(default_factory=list, alias="importArtifacts")
    import_candidates: List[ImportCandidate] = Field(default_factory=list, alias="importCandidates")
    suggestions: List[Suggestion] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_reference_integrity(self) -> "MCPDomainEnvelope":
        collections = {
            "source": self.sources,
            "evidence": self.evidence,
            "assertion": self.assertions,
            "boundaryContract": self.boundary_contracts,
            "proofRequirement": self.proof_requirements,
            "courseOffering": self.course_offerings,
            "syllabus": self.syllabi,
            "scholarshipCriterion": self.scholarship_criteria,
            "requiredDocument": self.required_documents,
            "scholarship": self.scholarships,
            "notificationPolicy": self.notification_policies,
            "importArtifact": self.import_artifacts,
            "importCandidate": self.import_candidates,
            "suggestion": self.suggestions,
        }

        all_ids: dict[str, str] = {}
        for entity_type, items in collections.items():
            for item in items:
                if item.id in all_ids:
                    raise ValueError(
                        f"Duplicate id '{item.id}' across {all_ids[item.id]} and {entity_type}"
                    )
                all_ids[item.id] = entity_type

        source_ids = {item.id for item in self.sources}
        evidence_ids = {item.id for item in self.evidence}
        assertion_ids = {item.id for item in self.assertions}
        contract_ids = {item.id for item in self.boundary_contracts}
        proof_ids = {item.id for item in self.proof_requirements}
        course_ids = {item.id for item in self.course_offerings}
        syllabus_ids = {item.id for item in self.syllabi}
        criterion_ids = {item.id for item in self.scholarship_criteria}
        required_document_ids = {item.id for item in self.required_documents}
        import_artifact_ids = {item.id for item in self.import_artifacts}

        def require_refs(refs: List[str], valid: set[str], label: str) -> None:
            missing = sorted(set(refs) - valid)
            if missing:
                raise ValueError(f"Missing {label} references: {missing}")

        for item in self.evidence:
            require_refs([item.source_id], source_ids, "source")

        for item in self.assertions:
            require_refs(item.evidence_ids, evidence_ids, "evidence")
            require_refs(item.derived_from_assertion_ids, assertion_ids, "assertion lineage")
            require_refs(item.contradicts_assertion_ids, assertion_ids, "contradiction assertion")
            require_refs(item.supersedes_assertion_ids, assertion_ids, "supersession assertion")
            require_refs(item.affected_contract_ids, contract_ids, "boundary contract")

        for item in self.boundary_contracts:
            require_refs(item.source_assertion_ids, assertion_ids, "contract source assertion")
            for condition in item.conditions:
                require_refs(
                    condition.source_assertion_ids,
                    assertion_ids,
                    "condition source assertion",
                )

        for item in self.course_offerings:
            require_refs(item.source_assertion_ids, assertion_ids, "course source assertion")

        for item in self.syllabi:
            require_refs([item.source_id], source_ids, "syllabus source")
            require_refs([item.course_offering_id], course_ids, "course offering")

        for item in self.assignments:
            require_refs([item.course_offering_id], course_ids, "assignment course offering")
            if item.syllabus_id:
                require_refs([item.syllabus_id], syllabus_ids, "syllabus")
            require_refs(item.proof_requirement_ids, proof_ids, "proof requirement")
            require_refs(item.source_assertion_ids, assertion_ids, "assignment source assertion")

        for item in self.scholarship_criteria:
            require_refs(item.source_assertion_ids, assertion_ids, "criterion source assertion")

        for item in self.required_documents:
            require_refs(item.source_assertion_ids, assertion_ids, "document source assertion")

        for item in self.scholarships:
            require_refs(item.criterion_ids, criterion_ids, "scholarship criterion")
            require_refs(item.required_document_ids, required_document_ids, "required document")
            require_refs(item.source_assertion_ids, assertion_ids, "scholarship source assertion")
            if item.award_formula:
                require_refs(
                    item.award_formula.source_assertion_ids,
                    assertion_ids,
                    "award formula source assertion",
                )
            for window in item.application_windows:
                require_refs(
                    window.source_assertion_ids,
                    assertion_ids,
                    "application window source assertion",
                )

        for item in self.import_artifacts:
            require_refs([item.source_id], source_ids, "import source")

        for item in self.import_candidates:
            require_refs([item.import_artifact_id], import_artifact_ids, "import artifact")
            require_refs(item.conflict_assertion_ids, assertion_ids, "conflict assertion")

        for item in self.suggestions:
            require_refs(item.based_on_assertion_ids, assertion_ids, "suggestion assertion")

        return self

    def to_canonical_dict(self) -> dict:
        """Serialize using schema aliases and JSON-safe values."""
        return self.model_dump(by_alias=True, exclude_none=True, mode="json")
