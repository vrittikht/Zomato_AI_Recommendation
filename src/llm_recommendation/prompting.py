"""Prompt templates and builders for Phase 5."""

from __future__ import annotations

import json
from typing import Any, Dict, List


def build_recommendation_prompt(
    user_preferences: Dict[str, Any],
    shortlisted_candidates: List[Dict[str, Any]],
    top_k: int,
) -> str:
    """
    Build a prompt that forces grounded, structured output.
    The model MUST only choose restaurants from the shortlist.
    """

    output_schema = {
        "recommendations": [
            {
                "name": "string",
                "explanation": "string (1-2 sentences, grounded in preferences and restaurant attributes)",
            }
        ],
        "summary": "string (optional, 1-2 sentences) OR null",
    }

    instructions = {
        "task": "Rank and recommend restaurants from the provided shortlist.",
        "constraints": [
            "ONLY recommend restaurants that appear in the shortlist exactly by name.",
            f"Return exactly {top_k} recommendations if possible; otherwise return as many as available.",
            "Explanations must reference user preferences (location/budget/cuisine/min rating/additional preferences) and restaurant attributes (rating/cost/cuisines).",
            "Return STRICT JSON that matches the schema. No markdown. No extra keys.",
        ],
        "output_schema": output_schema,
    }

    payload = {
        "instructions": instructions,
        "user_preferences": user_preferences,
        "shortlist": shortlisted_candidates,
    }

    return (
        "You are a recommendation engine.\n"
        "Use the following JSON input and produce a JSON output.\n\n"
        f"INPUT:\n{json.dumps(payload, ensure_ascii=False)}\n"
    )

