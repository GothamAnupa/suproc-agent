from __future__ import annotations

from .models import BusinessRequirement


def create_plan(requirement: BusinessRequirement) -> list[str]:
    return [
        "Extract constraints",
        "Search dataset",
        "Inspect matching records",
        "Filter invalid records",
        "Rank valid records",
        "Validate recommendations",
        "Correct failed recommendations if needed",
        "Generate final response",
        "Wait for human approval",
    ]
