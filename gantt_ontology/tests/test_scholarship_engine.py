from gantt_ontology.mcp_domain import (
    AuthorityTier,
    ConditionOperator,
    EligibilityCriterion,
    ScholarshipProgram,
    VerificationState,
)
from gantt_ontology.scholarship_engine import (
    CriterionState,
    ScholarshipEligibilityState,
    evaluate_scholarship,
)


def criterion(
    criterion_id: str,
    field: str,
    operator: ConditionOperator,
    expected: object,
    *,
    required: bool = True,
) -> EligibilityCriterion:
    return EligibilityCriterion(
        id=criterion_id,
        label=criterion_id,
        subjectField=field,
        operator=operator,
        expectedValue=expected,
        required=required,
    )


def program(*criterion_ids: str) -> ScholarshipProgram:
    return ScholarshipProgram(
        id="scholarship-1",
        sponsorEntityId="sponsor-1",
        name="Example Scholarship",
        criterionIds=list(criterion_ids),
        verificationState=VerificationState.EVIDENCE_LOCATED,
    )


def test_missing_required_fact_is_unknown_not_ineligible() -> None:
    gpa = criterion("gpa-min", "academic.cumulativeGpa", ConditionOperator.GTE, 3.0)

    result = evaluate_scholarship(
        program(gpa.id),
        criteria_by_id={gpa.id: gpa},
        facts={},
    )

    assert result.state == ScholarshipEligibilityState.UNKNOWN
    assert result.criteria[0].state == CriterionState.UNKNOWN
    assert result.missing_fields == ["academic.cumulativeGpa"]


def test_unmet_required_fact_is_ineligible() -> None:
    gpa = criterion("gpa-min", "academic.cumulativeGpa", ConditionOperator.GTE, 3.0)

    result = evaluate_scholarship(
        program(gpa.id),
        criteria_by_id={gpa.id: gpa},
        facts={"academic": {"cumulativeGpa": 2.75}},
    )

    assert result.state == ScholarshipEligibilityState.INELIGIBLE
    assert result.criteria[0].state == CriterionState.UNMET
    assert result.unmet_criterion_ids == ["gpa-min"]


def test_all_required_criteria_met_produces_candidate_not_award() -> None:
    gpa = criterion("gpa-min", "academic.cumulativeGpa", ConditionOperator.GTE, 3.0)
    enrollment = criterion(
        "enrollment",
        "academic.enrollmentStatus",
        ConditionOperator.IN,
        ["HalfTime", "ThreeQuarterTime", "FullTime"],
    )

    result = evaluate_scholarship(
        program(gpa.id, enrollment.id),
        criteria_by_id={gpa.id: gpa, enrollment.id: enrollment},
        facts={
            "academic": {
                "cumulativeGpa": 3.5,
                "enrollmentStatus": "FullTime",
            }
        },
    )

    assert result.state == ScholarshipEligibilityState.ELIGIBLE_CANDIDATE
    assert all(item.state == CriterionState.MET for item in result.criteria)
    assert "not an award decision" in result.reason


def test_optional_unknown_criterion_does_not_block_candidate_status() -> None:
    gpa = criterion("gpa-min", "academic.cumulativeGpa", ConditionOperator.GTE, 3.0)
    optional = criterion(
        "optional-community",
        "profile.communityServiceHours",
        ConditionOperator.GTE,
        20,
        required=False,
    )

    result = evaluate_scholarship(
        program(gpa.id, optional.id),
        criteria_by_id={gpa.id: gpa, optional.id: optional},
        facts={"academic": {"cumulativeGpa": 3.7}},
    )

    assert result.state == ScholarshipEligibilityState.ELIGIBLE_CANDIDATE
    assert result.criteria[1].state == CriterionState.UNKNOWN


def test_missing_criterion_definition_forces_unknown() -> None:
    result = evaluate_scholarship(
        program("criterion-not-loaded"),
        criteria_by_id={},
        facts={"academic": {"cumulativeGpa": 4.0}},
    )

    assert result.state == ScholarshipEligibilityState.UNKNOWN
    assert result.missing_fields == ["criterion:criterion-not-loaded"]
