"""Main FastAPI application."""

import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from llm_recommendation.dotenv_loader import load_env_file
from api.routes import router
from data_ingestion.pipeline import run_phase_2_pipeline
from data_ingestion.config import PROCESSED_OUTPUT_PATH

# Load environment before anything else
load_env_file(PROJECT_ROOT / ".env")

app = FastAPI(
    title="Zomato AI Recommendation API",
    description="Backend service for AI-powered restaurant recommendations.",
    version="1.0.0"
)

# Enable CORS for frontend integration
frontend_url = os.getenv("FRONTEND_URL", "*")
origins = [frontend_url] if frontend_url != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True if frontend_url != "*" else False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Ensure data is ingested and processed on startup."""
    print(f"Current working directory: {os.getcwd()}")
    print(f"Looking for dataset at: {PROCESSED_OUTPUT_PATH.absolute()}")
    
    if not PROCESSED_OUTPUT_PATH.exists():
        print(f"Dataset NOT found. Running ingestion pipeline...")
        try:
            run_phase_2_pipeline()
            print("Data ingestion completed successfully.")
        except Exception as e:
            print(f"CRITICAL: Error during data ingestion: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"Dataset found successfully.")

app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Welcome to Zomato AI API",
        "docs": "/docs",
        "status": "operational"
    }

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
