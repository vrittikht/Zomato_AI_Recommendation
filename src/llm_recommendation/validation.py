"""Validation and parsing for LLM structured outputs."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Tuple


class LLMOutputValidationError(ValueError):
    pass


def _ensure_dict(value: Any) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise LLMOutputValidationError("Output must be a JSON object.")
    return value


def _ensure_list(value: Any, field: str) -> List[Any]:
    if not isinstance(value, list):
        raise LLMOutputValidationError(f"Field '{field}' must be a list.")
    return value


def parse_llm_json(text: str) -> Dict[str, Any]:
    # Strip markdown code blocks if present
    content = text.strip()
    if content.startswith("```"):
        # Find first {
        start_idx = content.find("{")
        # Find last }
        end_idx = content.rfind("}")
        if start_idx != -1 and end_idx != -1:
            content = content[start_idx : end_idx + 1]

    try:
        return _ensure_dict(json.loads(content))
    except json.JSONDecodeError as exc:
        raise LLMOutputValidationError("LLM output is not valid JSON.") from exc


def validate_recommendations(
    parsed: Dict[str, Any], allowed_names: List[str], top_k: int
) -> Tuple[List[Dict[str, Any]], str | None]:
    allowed_set = set(allowed_names)

    extra_keys = set(parsed.keys()) - {"recommendations", "summary"}
    if extra_keys:
        raise LLMOutputValidationError(f"Unexpected keys: {sorted(extra_keys)}")

    recs_raw = _ensure_list(parsed.get("recommendations"), "recommendations")
    if not recs_raw:
        raise LLMOutputValidationError("No recommendations returned.")

    if len(recs_raw) > top_k:
        recs_raw = recs_raw[:top_k]

    cleaned: List[Dict[str, Any]] = []
    used_names: set[str] = set()
    for item in recs_raw:
        if not isinstance(item, dict):
            raise LLMOutputValidationError("Each recommendation must be an object.")
        if set(item.keys()) != {"name", "explanation"}:
            raise LLMOutputValidationError(
                "Each recommendation must contain only 'name' and 'explanation'."
            )

        name = item.get("name")
        explanation = item.get("explanation")
        if not isinstance(name, str) or not name.strip():
            raise LLMOutputValidationError("Recommendation 'name' must be a non-empty string.")
        if not isinstance(explanation, str) or not explanation.strip():
            raise LLMOutputValidationError(
                "Recommendation 'explanation' must be a non-empty string."
            )

        name = name.strip()
        if name not in allowed_set:
            raise LLMOutputValidationError(f"Hallucinated restaurant name: {name}")
        if name in used_names:
            continue
        used_names.add(name)
        cleaned.append({"name": name, "explanation": explanation.strip()})

    summary = parsed.get("summary")
    if summary is not None and not isinstance(summary, str):
        raise LLMOutputValidationError("Field 'summary' must be a string or null.")
    summary = summary.strip() if isinstance(summary, str) else None

    return cleaned, summary

