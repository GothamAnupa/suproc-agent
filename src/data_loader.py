from __future__ import annotations

import json
from pathlib import Path

from .models import Entity


DEFAULT_DATASET = Path(__file__).resolve().parents[1] / "data" / "suproc_dataset.json"


def load_dataset(path: Path | None = None) -> list[Entity]:
    dataset_path = path or DEFAULT_DATASET
    with dataset_path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    return [Entity.model_validate(item) for item in raw["entities"]]


def index_entities(entities: list[Entity]) -> dict[str, Entity]:
    return {entity.id: entity for entity in entities}
