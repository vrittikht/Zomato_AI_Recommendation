"""Entry script for Phase 5 LLM recommendation layer."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from llm_recommendation.dotenv_loader import load_env_file
from llm_recommendation.service import generate_recommendations

PREFERENCE_PAYLOAD_PATH = PROJECT_ROOT / "data" / "processed" / "sample_preference_payload.json"
SHORTLIST_PATH = PROJECT_ROOT / "data" / "processed" / "shortlisted_candidates.json"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "final_recommendations.json"


def main() -> None:
    # Load local env file if present (does not override real environment variables).
    load_env_file(PROJECT_ROOT / ".env")
    load_env_file(PROJECT_ROOT / "src" / ".env")

    response = generate_recommendations(
        preference_payload_path=PREFERENCE_PAYLOAD_PATH,
        shortlisted_candidates_path=SHORTLIST_PATH,
        top_k=5,
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(response.to_dict(), indent=2), encoding="utf-8")

    print("Phase 5 recommendation generation completed.")
    print(f"Used fallback: {response.used_fallback}")
    print(f"Saved recommendations to: {OUTPUT_PATH}")
    if response.summary:
        print(f"Summary: {response.summary}")


if __name__ == "__main__":
    main()

