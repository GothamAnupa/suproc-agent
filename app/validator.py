from __future__ import annotations

from .data_loader import index_entities
from .models import BusinessRequirement, Entity, ValidationResult
from .tools import constraint_failures


def validate_recommendations(
    entities: list[Entity],
    requirement: BusinessRequirement,
    recommendations: list[dict],
    human_approval_required: bool,
    allow_shortage: bool = True,
) -> ValidationResult:
    indexed = index_entities(entities)
    failures: list[str] = []
    checks = [
        "dataset existence",
        "entity type",
        "hard constraints",
        "factual support",
        "duplicates",
        "requested result count",
        "score arithmetic",
        "human approval",
    ]
    seen: set[str] = set()
    for rec in recommendations:
        entity_id = rec["entity_id"]
        if entity_id in seen:
            failures.append(f"Duplicate recommendation: {entity_id}")
            continue
        seen.add(entity_id)
        entity = indexed.get(entity_id)
        if not entity:
            failures.append(f"Entity {entity_id} does not exist in dataset")
            continue
        failures.extend([f"{entity_id}: {failure}" for failure in constraint_failures(entity, requirement)])
        score = rec["score"]
        components = score["components"] if isinstance(score, dict) else score.components
        total = score["total"] if isinstance(score, dict) else score.total
        component_total = sum(item["points"] if isinstance(item, dict) else item.points for item in components.values())
        if total != component_total:
            failures.append(f"{entity_id}: score total does not equal component sum")
        for claim_key, claim_value in rec.get("claims", {}).items():
            if claim_key == "pricing" and entity.pricing is None:
                failures.append(f"{entity_id}: pricing claim is unsupported by dataset")
            if claim_key == "name" and claim_value != entity.name:
                failures.append(f"{entity_id}: name claim is unsupported by dataset")
    if len(recommendations) < requirement.requested_results and not allow_shortage:
        failures.append("Requested number of results was not returned")
    if not human_approval_required:
        failures.append("Proposed consequential action does not require human approval")
    return ValidationResult(is_valid=not failures, failures=failures, checks=checks)
