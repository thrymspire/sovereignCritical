"""Deterministic boundary-contract evaluation for Master Critical Path.

This module evaluates already-defined contracts against admissible assertions.
It does not contain institutional policy and it does not mutate authoritative
state. The evaluator returns proposed effects with an audit trail; application
services decide whether to materialize deterministic low-risk effects or route
high-impact effects to review.

That distinction is intentional. A verified grade may *trigger* funding and
scholarship reevaluation without the engine inventing an award or eligibility
outcome that no explicit rule supports.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping, Optional

from pydantic import Field

from .mcp_domain import (
    Assertion,
    BoundaryAction,
    BoundaryContract,
    ConditionOperator,
    ImpactLevel,
    MCPModel,
    VerificationState,
)


class ConditionResult(str, Enum):
    MET = "Met"
    UNMET = "Unmet"
    UNKNOWN = "Unknown"


class ContractEvaluationState(str, Enum):
    NOT_TRIGGERED = "NotTriggered"
    CONDITIONS_UNMET = "ConditionsUnmet"
    CONDITIONS_UNKNOWN = "ConditionsUnknown"
    EFFECTS_PROPOSED = "EffectsProposed"
    REVIEW_REQUIRED = "ReviewRequired"


class ConditionEvaluation(MCPModel):
    predicate: str
    subject_id: Optional[str] = Field(default=None, alias="subjectId")
    result: ConditionResult
    assertion_id: Optional[str] = Field(default=None, alias="assertionId")
    actual_value: Optional[Any] = Field(default=None, alias="actualValue")
    expected_value: Optional[Any] = Field(default=None, alias="expectedValue")
    reason: str


class ProposedBoundaryEffect(MCPModel):
    action: BoundaryAction
    target_entity_id: Optional[str] = Field(default=None, alias="targetEntityId")
    target_predicate: Optional[str] = Field(default=None, alias="targetPredicate")
    value: Optional[Any] = None
    description: str
    source_contract_id: str = Field(alias="sourceContractId")
    source_assertion_ids: list[str] = Field(default_factory=list, alias="sourceAssertionIds")
    requires_human_review: bool = Field(default=False, alias="requiresHumanReview")


class BoundaryEvaluation(MCPModel):
    contract_id: str = Field(alias="contractId")
    state: ContractEvaluationState
    trigger_assertion_ids: list[str] = Field(default_factory=list, alias="triggerAssertionIds")
    condition_evaluations: list[ConditionEvaluation] = Field(
        default_factory=list,
        alias="conditionEvaluations",
    )
    effects: list[ProposedBoundaryEffect] = Field(default_factory=list)
    reason: str


DEFAULT_ADMISSIBLE_STATES = frozenset(
    {
        VerificationState.CORROBORATED,
        VerificationState.INSTITUTIONALLY_VERIFIED,
        VerificationState.DERIVED,
    }
)


def _assertion_index(assertions: Iterable[Assertion]) -> dict[tuple[str, str], list[Assertion]]:
    result: dict[tuple[str, str], list[Assertion]] = {}
    for assertion in assertions:
        result.setdefault((assertion.subject_id, assertion.predicate), []).append(assertion)
    return result


def _latest_admissible(
    assertions: Iterable[Assertion],
    admissible_states: frozenset[VerificationState],
) -> Optional[Assertion]:
    candidates = [
        item
        for item in assertions
        if item.verification_state in admissible_states
        and item.verification_state
        not in {
            VerificationState.CONTRADICTED,
            VerificationState.SUPERSEDED,
            VerificationState.EXPIRED,
        }
    ]
    if not candidates:
        return None

    # Prefer the assertion with the latest effective timestamp when available.
    # Stable ID provides deterministic tie-breaking without pretending insertion
    # order is a truth property.
    return max(
        candidates,
        key=lambda item: (
            item.effective_from.isoformat() if item.effective_from else "",
            item.id,
        ),
    )


def _compare(actual: Any, operator: ConditionOperator, expected: Any) -> Optional[bool]:
    """Compare values. Return None when the comparison is not safely evaluable."""

    if operator == ConditionOperator.EXISTS:
        return actual is not None

    if operator == ConditionOperator.EQ:
        return actual == expected
    if operator == ConditionOperator.NE:
        return actual != expected

    if operator in {ConditionOperator.IN, ConditionOperator.NOT_IN}:
        if not isinstance(expected, (list, tuple, set, frozenset)):
            return None
        member = actual in expected
        return member if operator == ConditionOperator.IN else not member

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


def evaluate_boundary_contract(
    contract: BoundaryContract,
    *,
    assertions: Iterable[Assertion],
    changed_assertion_ids: Iterable[str],
    admissible_states: frozenset[VerificationState] = DEFAULT_ADMISSIBLE_STATES,
) -> BoundaryEvaluation:
    """Evaluate one contract after a set of assertion changes.

    A contract triggers only if at least one changed admissible assertion has a
    predicate named in ``triggerPredicates``. A provisional changed assertion
    cannot trigger authoritative propagation.
    """

    assertion_list = list(assertions)
    changed_ids = set(changed_assertion_ids)
    admissible_changed = [
        item
        for item in assertion_list
        if item.id in changed_ids
        and item.verification_state in admissible_states
        and item.predicate in contract.trigger_predicates
    ]

    if not contract.enabled:
        return BoundaryEvaluation(
            contractId=contract.id,
            state=ContractEvaluationState.NOT_TRIGGERED,
            reason="Contract is disabled.",
        )

    if not admissible_changed:
        return BoundaryEvaluation(
            contractId=contract.id,
            state=ContractEvaluationState.NOT_TRIGGERED,
            reason=(
                "No changed admissible assertion matched the contract trigger predicates. "
                "Provisional/unknown claims do not propagate."
            ),
        )

    index = _assertion_index(assertion_list)
    condition_results: list[ConditionEvaluation] = []

    for condition in contract.conditions:
        # An explicit subject id is required for deterministic lookup. Contracts
        # that need variable binding should be compiled into subject-specific
        # contracts by an application/domain service rather than guessed here.
        if not condition.subject_id:
            condition_results.append(
                ConditionEvaluation(
                    predicate=condition.predicate,
                    result=ConditionResult.UNKNOWN,
                    expectedValue=condition.expected_value,
                    reason="Condition has no subjectId; deterministic binding is unavailable.",
                )
            )
            continue

        candidates = index.get((condition.subject_id, condition.predicate), [])
        chosen = _latest_admissible(candidates, admissible_states)
        if chosen is None:
            condition_results.append(
                ConditionEvaluation(
                    predicate=condition.predicate,
                    subjectId=condition.subject_id,
                    result=ConditionResult.UNKNOWN,
                    expectedValue=condition.expected_value,
                    reason="No admissible assertion supplies this condition value.",
                )
            )
            continue

        comparison = _compare(chosen.object_value, condition.operator, condition.expected_value)
        if comparison is None:
            result = ConditionResult.UNKNOWN
            reason = "Condition comparison could not be evaluated safely."
        elif comparison:
            result = ConditionResult.MET
            reason = "Condition is satisfied by an admissible assertion."
        else:
            result = ConditionResult.UNMET
            reason = "Condition is not satisfied by the current admissible assertion."

        condition_results.append(
            ConditionEvaluation(
                predicate=condition.predicate,
                subjectId=condition.subject_id,
                result=result,
                assertionId=chosen.id,
                actualValue=chosen.object_value,
                expectedValue=condition.expected_value,
                reason=reason,
            )
        )

    if any(item.result == ConditionResult.UNMET for item in condition_results):
        return BoundaryEvaluation(
            contractId=contract.id,
            state=ContractEvaluationState.CONDITIONS_UNMET,
            triggerAssertionIds=[item.id for item in admissible_changed],
            conditionEvaluations=condition_results,
            reason="At least one explicit contract condition is unmet.",
        )

    if any(item.result == ConditionResult.UNKNOWN for item in condition_results):
        return BoundaryEvaluation(
            contractId=contract.id,
            state=ContractEvaluationState.CONDITIONS_UNKNOWN,
            triggerAssertionIds=[item.id for item in admissible_changed],
            conditionEvaluations=condition_results,
            reason=(
                "At least one contract condition is unknown. No effects are proposed "
                "because missing evidence is not equivalent to a false or true condition."
            ),
        )

    high_impact = contract.impact_level in {ImpactLevel.HIGH, ImpactLevel.CRITICAL}
    requires_review = contract.human_review_required or not contract.deterministic or high_impact
    source_ids = sorted(
        {
            item.id for item in admissible_changed
        }
        | {
            item.assertion_id
            for item in condition_results
            if item.assertion_id is not None
        }
    )

    effects = [
        ProposedBoundaryEffect(
            action=effect.action,
            targetEntityId=effect.target_entity_id,
            targetPredicate=effect.target_predicate,
            value=effect.value,
            description=effect.description,
            sourceContractId=contract.id,
            sourceAssertionIds=source_ids,
            requiresHumanReview=requires_review,
        )
        for effect in contract.effects
    ]

    return BoundaryEvaluation(
        contractId=contract.id,
        state=(
            ContractEvaluationState.REVIEW_REQUIRED
            if requires_review
            else ContractEvaluationState.EFFECTS_PROPOSED
        ),
        triggerAssertionIds=[item.id for item in admissible_changed],
        conditionEvaluations=condition_results,
        effects=effects,
        reason=(
            "Contract conditions are satisfied; effects require review before materialization."
            if requires_review
            else "Contract conditions are satisfied; deterministic effects are proposed."
        ),
    )


def evaluate_changed_assertions(
    contracts: Iterable[BoundaryContract],
    *,
    assertions: Iterable[Assertion],
    changed_assertion_ids: Iterable[str],
    admissible_states: frozenset[VerificationState] = DEFAULT_ADMISSIBLE_STATES,
) -> list[BoundaryEvaluation]:
    """Evaluate all contracts against the same immutable assertion snapshot."""

    assertion_list = list(assertions)
    changed_ids = list(changed_assertion_ids)
    return [
        evaluate_boundary_contract(
            contract,
            assertions=assertion_list,
            changed_assertion_ids=changed_ids,
            admissible_states=admissible_states,
        )
        for contract in contracts
    ]
