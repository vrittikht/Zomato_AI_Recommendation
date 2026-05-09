"""Minimal .env loader to avoid extra dependencies.

This is intentionally simple:
- Loads KEY=VALUE lines
- Ignores comments and blank lines
- Does not override existing environment variables
"""

from __future__ import annotations

import os
from pathlib import Path


def load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')

        if not key:
            continue
        if key in os.environ and os.environ[key]:
            continue

        os.environ[key] = value

