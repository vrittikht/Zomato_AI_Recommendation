"""API routes for Phase 7."""

from fastapi import APIRouter, HTTPException
from pathlib import Path
import json

from .models import RecommendationRequest, RecommendationResponse, RecommendationItem

# Import existing services
from preference_capture.models import RawUserPreferenceInput
from preference_capture.service import build_preference_payload, load_allowed_locations
from candidate_retrieval.service import retrieve_top_candidates
from llm_recommendation.service import generate_recommendations

router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "zomato_processed.csv"
TEMP_DIR = PROJECT_ROOT / "data" / "processed" / "api_temp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    try:
        # 1. Phase 3: Preference Capture & Normalization
        allowed_locs = load_allowed_locations(DATASET_PATH)
        raw = RawUserPreferenceInput(
            location=request.location,
            budget=request.budget,
            cuisine=request.cuisine,
            minimum_rating=request.rating,
            additional_preferences=request.additional_preferences
        )
        payload = build_preference_payload(raw, allowed_locs)
        
        # Save payload to temp file
        pref_path = TEMP_DIR / "current_prefs.json"
        pref_path.write_text(json.dumps(payload.to_dict()), encoding="utf-8")

        # 2. Phase 4: Candidate Retrieval
        shortlist = retrieve_top_candidates(
            processed_dataset_path=DATASET_PATH,
            preference_payload_path=pref_path,
            top_n=max(15, request.top_k)
        )
        shortlist_path = TEMP_DIR / "current_shortlist.json"
        
        # Manually create dict for RetrievalResult
        shortlist_dict = {
            "total_records": shortlist.total_records,
            "filtered_records": shortlist.filtered_records,
            "shortlisted_count": shortlist.shortlisted_count,
            "relaxation_applied": shortlist.relaxation_applied,
            "shortlisted_candidates": [c.to_dict() for c in shortlist.shortlisted_candidates]
        }
        shortlist_path.write_text(json.dumps(shortlist_dict), encoding="utf-8")

        # 3. Phase 5: LLM Recommendation
        response = generate_recommendations(
            preference_payload_path=pref_path,
            shortlisted_candidates_path=shortlist_path,
            top_k=request.top_k
        )

        # 4. Map to API response model
        items = [
            RecommendationItem(
                name=r.name,
                location=r.location,
                cuisine=r.cuisine,
                rating=r.rating,
                cost=r.cost,
                explanation=r.explanation
            ) for r in response.recommendations
        ]

        return RecommendationResponse(
            recommendations=items,
            summary=response.summary,
            used_fallback=response.used_fallback
        )

    except Exception as e:
        # In production, log the full error stack
        raise HTTPException(status_code=500, detail=str(e))
