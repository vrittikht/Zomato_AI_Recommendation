"""Normalization helpers for user preference capture."""

from __future__ import annotations

import difflib
import re
from typing import Iterable, List, Set


BUDGET_NORMALIZATION_MAP = {
    "low": "low",
    "cheap": "low",
    "budget": "low",
    "economical": "low",
    "medium": "medium",
    "mid": "medium",
    "moderate": "medium",
    "high": "high",
    "premium": "high",
    "expensive": "high",
    "luxury": "high",
}

TAG_KEYWORDS = {
    "family_friendly": ["family", "kids", "child", "children"],
    "quick_service": ["quick", "fast", "speed", "urgent"],
    "romantic": ["date", "romantic", "couple", "anniversary"],
    "vegetarian_friendly": ["veg", "vegetarian", "vegan", "plant-based"],
    "delivery_friendly": ["delivery", "online order", "home delivery", "takeaway"],
}


def normalize_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    text = re.sub(r"\s+", " ", text)
    return text


def normalize_cuisine(value: object) -> str | None:
    text = normalize_text(value)
    if text is None:
        return None
    return text.title()


def normalize_budget(value: object) -> str | None:
    text = normalize_text(value)
    if text is None:
        return None

    token = text.lower()
    if token in BUDGET_NORMALIZATION_MAP:
        return BUDGET_NORMALIZATION_MAP[token]

    # Allow numeric budgets like "2000" (approx cost for two).
    digits = re.sub(r"[^0-9]", "", token)
    if not digits:
        return None

    amount = int(digits)
    return amount


def normalize_rating(value: object) -> float | None:
    text = normalize_text(value)
    if text is None:
        return None

    match = re.search(r"\d+(\.\d+)?", text)
    if not match:
        return None

    numeric = float(match.group())
    if numeric < 0 or numeric > 5:
        return None
    return round(numeric, 1)


def normalize_location(value: object, allowed_locations: Iterable[str]) -> str | None:
    text = normalize_text(value)
    if text is None:
        return None

    allowed_set: Set[str] = {entry.strip().title() for entry in allowed_locations if entry}
    requested = text.title()
    if requested in allowed_set:
        return requested

    close = difflib.get_close_matches(requested, list(allowed_set), n=1, cutoff=0.8)
    if close:
        return close[0]
    return None


def extract_additional_preferences(value: object) -> List[str]:
    text = normalize_text(value)
    if text is None:
        return []
    parts = re.split(r"[,\n;/]+", text)
    return [part.strip().lower() for part in parts if part.strip()]


def infer_tags(additional_preferences: List[str]) -> List[str]:
    joined = " ".join(additional_preferences).lower()
    tags: List[str] = []
    for tag, keywords in TAG_KEYWORDS.items():
        if any(keyword in joined for keyword in keywords):
            tags.append(tag)
    return tags

