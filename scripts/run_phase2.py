"""Entry script for Phase 2 data ingestion and preparation."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from data_ingestion.pipeline import run_phase_2_pipeline


def main() -> None:
    stats = run_phase_2_pipeline()
    print("Phase 2 pipeline completed successfully.")
    print(f"Raw rows: {stats.raw_rows}")
    print(f"Processed rows: {stats.processed_rows}")
    print(f"Duplicates removed: {stats.duplicates_removed}")
    print(f"Dropped missing-required rows: {stats.dropped_missing_required}")


if __name__ == "__main__":
    main()
