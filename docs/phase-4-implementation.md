# Phase 4 Implementation (Candidate Retrieval Layer)

This file documents the Phase 4 implementation from
`docs/phase-wise-architecture.md`.

## Implemented in Separate Folder

- `src/candidate_retrieval/`
  - `models.py`: candidate and retrieval result models
  - `scoring.py`: budget fit and composite scoring logic
  - `service.py`: deterministic filtering, optional relaxation, ranking, top-N selection

## Retrieval Logic Implemented

- Applies hard filters on:
  - location
  - cuisine
  - minimum rating
- If strict filter returns zero rows:
  - applies relaxed fallback (keeps location, lowers rating threshold by 0.5, relaxes cuisine)
- Scores each candidate with weighted composite scoring:
  - rating: 40%
  - location match: 25%
  - cuisine match: 20%
  - budget fit: 15%
- Produces deterministic top-N shortlist

## Entry Script

- `scripts/run_phase4.py`
  - reads:
    - `data/processed/zomato_processed.csv` (Phase 2)
    - `data/processed/sample_preference_payload.json` (Phase 3)
  - writes:
    - `data/processed/shortlisted_candidates.json`

## Run Command

```bash
python scripts/run_phase4.py
```

## Output Structure

- total records considered
- filtered record count
- whether fallback relaxation was applied
- shortlisted candidates with:
  - name
  - location
  - cuisine
  - cost
  - rating
  - score
  - match flags
