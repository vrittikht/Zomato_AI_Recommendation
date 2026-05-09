"""Phase 2 pipeline: ingest, preprocess, validate, and persist data."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

import pandas as pd
from datasets import load_dataset

from .config import (
    COLUMN_ALIASES,
    DATASET_ID,
    DEDUP_SUBSET,
    MAX_ALLOWED_NULL_RATE,
    PROCESSED_OUTPUT_PATH,
    RAW_OUTPUT_PATH,
    REPORT_OUTPUT_PATH,
    REQUIRED_CANONICAL_COLUMNS,
)


@dataclass
class PipelineStats:
    raw_rows: int
    processed_rows: int
    duplicates_removed: int
    dropped_missing_required: int
    null_rates: Dict[str, float]


def _pick_first_existing_column(df: pd.DataFrame, candidates: List[str]) -> str | None:
    for column in candidates:
        if column in df.columns:
            return column
    return None


def map_to_canonical_columns(df: pd.DataFrame) -> pd.DataFrame:
    mapped = pd.DataFrame()

    for canonical_name, alias_candidates in COLUMN_ALIASES.items():
        selected_column = _pick_first_existing_column(df, alias_candidates)
        if selected_column is not None:
            mapped[canonical_name] = df[selected_column]
        else:
            mapped[canonical_name] = pd.NA

    return mapped


def _normalize_text(value: object) -> str | None:
    if pd.isna(value):
        return None

    cleaned = str(value).strip()
    if not cleaned or cleaned in {"-", "N/A", "nan", "None"}:
        return None
    return cleaned


def normalize_rating(value: object) -> float | None:
    text = _normalize_text(value)
    if text is None:
        return None

    match = re.search(r"\d+(\.\d+)?", text)
    if not match:
        return None

    numeric = float(match.group())
    if numeric > 5:
        return None
    return numeric


def normalize_cost(value: object) -> int | None:
    text = _normalize_text(value)
    if text is None:
        return None

    digits = re.sub(r"[^0-9]", "", text)
    if not digits:
        return None

    amount = int(digits)
    if amount <= 0:
        return None
    return amount


def preprocess(df: pd.DataFrame) -> Tuple[pd.DataFrame, PipelineStats]:
    canonical = map_to_canonical_columns(df)
    raw_rows = len(canonical)

    canonical["name"] = canonical["name"].map(_normalize_text)
    canonical["location"] = canonical["location"].map(_normalize_text).str.title()
    canonical["cuisine"] = canonical["cuisine"].map(_normalize_text).str.title()
    canonical["rating"] = canonical["rating"].map(normalize_rating)
    canonical["cost"] = canonical["cost"].map(normalize_cost)

    null_rates = {
        column: float(canonical[column].isna().mean())
        for column in REQUIRED_CANONICAL_COLUMNS
    }

    before_dedup = len(canonical)
    deduplicated = canonical.drop_duplicates(subset=DEDUP_SUBSET, keep="first")
    duplicates_removed = before_dedup - len(deduplicated)

    before_dropna = len(deduplicated)
    processed = deduplicated.dropna(subset=REQUIRED_CANONICAL_COLUMNS).reset_index(drop=True)
    dropped_missing_required = before_dropna - len(processed)

    stats = PipelineStats(
        raw_rows=raw_rows,
        processed_rows=len(processed),
        duplicates_removed=duplicates_removed,
        dropped_missing_required=dropped_missing_required,
        null_rates=null_rates,
    )
    return processed, stats


def validate_quality(stats: PipelineStats) -> None:
    null_violations = [
        column
        for column, rate in stats.null_rates.items()
        if rate > MAX_ALLOWED_NULL_RATE
    ]
    if null_violations:
        columns = ", ".join(null_violations)
        raise ValueError(
            f"Data quality check failed. Null-rate threshold exceeded for: {columns}"
        )

    if stats.processed_rows == 0:
        raise ValueError("Data quality check failed. No usable rows after preprocessing.")


def write_quality_report(stats: PipelineStats) -> None:
    REPORT_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "Phase 2 Data Quality Report",
        "===========================",
        f"Raw rows: {stats.raw_rows}",
        f"Processed rows: {stats.processed_rows}",
        f"Duplicates removed: {stats.duplicates_removed}",
        f"Rows dropped due to missing required fields: {stats.dropped_missing_required}",
        "",
        "Null rates (before dropping required-null rows):",
    ]
    for column, rate in stats.null_rates.items():
        lines.append(f"- {column}: {rate:.2%}")

    REPORT_OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")


def run_phase_2_pipeline() -> PipelineStats:
    print(f"Loading dataset: {DATASET_ID}")
    dataset = load_dataset(DATASET_ID)
    split_name = "train" if "train" in dataset else next(iter(dataset.keys()))
    df = dataset[split_name].to_pandas()

    RAW_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW_OUTPUT_PATH, index=False)

    processed_df, stats = preprocess(df)
    validate_quality(stats)

    PROCESSED_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    processed_df.to_csv(PROCESSED_OUTPUT_PATH, index=False)
    write_quality_report(stats)

    return stats
