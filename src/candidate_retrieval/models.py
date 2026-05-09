"""Data models for Phase 4 candidate retrieval."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass
class CandidateRestaurant:
    name: str
    location: str
    cuisine: str
    cost: float
    rating: float
    score: float
    budget_match: bool
    cuisine_match: bool
    location_match: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RetrievalResult:
    total_records: int
    filtered_records: int
    shortlisted_count: int
    relaxation_applied: bool
    shortlisted_candidates: List[CandidateRestaurant]

