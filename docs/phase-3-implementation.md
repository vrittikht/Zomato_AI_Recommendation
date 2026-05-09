# Phase 3 Implementation (User Preference Capture Layer)

This document describes the implemented Phase 3 components from
`docs/phase-wise-architecture.md`.

## Implemented in Separate Folder

- `src/preference_capture/`
  - `models.py`: raw and normalized preference data models
  - `normalization.py`: normalization utilities for location, budget, cuisine, rating
  - `validator.py`: payload validation rules and custom validation error
  - `service.py`: orchestration service for building final structured payload

## Entry Script

- `scripts/run_phase3.py`
  - Loads allowed locations from Phase 2 processed data
  - Accepts sample raw input
  - Produces normalized + validated preference payload
  - Exports sample payload to:
    - `data/processed/sample_preference_payload.json`

## Implemented Validation and Normalization Rules

- Input must include at least one meaningful field among:
  - `location`, `budget`, `cuisine`
- Rating is normalized to numeric and validated in range `0-5`
- Budget synonyms mapped to canonical classes:
  - `low`, `medium`, `high`
- Location supports fuzzy matching against known dataset locations
- Additional preferences are tokenized and converted to inferred tags

## Run Command

```bash
python scripts/run_phase3.py
```

## Expected Output

- Console output of normalized payload
- Persisted sample structured payload JSON for downstream Phase 4 retrieval
