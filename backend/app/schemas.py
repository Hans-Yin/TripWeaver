# backend/app/schemas.py
from typing import List, Optional
from pydantic import BaseModel

class TripRequest(BaseModel):
    query: str
    days: int = 1
    city: Optional[str] = None

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
