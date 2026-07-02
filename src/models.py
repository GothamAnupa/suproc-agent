from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


EntityType = Literal["supplier", "business", "professional", "opportunity", "project", "bounty", "procurement"]


class Entity(BaseModel):
    id: str
    name: str
    entity_type: EntityType
    categories: list[str] = Field(default_factory=list)
    products: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    capacity_units: int | None = None
    delivery_days: int | None = None
    availability: str = "available"
    rating: float | None = None
    completed_projects: int | None = None
    previous_interactions: list[str] = Field(default_factory=list)
    notes: str | None = None
    risks: list[str] = Field(default_factory=list)
    pricing: str | None = None
    deadline_days: int | None = None


class BusinessRequirement(BaseModel):
    objective: str
    entity_type: EntityType
    hard_constraints: dict[str, Any] = Field(default_factory=dict)
    preferences: dict[str, Any] = Field(default_factory=dict)
    requested_results: int = 3
    conflicts: list[str] = Field(default_factory=list)
    safety_flags: list[str] = Field(default_factory=list)


class ScoreComponent(BaseModel):
    points: int
    max_points: int
    evidence: list[str] = Field(default_factory=list)


class ScoreBreakdown(BaseModel):
    components: dict[str, ScoreComponent]
    total: int


class Recommendation(BaseModel):
    entity_id: str
    name: str
    entity_type: EntityType
    score: ScoreBreakdown
    evidence: list[str]
    missing_information: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)


class ValidationResult(BaseModel):
    is_valid: bool
    failures: list[str] = Field(default_factory=list)
    checks: list[str] = Field(default_factory=list)


class AgentResponse(BaseModel):
    interpreted_requirement: BusinessRequirement
    hard_constraints: dict[str, Any]
    optional_preferences: dict[str, Any]
    plan_followed: list[str]
    recommended_matches: list[Recommendation]
    constraints_checked: list[str]
    missing_information: list[str]
    risks_or_uncertainties: list[str]
    recommended_next_action: str
    draft_outreach_message: str
    validation: ValidationResult
    human_approval_required: bool
    status: str
    correction_attempts: int = 0
