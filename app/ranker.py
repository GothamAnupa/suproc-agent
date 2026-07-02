from __future__ import annotations

from .models import BusinessRequirement, Entity, ScoreBreakdown, ScoreComponent
from .tools import constraint_failures


def calculate_match_score(entity: Entity, requirement: BusinessRequirement) -> ScoreBreakdown:
    constraints = requirement.hard_constraints
    searchable = " ".join(entity.categories + entity.products + entity.skills).lower()
    product_keywords = [k.lower() for k in constraints.get("product_keywords", [])]
    product_points = 30 if product_keywords and all(k in searchable for k in product_keywords) else 15 if product_keywords and any(k in searchable for k in product_keywords) else 20
    location_points = 20 if set(constraints.get("locations", [])).intersection(entity.locations) else 10 if not constraints.get("locations") else 0
    failures = constraint_failures(entity, requirement)
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


def rank_entities(entities: list[Entity], requirement: BusinessRequirement) -> list[Entity]:
    return sorted(entities, key=lambda item: calculate_match_score(item, requirement).total, reverse=True)
