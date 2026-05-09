"""Phase 6 service: Response presentation orchestration."""

from pathlib import Path
import json
from typing import Any, Dict

from .cli_renderer import render_to_console
from .html_renderer import generate_html, save_report

def present_recommendations(
    final_recommendations_path: Path,
    output_html_path: Path | None = None
) -> None:
    if not final_recommendations_path.exists():
        raise FileNotFoundError(f"Final recommendations not found at {final_recommendations_path}")

    with open(final_recommendations_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Render to Console
    render_to_console(data)

    # 2. Render to HTML if path provided
    if output_html_path:
        html_content = generate_html(data)
        save_report(html_content, str(output_html_path))
        print(f"✨ Premium HTML report generated at: {output_html_path}")
