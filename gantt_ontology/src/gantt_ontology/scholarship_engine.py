"""Tri-state scholarship eligibility evaluation.

Scholarship programs are externally governed and their rules change. This
module therefore evaluates only criteria already represented in the ontology;
it contains no sponsor-specific policy constants.

Unknown facts remain UNKNOWN. They are never coerced to failure or success.
This is important for a life-critical workflow: absence of a transcript value,
for example, should create an evidence/document action rather than silently
make a candidate ineligible.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Mapping, Optional

from pydantic import Field

from .mcp_domain import ConditionOperator, EligibilityCriterion, MCPModel, ScholarshipProgram


class CriterionState(str, Enum):
    MET = "Met"
    UNMET = "Unmet"
    UNKNOWN = "Unknown"


class ScholarshipEligibilityState(str, Enum):
    ELIGIBLE_CANDIDATE = "EligibleCandidate"
    INELIGIBLE = "Ineligible"
    UNKNOWN = "Unknown"


class CriterionEvaluation(MCPModel):
    criterion_id: str = Field(alias="criterionId")
    label: str
    field: str
    state: CriterionState
    actual_value: Optional[Any] = Field(default=None, alias="actualValue")
    expected_value: Optional[Any] = Field(default=None, alias="expectedValue")
    reason: str
    source_assertion_ids: list[str] = Field(default_factory=list, alias="sourceAssertionIds")


class ScholarshipEvaluation(MCPModel):
    scholarship_id: str = Field(alias="scholarshipId")
    state: ScholarshipEligibilityState
    criteria: list[CriterionEvaluation] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list, alias="missingFields")
    unmet_criterion_ids: list[str] = Field(default_factory=list, alias="unmetCriterionIds")
    reason: str


def _resolve_path(facts: Mapping[str, Any], path: str) -> tuple[bool, Any]:
    current: Any = facts
    for part in path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return False, None
        current = current[part]
    return True, current


def _compare(actual: Any, operator: ConditionOperator, expected: Any) -> Optional[bool]:
    if operator == ConditionOperator.EXISTS:
        return actual is not None
    if operator == ConditionOperator.EQ:
        return actual == expected
    if operator == ConditionOperator.NE:
        return actual != expected
    if operator in {ConditionOperator.IN, ConditionOperator.NOT_IN}:
        if not isinstance(expected, (list, tuple, set, frozenset)):
            return None
        result = actual in expected
        return result if operator == ConditionOperator.IN else not result
    if actual is None or expected is None:
        return None
    try:
        if operator == ConditionOperator.GT:
            return actual > expected
        if operator == ConditionOperator.GTE:
            return actual >= expected
        if operator == ConditionOperator.LT:
            return actual < expected
        if operator == ConditionOperator.LTE:
            return actual <= expected
    except TypeError:
        return None
    return None


def evaluate_scholarship(
    scholarship: ScholarshipProgram,
    *,
    criteria_by_id: Mapping[str, EligibilityCriterion],
    facts: Mapping[str, Any],
) -> ScholarshipEvaluation:
    """Evaluate a scholarship against already-admissible normalized facts.

    ``facts`` should be built by an application service from authoritative or
    otherwise admissible assertions. This function deliberately does not choose
    which assertions are trustworthy; that remains the truth layer's job.
    """

    evaluations: list[CriterionEvaluation] = []
    missing_fields: set[str] = set()
    unmet_ids: list[str] = []

    for criterion_id in scholarship.criterion_ids:
        criterion = criteria_by_id.get(criterion_id)
        if criterion is None:
            evaluations.append(
                CriterionEvaluation(
                    criterionId=criterion_id,
                    label="Missing criterion definition",
                    field="",
                    state=CriterionState.UNKNOWN,
                    reason="Scholarship references a criterion that is not available to the evaluator.",
                )
            )
            missing_fields.add(f"criterion:{criterion_id}")
            continue

        exists, actual = _resolve_path(facts, criterion.subject_field)
        if not exists:
            state = CriterionState.UNKNOWN
            reason = "Required fact is not available from the admissible fact set."
            missing_fields.add(criterion.subject_field)
        else:
            result = _compare(actual, criterion.operator, criterion.expected_value)
            if result is None:
                state = CriterionState.UNKNOWN
                reason = "Criterion comparison cannot be evaluated safely for these value types."
                missing_fields.add(criterion.subject_field)
            elif result:
                state = CriterionState.MET
                reason = "Current admissible fact satisfies the criterion."
            else:
                state = CriterionState.UNMET
                reason = "Current admissible fact does not satisfy the criterion."
                if criterion.required:
                    unmet_ids.append(criterion.id)

        evaluations.append(
            CriterionEvaluation(
                criterionId=criterion.id,
                label=criterion.label,
                field=criterion.subject_field,
                state=state,
                actualValue=actual if exists else None,
                expectedValue=criterion.expected_value,
                reason=reason,
                sourceAssertionIds=criterion.source_assertion_ids,
            )
        )

    required_unknown = any(
        item.state == CriterionState.UNKNOWN
        and criteria_by_id.get(item.criterion_id, None) is not None
        and criteria_by_id[item.criterion_id].required
        for item in evaluations
    ) or any(item.criterion_id not in criteria_by_id for item in evaluations)

    if unmet_ids:
        state = ScholarshipEligibilityState.INELIGIBLE
        reason = "At least one required eligibility criterion is unmet."
    elif required_unknown:
        state = ScholarshipEligibilityState.UNKNOWN
        reason = "No required criterion is known to be unmet, but required facts/rules are still unknown."
    else:
        state = ScholarshipEligibilityState.ELIGIBLE_CANDIDATE
        reason = (
            "All represented required criteria are satisfied. This is a candidate eligibility "
            "result, not an award decision or guarantee."
        )

    return ScholarshipEvaluation(
        scholarshipId=scholarship.id,
        state=state,
        criteria=evaluations,
        missingFields=sorted(missing_fields),
        unmetCriterionIds=sorted(unmet_ids),
        reason=reason,
    )
