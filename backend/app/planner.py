# backend/app/planner.py
from .schemas import TripRequest, TripPlan, DayPlan, Place
from .parser import parse_query
import sys
import os
import pandas as pd

# Add parent directory to path to import retrieval
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retrieval import (
    load_pois,
    filter_pois_by_category,
    top_popular_pois,
    as_records,
)


def dummy_plan(req: TripRequest) -> TripPlan:
    """
    Simple planner that uses retrieval and parser:
    - Parse the query to extract city, categories, and days
    - Filter POIs by city
    - If categories provided: filter by categories
    - If no categories: return top popular POIs
    - Distribute POIs across the requested days
    """
    
    # Parse the query to extract structured preferences
    parsed = parse_query(req.query)
    
    city = parsed.city.lower()
    # Use only categories explicitly mentioned in the query.
    # The parser sets `explicit_categories` to True when it found explicit tokens.
    explicit = getattr(parsed, "explicit_categories", False)
    categories = [c.lower() for c in (parsed.categories or [])]
    days_requested = parsed.days

    # Filter POIs by city. Use substring (case-insensitive) matching so variants
    # like 'New York City' or 'New York, NY' still match a query for 'New York'.
    # Load current POI dataset at request-time to pick up any normalization
    if city == "new york" or city == "nyc" or city == "NYC" or city == "New York" or city == "New York City":
        city_key = "newyork"
    else:
        city_key = city.strip().lower()
    pois_df = load_pois()
    pois = pois_df[pois_df["city_name"].str.lower().str.contains(city_key, na=False)]

    # Request POIs: 5 per day + buffer to account for distribution
    pois_needed = days_requested * 5 + 5
    
    # Only filter by category when the parser detected explicit categories.
    if explicit and categories:
        # Strict category filtering: only include POIs whose category was explicitly
        # mentioned in the query. Do NOT supplement with popular POIs of other
        # categories — that would introduce unwanted categories like 'shopping'.
        pois = filter_pois_by_category(pois, categories, top_k=pois_needed)
    else:
        pois = top_popular_pois(pois, top_k=pois_needed)

    # Convert to list of records
    records = as_records(pois)

    # Convert records to Place objects
    places = [
        Place(
            name=r["place_name"],
            category=r["place_category"],
        )
        for r in records
    ]

    # Distribute places across days.
    day_plans = []
    if len(places) == 0:
        # If no places found at all, fall back to top popular POIs for the city
        # and distribute those across requested days.
        all_pois_for_city = pois_df[pois_df["city_name"].str.lower().str.contains(city_key, na=False)]
        fallback = top_popular_pois(all_pois_for_city, top_k=pois_needed)
        records = as_records(fallback)
        places = [Place(name=r["place_name"], category=r["place_category"]) for r in records]

    # If explicit categories were requested but we have fewer matching places
    # than days, distribute existing matching places across the first (D-1)
    # days and fill the last day with top popular POIs (excluding already used places).
    if explicit and len(places) < days_requested and days_requested > 1:
        primary_days = days_requested - 1
        per_day_base = len(places) // primary_days
        remainder = len(places) % primary_days
        idx = 0
        for day_num in range(1, primary_days + 1):
            take = per_day_base + (1 if day_num <= remainder else 0)
            day_places = places[idx: idx + take]
            idx += take
            day_plans.append(DayPlan(day=day_num, places=day_places))

        # Prepare supplemental POIs for the last day: top popular in city excluding already used
        used_names = {p.name.lower() for p in places}
        all_pois_for_city = pois_df[pois_df["city_name"].str.lower().str.contains(city_key, na=False)]
        supplemental_df = top_popular_pois(all_pois_for_city, top_k=pois_needed * 2)
        supp_records = as_records(supplemental_df)
        supplemental_places = []
        for r in supp_records:
            if r["place_name"].lower() in used_names:
                continue
            supplemental_places.append(Place(name=r["place_name"], category=r["place_category"]))
            if len(supplemental_places) >= max(1, per_day_base or 1):
                break

        day_plans.append(DayPlan(day=days_requested, places=supplemental_places))
        return TripPlan(city=city, days=day_plans)

    # Otherwise distribute places evenly across the requested days
    days_to_return = days_requested
    per_day_base = len(places) // days_to_return
    remainder = len(places) % days_to_return
    idx = 0
    for day_num in range(1, days_to_return + 1):
        take = per_day_base + (1 if day_num <= remainder else 0)
        day_places = places[idx: idx + take]
        idx += take
        day_plans.append(DayPlan(day=day_num, places=day_places))

    return TripPlan(city=city, days=day_plans)

