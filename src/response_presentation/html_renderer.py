"""HTML renderer for restaurant recommendations with premium UI."""

from typing import Any, Dict, List

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zomato AI - Your Curated Recommendations</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #FF4D67;
            --secondary: #2D3142;
            --accent: #FFD166;
            --background: #0F111A;
            --card-bg: rgba(30, 34, 51, 0.7);
            --text-main: #FFFFFF;
            --text-muted: #A0AEC0;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Outfit', sans-serif;
            background-color: var(--background);
            background-image: 
                radial-gradient(at 0% 0%, hsla(350, 100%, 65%, 0.1) 0px, transparent 50%),
                radial-gradient(at 100% 0%, hsla(240, 100%, 65%, 0.1) 0px, transparent 50%);
            color: var(--text-main);
            line-height: 1.6;
            min-height: 100vh;
            padding: 40px 20px;
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}

        header {{
            text-align: center;
            margin-bottom: 60px;
            animation: fadeInDown 0.8s ease-out;
        }}

        h1 {{
            font-size: 3.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #FF4D67 0%, #FF8FA3 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
            letter-spacing: -1px;
        }}

        .summary {{
            font-size: 1.1rem;
            color: var(--text-muted);
            max-width: 600px;
            margin: 0 auto;
        }}

        .fallback-badge {{
            display: inline-block;
            margin-top: 15px;
            padding: 6px 12px;
            background: rgba(255, 209, 102, 0.1);
            color: var(--accent);
            border: 1px solid rgba(255, 209, 102, 0.3);
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }}

        .grid {{
            display: flex;
            flex-direction: column;
            gap: 25px;
        }}

        .card {{
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 24px;
            padding: 30px;
            display: flex;
            gap: 25px;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            animation: fadeInUp 0.6s ease-out both;
        }}

        .card:hover {{
            transform: translateY(-5px) scale(1.01);
            border-color: rgba(255, 77, 103, 0.3);
            background: rgba(35, 40, 61, 0.8);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }}

        .card-number {{
            flex-shrink: 0;
            width: 45px;
            height: 45px;
            background: linear-gradient(135deg, var(--primary), #FF8FA3);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 1.25rem;
            color: white;
            box-shadow: 0 10px 20px rgba(255, 77, 103, 0.3);
        }}

        .card-content {{
            flex-grow: 1;
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 8px;
        }}

        .restaurant-name {{
            font-size: 1.5rem;
            font-weight: 700;
            color: white;
        }}

        .rating-badge {{
            background: #4CC9F0;
            color: #0F111A;
            padding: 4px 10px;
            border-radius: 8px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 0.9rem;
        }}

        .restaurant-info {{
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            font-size: 0.9rem;
            color: var(--text-muted);
        }}

        .info-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}

        .explanation {{
            background: rgba(255, 255, 255, 0.03);
            border-left: 3px solid var(--primary);
            padding: 15px 20px;
            border-radius: 0 12px 12px 0;
            font-size: 1rem;
            color: #E2E8F0;
            position: relative;
        }}

        .explanation::before {{
            content: '“';
            position: absolute;
            left: -15px;
            top: -5px;
            font-size: 3rem;
            color: var(--primary);
            opacity: 0.3;
            font-family: serif;
        }}

        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        @keyframes fadeInDown {{
            from {{ opacity: 0; transform: translateY(-30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        @media (max-width: 600px) {{
            .card {{ flex-direction: column; gap: 15px; }}
            .card-header {{ flex-direction: column; gap: 10px; }}
            h1 {{ font-size: 2.5rem; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Zomato AI</h1>
            <p class="summary">{summary}</p>
            {fallback_html}
        </header>

        <div class="grid">
            {cards_html}
        </div>
    </div>
</body>
</html>
"""

def generate_html(data: Dict[str, Any]) -> str:
    recommendations: List[Dict[str, Any]] = data.get("recommendations", [])
    summary = data.get("summary", "Personalized recommendations crafted just for you.")
    used_fallback = data.get("used_fallback", False)

    fallback_html = '<div class="fallback-badge">Fallback Ranking Active</div>' if used_fallback else ""
    
    cards_list = []
    for i, rec in enumerate(recommendations, 1):
        card = f"""
            <div class="card" style="animation-delay: {i * 0.1}s">
                <div class="card-number">{i}</div>
                <div class="card-content">
                    <div class="card-header">
                        <h2 class="restaurant-name">{rec['name']}</h2>
                        <div class="rating-badge">
                            <span>⭐</span> {rec['rating']}
                        </div>
                    </div>
                    <div class="restaurant-info">
                        <div class="info-item">📍 {rec['location']}</div>
                        <div class="info-item">🍴 {rec['cuisine']}</div>
                        <div class="info-item">💰 ₹{rec['cost']} for two</div>
                    </div>
                    <div class="explanation">
                        {rec['explanation']}
                    </div>
                </div>
            </div>
        """
        cards_list.append(card)

    return HTML_TEMPLATE.format(
        summary=summary,
        fallback_html=fallback_html,
        cards_html="".join(cards_list)
    )

def save_report(html_content: str, output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
