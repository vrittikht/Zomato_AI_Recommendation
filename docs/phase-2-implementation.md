# Phase 2 Implementation (Data Ingestion and Preparation)

This file documents the implemented Phase 2 assets from `docs/phase-wise-architecture.md`.

## Implemented Components

- `src/data_ingestion/config.py`
  - Dataset ID
  - Canonical schema definitions
  - Column aliases for schema drift handling
  - Data quality thresholds and output paths

- `src/data_ingestion/pipeline.py`
  - Dataset loading from Hugging Face
  - Canonical column mapping
  - Normalization for text, rating, and cost
  - Duplicate removal
  - Required-field validation
  - Data quality checks
  - Raw/processed data export
  - Quality report generation

- `scripts/run_phase2.py`
  - Single command entrypoint for Phase 2

- `requirements.txt`
  - `datasets`
  - `pandas`

## Output Artifacts (Generated After Run)

- `data/raw/zomato_raw.csv`
- `data/processed/zomato_processed.csv`
- `data/processed/data_quality_report.txt`

## Run Instructions

From project root:

```bash
pip install -r requirements.txt
python scripts/run_phase2.py
```

## Quality Gates Enforced

- Required canonical fields must exist and be usable:
  - `name`, `location`, `cuisine`, `cost`, `rating`
- Null rate threshold on required fields:
  - max `40%` before required-null row dropping
- Processed dataset must contain at least one valid row
