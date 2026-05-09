"""Data models for Phase 3 preference capture."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List


@dataclass
class RawUserPreferenceInput:
    location: str | None = None
    budget: str | None = None
    cuisine: str | None = None
    minimum_rating: float | int | str | None = None
    additional_preferences: str | None = None


@dataclass
class NormalizedUserPreferencePayload:
    location: str | None
    budget: str | int | None
    cuisine: str | None
    minimum_rating: float | None
    additional_preferences: List[str]
    inferred_tags: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

