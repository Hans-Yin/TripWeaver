# backend/app/schemas.py
from typing import List, Optional
from pydantic import BaseModel

class TripRequest(BaseModel):
    query: str
    days: int = 1
    city: Optional[str] = None
    data_source: str = "offline" # "offline" or "google"

class ParsedTripRequest(BaseModel):
    query: str
    categories: List[str]
    explicit_categories: bool = False
    city: str  # Required; parser raises ValueError if not detected
    days: int = 1

class Place(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    summary: Optional[str] = None  # Wikipedia summary

class DayPlan(BaseModel):
    day: int
    places: List[Place]

class TripPlan(BaseModel):
    city: str
    days: List[DayPlan]
