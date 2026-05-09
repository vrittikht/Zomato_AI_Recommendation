"""Entry script for Phase 4 candidate retrieval."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from candidate_retrieval.service import retrieve_top_candidates

PROCESSED_DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "zomato_processed.csv"
PREFERENCE_PAYLOAD_PATH = PROJECT_ROOT / "data" / "processed" / "sample_preference_payload.json"
OUTPUT_SHORTLIST_PATH = PROJECT_ROOT / "data" / "processed" / "shortlisted_candidates.json"


def main() -> None:
    result = retrieve_top_candidates(
        processed_dataset_path=PROCESSED_DATASET_PATH,
        preference_payload_path=PREFERENCE_PAYLOAD_PATH,
        top_n=15,
    )

    output = {
        "total_records": result.total_records,
        "filtered_records": result.filtered_records,
        "shortlisted_count": result.shortlisted_count,
        "relaxation_applied": result.relaxation_applied,
        "shortlisted_candidates": [
            candidate.to_dict() for candidate in result.shortlisted_candidates
        ],
    }

    OUTPUT_SHORTLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_SHORTLIST_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print("Phase 4 candidate retrieval completed successfully.")
    print(f"Total records: {result.total_records}")
    print(f"Filtered records: {result.filtered_records}")
    print(f"Shortlisted count: {result.shortlisted_count}")
    print(f"Relaxation applied: {result.relaxation_applied}")
    print(f"Saved shortlist to: {OUTPUT_SHORTLIST_PATH}")


if __name__ == "__main__":
    main()

