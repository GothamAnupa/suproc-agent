from __future__ import annotations

from .data_loader import index_entities
from .models import BusinessRequirement, Entity, ScoreBreakdown, ScoreComponent, ValidationResult


def search_entities(entities: list[Entity], requirement: BusinessRequirement) -> list[Entity]:
    keywords = [k.lower() for k in requirement.hard_constraints.get("product_keywords", [])]
    locations = set(requirement.hard_constraints.get("locations", []))
    results: list[Entity] = []
    for entity in entities:
        if entity.entity_type != requirement.entity_type:
            continue
        searchable = " ".join(entity.categories + entity.products + entity.skills).lower()
        keyword_match = not keywords or any(keyword in searchable for keyword in keywords)
        location_match = not locations or bool(locations.intersection(entity.locations))
        if keyword_match and location_match:
            results.append(entity)
    return results


def get_entity_details(entities: list[Entity], entity_id: str) -> Entity:
    indexed = index_entities(entities)
    if entity_id not in indexed:
        raise KeyError(f"Entity {entity_id} not found in dataset")
    return indexed[entity_id]


def _fails_constraints(entity: Entity, requirement: BusinessRequirement) -> list[str]:
    failures: list[str] = []
    constraints = requirement.hard_constraints
    if entity.entity_type != requirement.entity_type:
        failures.append("wrong entity type")
    if entity.availability != "available":
        failures.append("entity is unavailable")
    locations = set(constraints.get("locations", []))
    if locations and not locations.intersection(entity.locations):
        failures.append("location constraint not satisfied")
    for cert in constraints.get("certifications", []):
        if cert not in entity.certifications:
            failures.append(f"missing certification: {cert}")
    minimum_capacity = constraints.get("minimum_capacity")
    if minimum_capacity is not None and (entity.capacity_units is None or entity.capacity_units < minimum_capacity):
        failures.append("capacity constraint not satisfied")
    maximum_delivery = constraints.get("maximum_delivery_days")
    if maximum_delivery is not None and (entity.delivery_days is None or entity.delivery_days > maximum_delivery):
        failures.append("delivery constraint not satisfied")
    for keyword in constraints.get("product_keywords", []):
        searchable = " ".join(entity.categories + entity.products).lower()
        if keyword.lower() not in searchable:
            failures.append(f"missing product keyword: {keyword}")
    return failures


def filter_by_constraints(entities: list[Entity], requirement: BusinessRequirement) -> list[Entity]:
    return [entity for entity in entities if not _fails_constraints(entity, requirement)]


def calculate_match_score(entity: Entity, requirement: BusinessRequirement) -> ScoreBreakdown:
    constraints = requirement.hard_constraints
    searchable = " ".join(entity.categories + entity.products + entity.skills).lower()
    product_keywords = [k.lower() for k in constraints.get("product_keywords", [])]
    product_points = 30 if product_keywords and all(k in searchable for k in product_keywords) else 15 if product_keywords and any(k in searchable for k in product_keywords) else 20
    location_points = 20 if set(constraints.get("locations", [])).intersection(entity.locations) else 10 if not constraints.get("locations") else 0
    failures = _fails_constraints(entity, requirement)
    hard_points = 25 if not failures else 0
    capacity_ok = constraints.get("minimum_capacity") is None or (entity.capacity_units or 0) >= constraints.get("minimum_capacity")
    delivery_ok = constraints.get("maximum_delivery_days") is None or (entity.delivery_days or 9999) <= constraints.get("maximum_delivery_days")
    availability_points = 15 if entity.availability == "available" and capacity_ok and delivery_ok else 0
    reputation_points = min(10, int((entity.rating or 0) * 2))
    if entity.completed_projects and entity.completed_projects >= 20 and reputation_points < 10:
        reputation_points += 1
    reputation_points = min(10, reputation_points)
    components = {
        "product_or_skill_relevance": ScoreComponent(points=product_points, max_points=30, evidence=[f"Products/categories: {', '.join(entity.products + entity.categories)}"]),
        "location_suitability": ScoreComponent(points=location_points, max_points=20, evidence=[f"Locations: {', '.join(entity.locations)}"]),
        "hard_constraint_compliance": ScoreComponent(points=hard_points, max_points=25, evidence=["All hard constraints satisfied, including " + ", ".join(entity.certifications)] if not failures else failures),
        "availability_capacity_delivery": ScoreComponent(points=availability_points, max_points=15, evidence=[f"Availability {entity.availability}, capacity {entity.capacity_units}, delivery {entity.delivery_days} days"]),
        "reputation_previous_performance": ScoreComponent(points=reputation_points, max_points=10, evidence=[f"Rating {entity.rating}, completed projects {entity.completed_projects}"]),
    }
    return ScoreBreakdown(components=components, total=sum(component.points for component in components.values()))


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
        constraint_failures = _fails_constraints(entity, requirement)
        failures.extend([f"{entity_id}: {failure}" for failure in constraint_failures])
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


def draft_outreach(requirement: BusinessRequirement, recommendations: list) -> str:
    ids = ", ".join(rec.entity_id for rec in recommendations) or "the matching suppliers"
    return (
        f"Subject: Procurement enquiry for {requirement.objective}\n\n"
        f"Hello, we are evaluating suppliers for {requirement.objective}. "
        f"Please confirm certifications, available capacity, delivery timeline, pricing, and sample availability. "
        f"This draft is prepared for {ids} and has not been sent."
    )
