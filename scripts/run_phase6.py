"""Entry script for Phase 6 Response Presentation Layer."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from response_presentation.service import present_recommendations

RECOMMENDATIONS_PATH = PROJECT_ROOT / "data" / "processed" / "final_recommendations.json"
if len(sys.argv) > 1:
    RECOMMENDATIONS_PATH = Path(sys.argv[1]).resolve()

HTML_OUTPUT_PATH = PROJECT_ROOT / "docs" / "recommendation_report.html"

def main():
    print("Starting Phase 6: Response Presentation...")
    try:
        present_recommendations(
            final_recommendations_path=RECOMMENDATIONS_PATH,
            output_html_path=HTML_OUTPUT_PATH
        )
        print("Phase 6 completed successfully.")
    except Exception as e:
        print(f"Error in Phase 6: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
