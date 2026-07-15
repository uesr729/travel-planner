# Run this script to fix budget-aware cost allocation
# Usage: python fix_budget.py

import os, re

base = r"C:\Users\A2529\Downloads\travel-planner"
path = os.path.join(base, "travel_planner", "services", "mock_data.py")

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# ---- ADD 1: budget tier helper function ----
tier_helper = '''

def _get_budget_tier(budget: int, days: int) -> str:
    """Determine budget tier based on daily per-person budget.
    
    Returns one of: "budget", "comfort", "luxury"
    """
    daily = budget / max(1, days)
    if daily < 200:
        return "budget"
    elif daily < 500:
        return "comfort"
    else:
        return "luxury"
'''

# Insert before generate_mock_itinerary
content = content.replace(
    '\n\ndef generate_mock_itinerary(',
    tier_helper + '\n\ndef generate_mock_itinerary('
)

# ---- ADD 2: budget-aware cost selection ----
# Find: city_data = _build_city_data_with_real_poi(destination)
# After that block, add tier-based filtering

old_block = '''    city_data = _build_city_data_with_real_poi(destination)

    # Select and distribute spots
    selected_spots = _select_spots(city_data, preferences, days)'''

new_block = '''    city_data = _build_city_data_with_real_poi(destination)

    # Budget-aware cost selection: filter restaurants and accommodations by tier
    tier = _get_budget_tier(budget, days)
    if tier == "budget":
        city_data["restaurants"] = [r for r in city_data["restaurants"] if r["cost"] <= 50]
        city_data["accommodations"] = [a for a in city_data["accommodations"] if a["cost"] <= 250]
    elif tier == "comfort":
        city_data["restaurants"] = [r for r in city_data["restaurants"] if 30 <= r["cost"] <= 150]
        city_data["accommodations"] = [a for a in city_data["accommodations"] if 200 <= a["cost"] <= 400]
    else:  # luxury
        city_data["restaurants"] = [r for r in city_data["restaurants"] if r["cost"] >= 80]
        city_data["accommodations"] = [a for a in city_data["accommodations"] if a["cost"] >= 300]

    # Select and distribute spots
    selected_spots = _select_spots(city_data, preferences, days)'''

content = content.replace(old_block, new_block)

# ---- SAVE ----
with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("mock_data.py updated with budget-aware cost allocation")
print("Budget tiers: budget (<200/day), comfort (200-500/day), luxury (>500/day)")
