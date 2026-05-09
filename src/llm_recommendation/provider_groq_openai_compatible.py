"""Groq (OpenAI-compatible) chat-completions provider (optional).

Groq provides an OpenAI-compatible API surface. We use Chat Completions:
`POST /openai/v1/chat/completions`

Env vars:
- GROQ_API_KEY (required to call Groq)
- GROQ_BASE_URL (optional; default: https://api.groq.com)
- GROQ_MODEL (optional; default: llama-3.1-8b-instant)
"""

from __future__ import annotations

import os
from typing import Optional

import requests


class GroqProviderError(RuntimeError):
    pass


def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    value = os.getenv(name)
    return value if value else default


def is_configured() -> bool:
    return bool(_env("GROQ_API_KEY"))


def generate_json(prompt: str, timeout_s: int = 30) -> str:
    api_key = _env("GROQ_API_KEY")
    if not api_key:
        raise GroqProviderError("GROQ_API_KEY is not set.")

    base_url = _env("GROQ_BASE_URL", "https://api.groq.com").rstrip("/")
    model = _env("GROQ_MODEL", "llama-3.1-8b-instant")

    # Groq OpenAI-compatible endpoint path includes /openai/v1
    url = f"{base_url}/openai/v1/chat/completions"
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
        raise GroqProviderError(f"Request failed: {exc}") from exc

    if resp.status_code >= 400:
        raise GroqProviderError(f"HTTP {resp.status_code}: {resp.text[:500]}")

    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"]
    except Exception as exc:  # noqa: BLE001
        raise GroqProviderError("Unexpected response format from Groq provider.") from exc

