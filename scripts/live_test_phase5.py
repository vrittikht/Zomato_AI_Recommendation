"""Live end-to-end test for Phase 3 -> Phase 4 -> Phase 5.

Example:
  python scripts/live_test_phase5.py --location Bellandur --budget 2000 --rating 4.0 --top_k 5
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from llm_recommendation.dotenv_loader import load_env_file

from preference_capture.models import RawUserPreferenceInput
from preference_capture.service import build_preference_payload, load_allowed_locations
from candidate_retrieval.service import retrieve_top_candidates
from llm_recommendation.service import generate_recommendations


PROCESSED_DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "zomato_processed.csv"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--location", type=str, required=True)
    p.add_argument("--budget", type=str, required=True, help="Use: low/medium/high or synonyms (cheap/premium)")
    p.add_argument("--rating", type=str, required=True, help="Minimum rating, 0-5")
    p.add_argument("--cuisine", type=str, default=None)
    p.add_argument("--additional", type=str, default=None)
    p.add_argument("--top_k", type=int, default=5)
    return p.parse_args()


def main() -> None:
    # Load local env file if present (does not override real environment variables).
    load_env_file(PROJECT_ROOT / ".env")
    load_env_file(PROJECT_ROOT / ".env.example")

    args = parse_args()

    allowed_locations = load_allowed_locations(PROCESSED_DATASET_PATH)
    raw = RawUserPreferenceInput(
        location=args.location,
        budget=args.budget,
        cuisine=args.cuisine,
        minimum_rating=args.rating,
        additional_preferences=args.additional,
    )
    payload = build_preference_payload(raw, allowed_locations)

    # Save payload for traceability
    pref_path = PROJECT_ROOT / "data" / "processed" / "live_preference_payload.json"
    pref_path.parent.mkdir(parents=True, exist_ok=True)
    pref_path.write_text(json.dumps(payload.to_dict(), indent=2), encoding="utf-8")

    # Phase 4 shortlist
    shortlist = retrieve_top_candidates(
        processed_dataset_path=PROCESSED_DATASET_PATH,
        preference_payload_path=pref_path,
        top_n=max(15, args.top_k),
    )
    shortlist_path = PROJECT_ROOT / "data" / "processed" / "live_shortlisted_candidates.json"
    shortlist_path.write_text(
        json.dumps(
            {
                "total_records": shortlist.total_records,
                "filtered_records": shortlist.filtered_records,
                "shortlisted_count": shortlist.shortlisted_count,
                "relaxation_applied": shortlist.relaxation_applied,
                "shortlisted_candidates": [c.to_dict() for c in shortlist.shortlisted_candidates],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    # Phase 5 recommendations
    response = generate_recommendations(
        preference_payload_path=pref_path,
        shortlisted_candidates_path=shortlist_path,
        top_k=args.top_k,
    )
    out_path = PROJECT_ROOT / "data" / "processed" / "live_final_recommendations.json"
    out_path.write_text(json.dumps(response.to_dict(), indent=2), encoding="utf-8")

    print("Live Phase 5 test completed.")
    print(f"Used fallback: {response.used_fallback}")
    print(f"Saved: {out_path}")
    print(json.dumps(response.to_dict(), indent=2))


if __name__ == "__main__":
    main()

