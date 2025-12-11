# backend/app/schemas.py
from typing import List, Optional
from pydantic import BaseModel

class TripRequest(BaseModel):
    query: str
    days: int = 1
    city: Optional[str] = None
    data_source: str = "offline"  # "offline" or "google"
    max_places_per_day: Optional[int] = None
    pace: Optional[str] = None  # e.g. "relaxed" | "standard" | "packed"


class ParsedTripRequest(BaseModel):
    query: str
    categories: List[str]
    explicit_categories: bool = False
    city: str
    days: int = 1


class Place(BaseModel):
    name: str
    category: str
    description: Optional[str] = None

class DayPlan(BaseModel):
    day: int
    places: List[Place]

class TripPlan(BaseModel):
    city: str
    days: List[DayPlan]
    explanation: Optional[str] = None
