from __future__ import annotations

from .data_loader import load_dataset
from .models import AgentResponse, Recommendation
from .parser import parse_requirement
from .tools import (
    calculate_match_score,
    draft_outreach,
    filter_by_constraints,
    search_entities,
    validate_recommendations,
)


PLAN = [
    "Search suppliers by product category and location",
    "Inspect supplier capabilities and certifications",
    "Filter records that fail hard requirements",
    "Rank the remaining suppliers",
    "Validate every recommendation",
    "Prepare the final response and outreach message",
]


def _recommend(entity, requirement) -> Recommendation:
    score = calculate_match_score(entity, requirement)
    missing = []
    if entity.pricing is None:
        missing.append(f"{entity.id}: pricing is not available in the dataset")
    return Recommendation(
        entity_id=entity.id,
        name=entity.name,
        entity_type=entity.entity_type,
        score=score,
        evidence=[
            f"Locations: {', '.join(entity.locations)}",
            f"Certifications: {', '.join(entity.certifications)}",
            f"Capacity: {entity.capacity_units} units",
            f"Delivery: {entity.delivery_days} days",
            f"Rating: {entity.rating}",
        ],
        missing_information=missing,
        risks=entity.risks,
    )


def _validation_payload(recommendations: list[Recommendation]) -> list[dict]:
    return [
        {"entity_id": rec.entity_id, "score": rec.score.model_dump(), "claims": {"name": rec.name}}
        for rec in recommendations
    ]


def run_agent(request: str, inject_invalid_first: bool = False) -> AgentResponse:
    entities = load_dataset()
    requirement = parse_requirement(request)
    candidates = search_entities(entities, requirement)
    valid_entities = filter_by_constraints(candidates, requirement)
    ranked = sorted(valid_entities, key=lambda item: calculate_match_score(item, requirement).total, reverse=True)
    recommendations = [_recommend(entity, requirement) for entity in ranked[: requirement.requested_results]]

    correction_attempts = 0
    if inject_invalid_first:
        invalid = next((entity for entity in entities if entity.id == "SUP-014"), None)
        if invalid:
            recommendations = [_recommend(invalid, requirement)] + recommendations[: max(0, requirement.requested_results - 1)]

    while correction_attempts < 3:
        validation = validate_recommendations(
            entities,
            requirement,
            _validation_payload(recommendations),
            human_approval_required=True,
            allow_shortage=True,
        )
        if validation.is_valid:
            break
        correction_attempts += 1
        bad_ids = {failure.split(":", 1)[0] for failure in validation.failures if ":" in failure}
        recommendations = [rec for rec in recommendations if rec.entity_id not in bad_ids]
        existing_ids = {rec.entity_id for rec in recommendations}
        for entity in ranked:
            if len(recommendations) >= requirement.requested_results:
                break
            if entity.id not in existing_ids:
                recommendations.append(_recommend(entity, requirement))
                existing_ids.add(entity.id)
    else:
        validation = validate_recommendations(entities, requirement, _validation_payload(recommendations), True)

    missing = [item for rec in recommendations for item in rec.missing_information]
    risks = [item for rec in recommendations for item in rec.risks]
    if not recommendations:
        risks.insert(0, "No valid matches satisfy all hard constraints; no records were invented.")
    if requirement.conflicts:
        risks.extend(requirement.conflicts)
    if requirement.safety_flags:
        risks.extend(requirement.safety_flags)

    next_action = "No outreach recommended because no valid matches are available."
    if recommendations:
        ids = ", ".join(rec.entity_id for rec in recommendations)
        next_action = f"Send a procurement enquiry to {ids}."

    return AgentResponse(
        interpreted_requirement=requirement,
        hard_constraints=requirement.hard_constraints,
        optional_preferences=requirement.preferences,
        plan_followed=PLAN,
        recommended_matches=recommendations,
        constraints_checked=validation.checks,
        missing_information=missing or ["No missing information identified for recommended records."],
        risks_or_uncertainties=risks or ["Final supplier choice still requires human commercial review."],
        recommended_next_action=next_action,
        draft_outreach_message=draft_outreach(requirement, recommendations),
        validation=validation,
        human_approval_required=True,
        status="Awaiting user approval",
        correction_attempts=correction_attempts,
    )
