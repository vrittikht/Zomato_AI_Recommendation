"""OpenAI-compatible chat-completions provider (optional).

This module is optional at runtime:
- If no API key is set, Phase 5 will use deterministic fallback.

Env vars:
- OPENAI_API_KEY (required to call API)
- OPENAI_BASE_URL (optional; default: https://api.openai.com)
- OPENAI_MODEL (optional; default: gpt-4o-mini)
"""

from __future__ import annotations

import os
from typing import Optional

import requests


class LLMProviderError(RuntimeError):
    pass


def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    value = os.getenv(name)
    return value if value else default


def is_configured() -> bool:
    return bool(_env("OPENAI_API_KEY"))


def generate_json(prompt: str, timeout_s: int = 30) -> str:
    api_key = _env("OPENAI_API_KEY")
    if not api_key:
        raise LLMProviderError("OPENAI_API_KEY is not set.")

    base_url = _env("OPENAI_BASE_URL", "https://api.openai.com").rstrip("/")
    model = _env("OPENAI_MODEL", "gpt-4o-mini")

    url = f"{base_url}/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": "Return only valid JSON."},
            {"role": "user", "content": prompt},
        ],
    }

    try:
        resp = requests.post(url, headers=headers, json=body, timeout=timeout_s)
    except requests.RequestException as exc:
        raise LLMProviderError(f"Request failed: {exc}") from exc

    if resp.status_code >= 400:
        raise LLMProviderError(f"HTTP {resp.status_code}: {resp.text[:500]}")

    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"]
    except Exception as exc:  # noqa: BLE001
        raise LLMProviderError("Unexpected response format from provider.") from exc

