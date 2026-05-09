"""Models for Phase 5 recommendation layer."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass
class RecommendationItem:
    name: str
    location: str
    cuisine: str
    rating: float
    cost: float
    explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RecommendationResponse:
    recommendations: List[RecommendationItem]
    summary: Optional[str]
    used_fallback: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "recommendations": [r.to_dict() for r in self.recommendations],
            "summary": self.summary,
            "used_fallback": self.used_fallback,
        }

