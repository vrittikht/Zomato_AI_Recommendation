"""Deterministic fallback recommendation generation."""

from __future__ import annotations

from typing import Any, Dict, List

from .models import RecommendationItem


def _build_explanation(candidate: Dict[str, Any], prefs: Dict[str, Any]) -> str:
    parts: List[str] = []

    if prefs.get("location") and candidate.get("location"):
        if str(candidate["location"]).lower() == str(prefs["location"]).lower():
            parts.append(f"Matches your location preference ({prefs['location']}).")

    if prefs.get("cuisine") and candidate.get("cuisine"):
        if str(prefs["cuisine"]).lower() in str(candidate["cuisine"]).lower():
            parts.append(f"Includes your preferred cuisine ({prefs['cuisine']}).")

    if prefs.get("minimum_rating") is not None and candidate.get("rating") is not None:
        parts.append(
            f"Rated {candidate['rating']:.1f}, meeting your minimum rating of {float(prefs['minimum_rating']):.1f}."
        )
    elif candidate.get("rating") is not None:
        parts.append(f"Rated {candidate['rating']:.1f}.")

    if prefs.get("budget") and candidate.get("cost") is not None:
        parts.append(f"Approx. cost for two is {int(float(candidate['cost']))}.")

    tags = prefs.get("inferred_tags") or []
    if "family_friendly" in tags:
        parts.append("Likely suitable for family dining based on your preference.")
    if "quick_service" in tags:
        parts.append("Aligned with your quick service preference.")

    if not parts:
        parts.append("A good overall match based on rating and preference fit.")

    # Keep explanation concise (1-2 sentences).
    text = " ".join(parts)
    # Split on ". " (dot + space) to avoid breaking decimals like "4.6".
    sentences = [s.strip() for s in text.split(". ") if s.strip()]
    trimmed = sentences[:2]
    joined = ". ".join(trimmed)
    if not joined.endswith("."):
        joined += "."
    return joined


def fallback_recommendations(
    shortlisted_candidates: List[Dict[str, Any]],
    user_preferences: Dict[str, Any],
    top_k: int,
) -> List[RecommendationItem]:
    # Assumes candidates already contain a deterministic score from Phase 4.
    ranked = sorted(
        shortlisted_candidates,
        key=lambda c: (
            float(c.get("score", 0.0)),
            float(c.get("rating", 0.0)),
        ),
        reverse=True,
    )
    picked = ranked[:top_k]

    results: List[RecommendationItem] = []
    for c in picked:
        results.append(
            RecommendationItem(
                name=str(c["name"]),
                location=str(c["location"]),
                cuisine=str(c["cuisine"]),
                rating=float(c["rating"]),
                cost=float(c["cost"]),
                explanation=_build_explanation(c, user_preferences),
            )
        )
    return results

