"""Phase 4 candidate retrieval service."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import pandas as pd

from .models import CandidateRestaurant, RetrievalResult
from .scoring import compute_composite_score


def _load_preferences(preference_payload_path: Path) -> dict:
    if not preference_payload_path.exists():
        raise FileNotFoundError(
            f"Preference payload not found: {preference_payload_path}. "
            "Run Phase 3 first."
        )
    return json.loads(preference_payload_path.read_text(encoding="utf-8"))


def _apply_strict_filters(df: pd.DataFrame, preferences: dict) -> pd.DataFrame:
    filtered = df.copy()
    location = preferences.get("location")
    cuisine = preferences.get("cuisine")
    minimum_rating = preferences.get("minimum_rating")

    if location:
        filtered = filtered[filtered["location"].str.lower() == location.lower()]
    if cuisine:
        filtered = filtered[filtered["cuisine"].str.lower().str.contains(cuisine.lower(), na=False)]
    if minimum_rating is not None:
        filtered = filtered[filtered["rating"] >= float(minimum_rating)]
    return filtered


def _apply_relaxed_filters(df: pd.DataFrame, preferences: dict) -> pd.DataFrame:
    # Phase 4 fallback: relax cuisine exactness first, keep rating and location where possible.
    filtered = df.copy()
    location = preferences.get("location")
    minimum_rating = preferences.get("minimum_rating")

    if location:
        filtered = filtered[filtered["location"].str.lower() == location.lower()]
    if minimum_rating is not None:
        relaxed_rating = max(0.0, float(minimum_rating) - 0.5)
        filtered = filtered[filtered["rating"] >= relaxed_rating]
    return filtered


def retrieve_top_candidates(
    processed_dataset_path: Path,
    preference_payload_path: Path,
    top_n: int = 15,
) -> RetrievalResult:
    if not processed_dataset_path.exists():
        raise FileNotFoundError(
            f"Processed dataset not found: {processed_dataset_path}. Run Phase 2 first."
        )

    df = pd.read_csv(processed_dataset_path)
    preferences = _load_preferences(preference_payload_path)
    total_records = len(df)

    strict = _apply_strict_filters(df, preferences)
    relaxation_applied = False
    filtered = strict

    if strict.empty:
        relaxation_applied = True
        filtered = _apply_relaxed_filters(df, preferences)

    if filtered.empty:
        return RetrievalResult(
            total_records=total_records,
            filtered_records=0,
            shortlisted_count=0,
            relaxation_applied=relaxation_applied,
            shortlisted_candidates=[],
        )

    candidates: List[CandidateRestaurant] = []
    for _, row in filtered.iterrows():
        score, budget_match, cuisine_match, location_match = compute_composite_score(
            rating=float(row["rating"]),
            cost=float(row["cost"]),
            location=str(row["location"]),
            cuisines=str(row["cuisine"]),
            preferred_location=preferences.get("location"),
            preferred_budget=preferences.get("budget"),
            preferred_cuisine=preferences.get("cuisine"),
        )
        candidates.append(
            CandidateRestaurant(
                name=str(row["name"]),
                location=str(row["location"]),
                cuisine=str(row["cuisine"]),
                cost=float(row["cost"]),
                rating=float(row["rating"]),
                score=score,
                budget_match=budget_match,
                cuisine_match=cuisine_match,
                location_match=location_match,
            )
        )

    # Deduplicate by restaurant name (keep best-scoring entry).
    best_by_name: dict[str, CandidateRestaurant] = {}
    for c in candidates:
        existing = best_by_name.get(c.name)
        if existing is None or (c.score, c.rating) > (existing.score, existing.rating):
            best_by_name[c.name] = c
    candidates = list(best_by_name.values())

    ranked = sorted(
        candidates,
        key=lambda c: (c.score, c.rating, c.cost, c.name.lower()),
        reverse=True,
    )
    shortlisted = ranked[:top_n]

    return RetrievalResult(
        total_records=total_records,
        filtered_records=len(filtered),
        shortlisted_count=len(shortlisted),
        relaxation_applied=relaxation_applied,
        shortlisted_candidates=shortlisted,
    )

