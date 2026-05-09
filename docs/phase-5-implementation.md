# Phase 5 Implementation (LLM Recommendation Layer)

This file documents Phase 5 implementation from `docs/phase-wise-architecture.md`.

## Implemented in Separate Folder

- `src/llm_recommendation/`
  - `prompting.py`: prompt builder with strict JSON output constraints
  - `validation.py`: JSON parsing + schema validation + hallucination checks
  - `provider_openai_compatible.py`: optional OpenAI-compatible provider (env-based)
  - `fallback.py`: deterministic ranking + explanation fallback when LLM is unavailable
  - `service.py`: orchestration (LLM-first, fallback-on-failure)
  - `models.py`: recommendation response models

## Inputs (From Previous Phases)

- Phase 3 payload:
  - `data/processed/sample_preference_payload.json`
- Phase 4 shortlist:
  - `data/processed/shortlisted_candidates.json`

## Outputs

- Phase 5 final recommendations:
  - `data/processed/final_recommendations.json`

## Run Command

```bash
python scripts/run_phase5.py
```

## Optional LLM Configuration

### Option A (Recommended): Groq

Set environment variables:

- `GROQ_API_KEY` (required)
- `GROQ_MODEL` (optional, default: `llama-3.1-8b-instant`)
- `GROQ_BASE_URL` (optional, default: `https://api.groq.com`)

Groq uses an OpenAI-compatible endpoint at:
- `POST /openai/v1/chat/completions`

### Option B: OpenAI-Compatible API

Set environment variables:

- `OPENAI_API_KEY` (required)
- `OPENAI_MODEL` (optional, default: `gpt-4o-mini`)
- `OPENAI_BASE_URL` (optional, default: `https://api.openai.com`)

If neither Groq nor OpenAI is configured, the system automatically uses deterministic fallback.

## Reliability Behaviors Implemented

- Enforces model output to be **strict JSON** with expected keys only
- Blocks hallucinations by validating restaurant names against shortlist
- Degrades gracefully to deterministic fallback on:
  - provider error/timeouts
  - invalid JSON
  - schema mismatch
  - duplicate/unknown items
