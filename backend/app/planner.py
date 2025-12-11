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
from .llm_parser import llm_parse_to_parsed_trip_request
from .llm_explainer import build_itinerary_explanation

import pandas as pd


def dummy_plan(req: TripRequest) -> TripPlan:
    """
    Planner pipeline:
    1) parse query into ParsedTripRequest
    2) choose data source (offline CSV or Google Places)
    3) run greedy optimizer to select POIs
    4) distribute POIs across days
    """
    # 1) parse user query (heuristic)
    base_parsed = parse_query(req.query)

    # 1.1 optional: refine with LLM parser (fallback-safe)
    parsed = llm_parse_to_parsed_trip_request(req.query, base_parsed)

    # keep original days logic
    days_requested = parsed.days or 1

    pace_raw = getattr(req, "pace", None) or ""
    pace = pace_raw.strip().lower()

    # default values based on pace
    if pace in {"relax", "relaxed"}:
        default_max_per_day = 3
    elif pace == "packed":
        default_max_per_day = 7
    else:
        # "standard" or anything else → behave like original (~5 per day)
        default_max_per_day = 5

    # read explicit max_places_per_day if provided
    max_per_day = getattr(req, "max_places_per_day", None)
    try:
        max_per_day = int(max_per_day) if max_per_day is not None else None
    except Exception:
        max_per_day = None

    # if user didn't specify or invalid, fall back to pace-based default
    if max_per_day is None or max_per_day <= 0:
        max_per_day = default_max_per_day

    # total POIs we want
    pois_needed = days_requested * max_per_day

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

    # Hard cap: don't exceed days * max_per_day, even if optimizer returns more
    max_total = days_requested * max_per_day
    if max_total > 0 and len(records) > max_total:
        records = records[:max_total]

    # enrich with Wikipedia description
    places = []
    for r in records:
        wiki_text = get_poi_summary(r["place_name"], sentences=2)
        places.append(Place(
            name=r["place_name"],
            category=r["place_category"],
            description=wiki_text,
        ))

    # 5) distribute across days
    day_plans: list[DayPlan] = []

    if len(places) == 0:
        # offline fallback: if no places after greedy selection, use offline dataset
        all_pois_for_city = _pois_from_offline(parsed, pois_needed)
        fallback_records = select_pois_greedy(all_pois_for_city, parsed, pois_needed)

        # apply the same hard cap in fallback
        if max_total > 0 and len(fallback_records) > max_total:
            fallback_records = fallback_records[:max_total]

        places = []
        for r in fallback_records:
            wiki_text = get_poi_summary(r["place_name"], sentences=2)
            places.append(Place(
                name=r["place_name"],
                category=r["place_category"],
                description=wiki_text,
            ))

    # average distribution logic (unchanged)
    days_to_return = days_requested or 1
    per_day_base = len(places) // days_to_return
    remainder = len(places) % days_to_return
    idx = 0
    for day_num in range(1, days_to_return + 1):
        take = per_day_base + (1 if day_num <= remainder else 0)
        day_places = places[idx: idx + take]
        idx += take
        day_plans.append(DayPlan(day=day_num, places=day_places))

    # Build base TripPlan
    plan = TripPlan(city=parsed.city, days=day_plans)

    # Optional: LLM explanation layer (safe fallback)
    try:
        plan.explanation = build_itinerary_explanation(req, parsed, plan)
    except Exception as e:
        print(f"[LLM explainer] Failed to generate explanation: {e}")

    return plan


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
