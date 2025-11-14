# backend/app/planner.py
from .schemas import TripRequest, TripPlan, DayPlan, Place

def dummy_plan(req: TripRequest) -> TripPlan:
    """
    Placeholder planner for NYC:
    Will be replaced by the actual parsing + retrieval + planning logic later.
    """
    city = req.city or "New York"

    day1 = DayPlan(
        day=1,
        places=[
            Place(name="Times Square", category="landmark"),
            Place(name="Central Park", category="park"),
            Place(name="The Metropolitan Museum of Art", category="museum"),
            Place(name="Brooklyn Bridge", category="landmark"),
        ],
    )

    return TripPlan(city=city, days=[day1])
