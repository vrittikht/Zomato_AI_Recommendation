"""API models for recommendation service."""

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field

class RecommendationRequest(BaseModel):
    location: str = Field(..., description="The city or area to search in.")
    budget: Optional[str | int] = Field(None, description="Budget preference (numeric or low/medium/high).")
    cuisine: Optional[str] = Field(None, description="Preferred cuisine.")
    rating: float = Field(0.0, ge=0, le=5, description="Minimum rating (0-5).")
    additional_preferences: Optional[str] = Field(None, description="Any other preferences.")
    top_k: int = Field(5, ge=1, le=10, description="Number of recommendations to return.")

class RecommendationItem(BaseModel):
    name: str
    location: str
    cuisine: str
    rating: float
    cost: float
    explanation: str

class RecommendationResponse(BaseModel):
    recommendations: List[RecommendationItem]
    summary: Optional[str]
    used_fallback: bool
