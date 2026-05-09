"""Phase 5 service: LLM-based ranking + explanations with fallback."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .fallback import fallback_recommendations
from .models import RecommendationItem, RecommendationResponse
from .prompting import build_recommendation_prompt
from .provider_groq_openai_compatible import (
    GroqProviderError,
    generate_json as groq_generate_json,
    is_configured as is_groq_configured,
)
from .provider_openai_compatible import (
    LLMProviderError,
    generate_json as openai_generate_json,
    is_configured as is_openai_configured,
)
from .validation import LLMOutputValidationError, parse_llm_json, validate_recommendations


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _index_candidates_by_name(candidates: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    indexed: Dict[str, Dict[str, Any]] = {}
    for c in candidates:
        name = str(c.get("name", "")).strip()
        if name and name not in indexed:
            indexed[name] = c
    return indexed


def generate_recommendations(
    preference_payload_path: Path,
    shortlisted_candidates_path: Path,
    top_k: int = 5,
) -> RecommendationResponse:
    prefs = _load_json(preference_payload_path)
    shortlist_doc = _load_json(shortlisted_candidates_path)
    candidates: List[Dict[str, Any]] = shortlist_doc.get("shortlisted_candidates", [])
    candidates = [c for c in candidates if isinstance(c, dict)]

    if not candidates:
        return RecommendationResponse(recommendations=[], summary=None, used_fallback=True)

    # Prefer Groq if configured; otherwise use OpenAI-compatible; else fallback.
    llm_kind: str | None = None
    if is_groq_configured():
        llm_kind = "groq"
    elif is_openai_configured():
        llm_kind = "openai"

    if llm_kind is None:
        return RecommendationResponse(
            recommendations=fallback_recommendations(candidates, prefs, top_k),
            summary="Recommendations generated using deterministic fallback (LLM not configured).",
            used_fallback=True,
        )

    indexed = _index_candidates_by_name(candidates)
    allowed_names = list(indexed.keys())
    prompt = build_recommendation_prompt(prefs, candidates, top_k=top_k)

    try:
        raw_text = (
            groq_generate_json(prompt)
            if llm_kind == "groq"
            else openai_generate_json(prompt)
        )
        parsed = parse_llm_json(raw_text)
        recs_clean, summary = validate_recommendations(parsed, allowed_names, top_k=top_k)
        items: List[RecommendationItem] = []
        for rec in recs_clean:
            c = indexed[rec["name"]]
            items.append(
                RecommendationItem(
                    name=str(c["name"]),
                    location=str(c["location"]),
                    cuisine=str(c["cuisine"]),
                    rating=float(c["rating"]),
                    cost=float(c["cost"]),
                    explanation=rec["explanation"],
                )
            )
        return RecommendationResponse(recommendations=items, summary=summary, used_fallback=False)
    except (
        GroqProviderError,
        LLMProviderError,
        LLMOutputValidationError,
        KeyError,
    ):
        # Any provider or formatting problem should degrade gracefully.
        return RecommendationResponse(
            recommendations=fallback_recommendations(candidates, prefs, top_k),
            summary="Recommendations generated using deterministic fallback (LLM response unavailable/invalid).",
            used_fallback=True,
        )

