from __future__ import annotations

import re

from .models import BusinessRequirement, EntityType


SOUTH_INDIA = ["Karnataka", "Tamil Nadu", "Kerala", "Andhra Pradesh", "Telangana"]
NORTH_INDIA = ["Delhi", "Punjab", "Haryana", "Uttar Pradesh", "Rajasthan"]


def _entity_type(text: str) -> EntityType:
    if "professional" in text or "consultant" in text or "expert" in text:
        return "professional"
    if "opportunit" in text:
        return "opportunity"
    if "bount" in text:
        return "bounty"
    if "project" in text:
        return "project"
    return "supplier"


def _number_before(words: str, text: str) -> int | None:
    pattern = rf"(\d[\d,]*)\s*(?:{words})"
    match = re.search(pattern, text)
    if not match:
        return None
    return int(match.group(1).replace(",", ""))


def parse_requirement(request: str) -> BusinessRequirement:
    text = request.lower()
    constraints: dict[str, object] = {}
    preferences: dict[str, object] = {}
    conflicts: list[str] = []
    safety_flags: list[str] = []

    entity_type = _entity_type(text)
    requested = _number_before("suppliers|professionals|opportunities|projects|bounties|results|matches", text) or 3
    capacity = _number_before("units|unit", text)
    delivery = _number_before("days|day", text)

    if "ignore validation" in text or "ignore validation rules" in text:
        safety_flags.append("User asked to ignore validation rules; deterministic validation remains enforced.")

    locations: list[str] = []
    if "south india" in text or "southern india" in text:
        locations.extend(SOUTH_INDIA)
    if "north india" in text:
        locations.extend(NORTH_INDIA)
    explicit_locations = {
        "bengaluru": "Karnataka",
        "bangalore": "Karnataka",
        "karnataka": "Karnataka",
        "tamil nadu": "Tamil Nadu",
        "kerala": "Kerala",
        "andhra": "Andhra Pradesh",
        "telangana": "Telangana",
        "delhi": "Delhi",
    }
    for needle, location in explicit_locations.items():
        if needle in text:
            locations.append(location)
    if locations:
        constraints["locations"] = sorted(set(locations), key=locations.index)
    if any(loc in locations for loc in SOUTH_INDIA) and any(loc in locations for loc in NORTH_INDIA) and "only" in text:
        conflicts.append("Conflicting location requirement: request includes both South India and North India only.")

    certifications: list[str] = []
    if "food-grade" in text or "food grade" in text:
        certifications.append("food-grade")
    if "aerospace-grade" in text or "aerospace grade" in text:
        certifications.append("aerospace-grade")
    if certifications:
        constraints["certifications"] = certifications
    if capacity:
        constraints["minimum_capacity"] = capacity
    if delivery:
        constraints["maximum_delivery_days"] = delivery
    if "biodegradable" in text:
        constraints["product_keywords"] = ["biodegradable", "container"]
        preferences["sustainable_materials"] = True
    if "startup" in text:
        preferences["startup_friendly"] = True

    objective = "Find matching " + entity_type + " records"
    if "biodegradable" in text:
        objective = "Find biodegradable food-container suppliers"

    return BusinessRequirement(
        objective=objective,
        entity_type=entity_type,
        hard_constraints=constraints,
        preferences=preferences,
        requested_results=requested,
        conflicts=conflicts,
        safety_flags=safety_flags,
    )
