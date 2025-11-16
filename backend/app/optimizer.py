# backend/app/optimizer.py
from __future__ import annotations
from typing import List
from .schemas import ParsedTripRequest
from .retrieval import as_records
from math import radians, sin, cos, asin, sqrt

def _haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    from math import radians, sin, cos, asin, sqrt
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

def score_record(rec: dict, prefs: ParsedTripRequest) -> float:
    """
    Simple scoring:
    - base = popularity_score
    - +0.2 if category matches user preference
    """
    score = float(rec.get("popularity_score", 0.0))

    cat = str(rec.get("place_category", "")).lower()
    if cat in [c.lower() for c in (prefs.categories or [])]:
        score += 0.2

    return score

def select_pois_greedy(pois_df, prefs: ParsedTripRequest, pois_needed: int):
    """
    Greedy selection:
    1. DataFrame -> records
    2. For each record: compute score
    3. Sort by score desc
    4. Take top `pois_needed`
    """
    records = as_records(pois_df)
    scored = sorted(records, key=lambda r: score_record(r, prefs), reverse=True)
    return scored[:pois_needed]
