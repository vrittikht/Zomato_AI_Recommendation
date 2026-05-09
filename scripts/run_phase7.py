"""Start the Phase 7 Backend API."""

import sys
from pathlib import Path
import uvicorn

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

def main():
    print("🚀 Starting Zomato AI Backend API...")
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
