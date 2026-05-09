"""Phase 3 service for preference capture and normalization."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

from .models import NormalizedUserPreferencePayload, RawUserPreferenceInput
from .normalization import (
    extract_additional_preferences,
    infer_tags,
    normalize_budget,
    normalize_cuisine,
    normalize_location,
    normalize_rating,
)
from .validator import validate_payload
from .validator import PreferenceValidationError


def load_allowed_locations(processed_dataset_path: Path) -> Iterable[str]:
    if not processed_dataset_path.exists():
        raise FileNotFoundError(
            f"Processed dataset not found: {processed_dataset_path}. "
            "Run Phase 2 first to generate it."
        )

    df = pd.read_csv(processed_dataset_path, usecols=["location"])
    return sorted(df["location"].dropna().astype(str).str.title().unique().tolist())


def build_preference_payload(
    raw_input: RawUserPreferenceInput, allowed_locations: Iterable[str]
) -> NormalizedUserPreferencePayload:
    normalized_location = normalize_location(raw_input.location, allowed_locations)
    normalized_budget = normalize_budget(raw_input.budget)
    normalized_rating = normalize_rating(raw_input.minimum_rating)
    additional_preferences = extract_additional_preferences(
        raw_input.additional_preferences
    )

    input_errors = []
    if raw_input.location and normalized_location is None:
        input_errors.append("Unsupported location. Please provide a valid location.")
    if raw_input.budget and normalized_budget is None:
        input_errors.append(
            "Invalid budget. Allowed values map to low/medium/high."
        )
    if raw_input.minimum_rating not in (None, "") and normalized_rating is None:
        input_errors.append("Invalid minimum_rating. Provide a number between 0 and 5.")
    if input_errors:
        raise PreferenceValidationError(" | ".join(input_errors))

    payload = NormalizedUserPreferencePayload(
        location=normalized_location,
        budget=normalized_budget,
        cuisine=normalize_cuisine(raw_input.cuisine),
        minimum_rating=normalized_rating,
        additional_preferences=additional_preferences,
        inferred_tags=infer_tags(additional_preferences),
    )
    validate_payload(payload)
    return payload

