"""CLI renderer for restaurant recommendations."""

import sys

# ANSI Color Codes
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
RESET = "\033[0m"

def render_to_console(data: dict) -> None:
    recommendations = data.get("recommendations", [])
    summary = data.get("summary", "")
    used_fallback = data.get("used_fallback", False)

    print("\n" + "="*60)
    print(f"{BOLD}{BLUE}🍽️  AI RESTAURANT RECOMMENDATIONS{RESET}")
    print("="*60)

    if summary:
        print(f"\n{BOLD}Summary:{RESET} {summary}")
    
    if used_fallback:
        print(f"\n{YELLOW}⚠️  Note: Generated using fallback ranking.{RESET}")

    for i, rec in enumerate(recommendations, 1):
        print(f"\n{BOLD}{GREEN}{i}. {rec['name']}{RESET}")
        print(f"   {BOLD}Location:{RESET} {rec['location']}")
        print(f"   {BOLD}Cuisine:{RESET} {rec['cuisine']}")
        print(f"   {BOLD}Rating:{RESET} ⭐ {rec['rating']} | {BOLD}Cost:{RESET} ₹{rec['cost']}")
        print(f"   {BOLD}Why?{RESET} {rec['explanation']}")

    print("\n" + "="*60 + "\n")
