"""Entry script for Phase 3 preference capture and validation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from preference_capture.models import RawUserPreferenceInput
from preference_capture.service import build_preference_payload, load_allowed_locations
from preference_capture.validator import PreferenceValidationError

PROCESSED_DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "zomato_processed.csv"
OUTPUT_SAMPLE_PATH = (
    PROJECT_ROOT / "data" / "processed" / "sample_preference_payload.json"
)


def main() -> None:
    allowed_locations = load_allowed_locations(PROCESSED_DATASET_PATH)

    sample_input = RawUserPreferenceInput(
        location="Banashankari",
        budget="cheap",
        cuisine="north indian",
        minimum_rating="4.0",
        additional_preferences="family-friendly, quick service",
    )

    try:
        payload = build_preference_payload(sample_input, allowed_locations)
    except PreferenceValidationError as error:
        print(f"Validation failed: {error}")
        sys.exit(1)

    OUTPUT_SAMPLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_SAMPLE_PATH.write_text(
        json.dumps(payload.to_dict(), indent=2), encoding="utf-8"
    )

    print("Phase 3 preference capture completed successfully.")
    print("Normalized payload:")
    print(json.dumps(payload.to_dict(), indent=2))
    print(f"Saved sample payload to: {OUTPUT_SAMPLE_PATH}")


if __name__ == "__main__":
    main()

