"""Validation rules for user preference payload."""

from __future__ import annotations

from typing import List

from .models import NormalizedUserPreferencePayload


class PreferenceValidationError(Exception):
    """Raised when normalized preferences fail validation."""


def validate_payload(payload: NormalizedUserPreferencePayload) -> None:
    errors: List[str] = []

    if not any([payload.location, payload.budget, payload.cuisine]):
        errors.append(
            "At least one of location, budget, or cuisine must be provided."
        )

    if payload.minimum_rating is not None:
        if payload.minimum_rating < 0 or payload.minimum_rating > 5:
            errors.append("minimum_rating must be between 0 and 5.")

    if errors:
        raise PreferenceValidationError(" | ".join(errors))

