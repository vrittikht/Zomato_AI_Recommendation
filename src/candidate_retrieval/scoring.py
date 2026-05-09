"""Scoring utilities for deterministic candidate ranking."""

from __future__ import annotations

from typing import Tuple


def budget_range_for_tier(tier: str | None) -> Tuple[float, float]:
    if tier == "low":
        return (0, 500)
    if tier == "medium":
        return (501, 1200)
    if tier == "high":
        return (1201, 100000)
    return (0, 100000)


def cost_fit_score(cost: float, budget_pref: str | int | None) -> Tuple[float, bool]:
    if isinstance(budget_pref, int):
        # Numeric max budget
        if cost <= budget_pref:
            return (1.0, True)
        
        # Penalize softly when cost exceeds max budget
        distance = cost - budget_pref
        penalty = min(distance / 500.0, 1.0) # Penalty gradient over 500 units
        return (max(0.0, 1.0 - penalty), False)

    # String tiers (low, medium, high)
    min_cost, max_cost = budget_range_for_tier(budget_pref)
    if min_cost <= cost <= max_cost:
        return (1.0, True)

    if cost < min_cost:
        distance = min_cost - cost
    else:
        distance = cost - max_cost

    penalty = min(distance / 1000.0, 1.0)
    return (max(0.0, 1.0 - penalty), False)


def cuisine_match_score(restaurant_cuisines: str, preferred_cuisine: str | None) -> Tuple[float, bool]:
    if not preferred_cuisine:
        return (0.5, False)

    normalized_pref = preferred_cuisine.lower()
    normalized_cuisine = restaurant_cuisines.lower()
    matched = normalized_pref in normalized_cuisine
    return (1.0 if matched else 0.0, matched)


def location_match_score(location: str, preferred_location: str | None) -> Tuple[float, bool]:
    if not preferred_location:
        return (0.5, False)
    matched = location.lower() == preferred_location.lower()
    return (1.0 if matched else 0.0, matched)


def compute_composite_score(
    rating: float,
    cost: float,
    location: str,
    cuisines: str,
    preferred_location: str | None,
    preferred_budget: str | None,
    preferred_cuisine: str | None,
) -> Tuple[float, bool, bool, bool]:
    # Weights prioritize user intent while keeping rating meaningful.
    rating_norm = max(0.0, min(rating / 5.0, 1.0))
    location_score, location_match = location_match_score(location, preferred_location)
    cuisine_score, cuisine_match = cuisine_match_score(cuisines, preferred_cuisine)
    budget_score, budget_match = cost_fit_score(cost, preferred_budget)

    score = (
        0.40 * rating_norm
        + 0.25 * location_score
        + 0.20 * cuisine_score
        + 0.15 * budget_score
    )
    return (round(score, 4), budget_match, cuisine_match, location_match)

