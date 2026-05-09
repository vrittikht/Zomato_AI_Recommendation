"""Configuration for Phase 2 ingestion and preprocessing."""

from pathlib import Path

DATASET_ID = "ManikaSaini/zomato-restaurant-recommendation"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_OUTPUT_PATH = PROJECT_ROOT / "data" / "raw" / "zomato_raw.csv"
PROCESSED_OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "zomato_processed.csv"
REPORT_OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "data_quality_report.txt"

REQUIRED_CANONICAL_COLUMNS = ["name", "location", "cuisine", "cost", "rating"]

# Canonical column mapping to absorb schema differences.
COLUMN_ALIASES = {
    "name": ["name", "restaurant_name", "res_name", "title"],
    "location": ["location", "city", "locality", "address"],
    "cuisine": ["cuisine", "cuisines", "food_type"],
    "cost": [
        "cost",
        "average_cost",
        "cost_for_two",
        "approx_cost(for two people)",
        "price",
    ],
    "rating": ["rating", "rate", "aggregate_rating", "user_rating", "stars"],
}

MAX_ALLOWED_NULL_RATE = 0.40
DEDUP_SUBSET = ["name", "location", "cuisine", "cost", "rating"]
