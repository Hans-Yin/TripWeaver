# backend/app/planner.py
from .schemas import TripRequest, TripPlan, DayPlan, Place, ParsedTripRequest
from .parser import parse_query
from .optimizer import select_pois_greedy
from .retrieval import (
    load_pois,
    filter_pois_by_category,
    top_popular_pois,
    as_records,
)
from .google_places import search_places
from .wikipedia import get_poi_summary

import pandas as pd

# Add parent directory to path to import retrieval

from .retrieval import (
    load_pois,
    filter_pois_by_category,
    top_popular_pois,
    as_records,
)


def dummy_plan(req: TripRequest) -> TripPlan:
    """
    Planner pipeline:
    1) parse query into ParsedTripRequest
    2) choose data source (offline CSV or Google Places)
    3) run greedy optimizer to select POIs
    4) distribute POIs across days
    """
    # 1) parse user query
    parsed = parse_query(req.query)

    days_requested = parsed.days
    pois_needed = days_requested * 5 + 5

    # 2) choose data source
    data_source = getattr(req, "data_source", "offline").lower()
    if data_source == "google":
        pois_df = _pois_from_google(parsed, pois_needed)
    else:
        pois_df = _pois_from_offline(parsed, pois_needed)

    # 3) check if there are any POIs
    if pois_df is None or len(pois_df) == 0:
        return TripPlan(city=parsed.city, days=[])

    # 4) greedy selection
    records = select_pois_greedy(pois_df, parsed, pois_needed)
    places = []
    for r in records:
        # Try to fetch Wikipedia summary for the place
        summary = get_poi_summary(r["place_name"], sentences=2)
        places.append(Place(
            name=r["place_name"],
            category=r["place_category"],
            summary=summary
        ))

    # 5) distribute across days
    day_plans: list[DayPlan] = []

    if len(places) == 0:
        # offline fallback: if no places after greedy selection, use offline dataset
        all_pois_for_city = _pois_from_offline(parsed, pois_needed)
        fallback_records = select_pois_greedy(all_pois_for_city, parsed, pois_needed)
        places = []
        for r in fallback_records:
            summary = get_poi_summary(r["place_name"], sentences=2)
            places.append(Place(
                name=r["place_name"],
                category=r["place_category"],
                summary=summary
            ))

    # average distribution logic
    days_to_return = days_requested or 1
    per_day_base = len(places) // days_to_return
    remainder = len(places) % days_to_return
    idx = 0
    for day_num in range(1, days_to_return + 1):
        take = per_day_base + (1 if day_num <= remainder else 0)
        day_places = places[idx: idx + take]
        idx += take
        day_plans.append(DayPlan(day=day_num, places=day_places))

    return TripPlan(city=parsed.city, days=day_plans)


def _pois_from_offline(parsed: ParsedTripRequest, pois_needed: int) -> pd.DataFrame:
    """Use our offline CSV dataset to retrieve POIs for a city."""
    city = parsed.city.lower()

    # normalize city name
    if city in {"new york", "nyc", "new york city"}:
        city_key = "newyork"
    else:
        city_key = city.strip().lower()

    pois_df = load_pois()
    pois_for_city = pois_df[pois_df["city_name"].str.lower().str.contains(city_key, na=False)]

    explicit = getattr(parsed, "explicit_categories", False)
    categories = [c.lower() for c in (parsed.categories or [])]

    if explicit and categories:
        filtered_df = filter_pois_by_category(pois_for_city, categories, top_k=pois_needed * 2)
    else:
        filtered_df = top_popular_pois(pois_for_city, top_k=pois_needed * 2)

    return filtered_df


def _pois_from_google(parsed: ParsedTripRequest, pois_needed: int) -> pd.DataFrame:
    """Use Google Places API to retrieve POIs for a city."""
    city = parsed.city

    if parsed.categories:
        search_query = " ".join(parsed.categories)
    else:
        search_query = "tourist attractions"

    raw_pois = search_places(search_query, city)
    if not raw_pois:
        return pd.DataFrame(columns=[
            "city_name", "place_name", "country", "place_category",
            "price", "open_time", "close_time", "popularity_score",
            "lat", "lon"
        ])

    df = pd.DataFrame(raw_pois)
    return df

