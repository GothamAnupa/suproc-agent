from __future__ import annotations

from .data_loader import index_entities
from .models import BusinessRequirement, Entity


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


def constraint_failures(entity: Entity, requirement: BusinessRequirement) -> list[str]:
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
    return [entity for entity in entities if not constraint_failures(entity, requirement)]


def check_availability(entity: Entity) -> bool:
    return entity.availability == "available"
