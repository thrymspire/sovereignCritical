from gantt_ontology.mcp_domain import (
    Assertion,
    AuthorityTier,
    BoundaryAction,
    BoundaryContract,
    BoundaryEffect,
    ClaimType,
    ConditionOperator,
    ImpactLevel,
    RuleCondition,
    VerificationState,
)
from gantt_ontology.rule_engine import (
    ConditionResult,
    ContractEvaluationState,
    evaluate_boundary_contract,
)


def assertion(
    assertion_id: str,
    subject_id: str,
    predicate: str,
    value: object,
    *,
    state: VerificationState,
    tier: AuthorityTier,
) -> Assertion:
    evidence_ids = [f"evidence-{assertion_id}"] if state == VerificationState.INSTITUTIONALLY_VERIFIED else []
    # Assertion itself only checks evidence IDs are present; envelope reference
    # integrity is tested elsewhere.
    return Assertion(
        id=assertion_id,
        subjectId=subject_id,
        predicate=predicate,
        objectValue=value,
        claimType=(
            ClaimType.INSTITUTIONAL_FACT
            if tier == AuthorityTier.TIER_1_INSTITUTIONAL
            else ClaimType.PROVISIONAL_ASSERTION
        ),
        authorityTier=tier,
        verificationState=state,
        evidenceIds=evidence_ids,
    )


def grade_contract(*, impact: ImpactLevel = ImpactLevel.HIGH) -> BoundaryContract:
    return BoundaryContract(
        id="contract-grade-funding",
        name="Verified grade triggers academic/funding reevaluation",
        sourceLane="Academic",
        targetLanes=["Financial Aid / Funding", "Scholarships"],
        triggerPredicates=["finalGrade"],
        conditions=[
            RuleCondition(
                subjectId="course-1",
                predicate="finalGrade",
                operator=ConditionOperator.EQ,
                expectedValue="A",
            )
        ],
        effects=[
            BoundaryEffect(
                action=BoundaryAction.RECALCULATE,
                targetEntityId="academic-standing",
                targetPredicate="gpa",
                description="Recalculate GPA from verified course outcomes.",
            ),
            BoundaryEffect(
                action=BoundaryAction.CREATE_REVIEW,
                targetEntityId="funding-state",
                description="Reevaluate funding and scholarship rules against updated academic standing.",
            ),
        ],
        deterministic=True,
        impactLevel=impact,
        humanReviewRequired=impact in {ImpactLevel.HIGH, ImpactLevel.CRITICAL},
    )


def test_provisional_grade_does_not_propagate() -> None:
    grade = assertion(
        "grade-claim",
        "course-1",
        "finalGrade",
        "A",
        state=VerificationState.CLAIMED,
        tier=AuthorityTier.TIER_5_PROVISIONAL,
    )

    result = evaluate_boundary_contract(
        grade_contract(),
        assertions=[grade],
        changed_assertion_ids=[grade.id],
    )

    assert result.state == ContractEvaluationState.NOT_TRIGGERED
    assert result.effects == []


def test_verified_a_triggers_high_impact_review_not_award_assertion() -> None:
    grade = assertion(
        "grade-verified",
        "course-1",
        "finalGrade",
        "A",
        state=VerificationState.INSTITUTIONALLY_VERIFIED,
        tier=AuthorityTier.TIER_1_INSTITUTIONAL,
    )

    result = evaluate_boundary_contract(
        grade_contract(),
        assertions=[grade],
        changed_assertion_ids=[grade.id],
    )

    assert result.state == ContractEvaluationState.REVIEW_REQUIRED
    assert len(result.effects) == 2
    assert all(effect.requires_human_review for effect in result.effects)
    assert {effect.action for effect in result.effects} == {
        BoundaryAction.RECALCULATE,
        BoundaryAction.CREATE_REVIEW,
    }
    assert not any(effect.action == BoundaryAction.SET for effect in result.effects)


def test_verified_nonmatching_grade_does_not_execute_effects() -> None:
    grade = assertion(
        "grade-b",
        "course-1",
        "finalGrade",
        "B",
        state=VerificationState.INSTITUTIONALLY_VERIFIED,
        tier=AuthorityTier.TIER_1_INSTITUTIONAL,
    )

    result = evaluate_boundary_contract(
        grade_contract(),
        assertions=[grade],
        changed_assertion_ids=[grade.id],
    )

    assert result.state == ContractEvaluationState.CONDITIONS_UNMET
    assert result.condition_evaluations[0].result == ConditionResult.UNMET
    assert result.effects == []


def test_missing_condition_value_is_unknown_not_false() -> None:
    trigger = assertion(
        "trigger",
        "other-course",
        "finalGrade",
        "A",
        state=VerificationState.INSTITUTIONALLY_VERIFIED,
        tier=AuthorityTier.TIER_1_INSTITUTIONAL,
    )

    result = evaluate_boundary_contract(
        grade_contract(),
        assertions=[trigger],
        changed_assertion_ids=[trigger.id],
    )

    assert result.state == ContractEvaluationState.CONDITIONS_UNKNOWN
    assert result.condition_evaluations[0].result == ConditionResult.UNKNOWN
    assert result.effects == []


def test_low_impact_deterministic_contract_can_propose_effects_without_review() -> None:
    grade = assertion(
        "grade-low-risk",
        "course-1",
        "finalGrade",
        "A",
        state=VerificationState.INSTITUTIONALLY_VERIFIED,
        tier=AuthorityTier.TIER_1_INSTITUTIONAL,
    )
    contract = grade_contract(impact=ImpactLevel.LOW)

    result = evaluate_boundary_contract(
        contract,
        assertions=[grade],
        changed_assertion_ids=[grade.id],
    )

    assert result.state == ContractEvaluationState.EFFECTS_PROPOSED
    assert not any(effect.requires_human_review for effect in result.effects)
