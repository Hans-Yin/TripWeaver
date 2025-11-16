# backend/debug_query.py
"""Debug script to trace food and landmarks query"""

from app.parser import parse_query
from app.schemas import TripRequest
from app.planner import dummy_plan
from app.retrieval import load_pois

query = "food and landmarks in New York for 2 days"
print(f"Query: {query}\n")

# Step 1: Test parser
print("=" * 60)
print("STEP 1: Parse query")
print("=" * 60)
parsed = parse_query(query)
print(f"Categories: {parsed.categories}")
print(f"Explicit categories: {parsed.explicit_categories}")
print(f"City: {parsed.city}")
print(f"Days: {parsed.days}\n")

# Step 2: Load POIs and check what's in dataset
print("=" * 60)
print("STEP 2: Check POI dataset")
print("=" * 60)
pois = load_pois()
print(f"Total POIs in dataset: {len(pois)}")
print(f"Unique cities: {pois['city_name'].unique().tolist()}")
print(f"Unique categories: {pois['place_category'].unique().tolist()}\n")

# Step 3: Filter by city
print("=" * 60)
print("STEP 3: Filter by city (substring match)")
print("=" * 60)
city_key = parsed.city.lower().replace(" ", "").strip()
ny_pois = pois[pois["city_name"].str.lower().str.contains(city_key, na=False)]
print(f"POIs containing '{city_key}': {len(ny_pois)}")
if len(ny_pois) > 0:
    print(f"Cities found: {ny_pois['city_name'].unique().tolist()}")
    print(f"Categories in NY: {ny_pois['place_category'].unique().tolist()}")
    print("\nNY POIs:")
    for idx, row in ny_pois.iterrows():
        print(f"  - {row['place_name']} ({row['place_category']})")
print()

# Step 4: Filter by categories
print("=" * 60)
print("STEP 4: Filter by categories")
print("=" * 60)
print(f"Looking for categories: {parsed.categories}")
if parsed.categories:
    cats = {c.lower() for c in parsed.categories}
    print(f"Normalized category set: {cats}")
    matching = ny_pois[ny_pois["place_category"].str.lower().isin(cats)]
    print(f"Matching POIs: {len(matching)}")
    if len(matching) > 0:
        print("Matching POIs:")
        for idx, row in matching.iterrows():
            print(f"  - {row['place_name']} ({row['place_category']})")
print()

# Step 5: Run full planner
print("=" * 60)
print("STEP 5: Run full planner")
print("=" * 60)
req = TripRequest(query=query)
trip_plan = dummy_plan(req)
print(f"City: {trip_plan.city}")
print(f"Days: {len(trip_plan.days)}")
for day in trip_plan.days:
    print(f"\nDay {day.day}: {len(day.places)} places")
    for place in day.places:
        print(f"  - {place.name} ({place.category})")
