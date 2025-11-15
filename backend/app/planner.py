# backend/app/planner.py
from .schemas import TripRequest, TripPlan, DayPlan, Place
from ..retrieval import (
    load_pois,
    filter_pois_by_category,
    top_popular_pois,
    as_records,
)
_ALL_POIS = load_pois()

def dummy_plan(req: TripRequest) -> TripPlan:
    """
    Simple planner that uses retrieval:
    - Filter POIs by city
    - If categories provided: filter by categories
    - If no categories: return top popular POIs
    """

    city = (req.city or "newyork").lower()


    categories = getattr(req, "categories", None) or []


    pois = _ALL_POIS[_ALL_POIS["city_name"].str.lower() == city]


    if categories:
        pois = filter_pois_by_category(pois, categories)
    else:
     
        pois = top_popular_pois(pois, k=5)

  
    records = as_records(pois)

   
    places = [
        Place(
            name=r["place_name"],
            category=r["place_category"],
        )
        for r in records
    ]


    day1 = DayPlan(
        day=1,
        places=places,
    )

    return TripPlan(city=city, days=[day1])

