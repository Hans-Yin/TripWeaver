# backend/app/google_places.py
import os
import requests

API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")


def map_google_types_to_category(types: list) -> str:
    if not types:
        return ""
    mapping = {
        "museum": "museum",
        "park": "park",
        "tourist_attraction": "landmark",
        "restaurant": "food",
        "cafe": "food",
        "meal_takeaway": "food",
        "shopping_mall": "shopping",
    }
    for t in types:
        if t in mapping:
            return mapping[t]
    return ""


def search_places(query: str, city: str, country: str = "") -> list[dict]:
    """Call Google Places Text Search API and normalize results into our POI schema."""
    if API_KEY is None:
        raise ValueError("Missing GOOGLE_PLACES_API_KEY")

    url = (
        "https://maps.googleapis.com/maps/api/place/textsearch/json"
        f"?query={query}+in+{city}&key={API_KEY}"
    )
    resp = requests.get(url)
    data = resp.json()

    pois: list[dict] = []
    for item in data.get("results", []):
        location = item["geometry"]["location"]
        poi = {
            "city_name": city,
            "place_name": item.get("name", ""),
            "country": country or "",
            "place_category": map_google_types_to_category(item.get("types", [])),
            "price": item.get("price_level", None),
            "open_time": None,
            "close_time": None,
            "popularity_score": item.get("rating", 0),
            "lat": location.get("lat"),
            "lon": location.get("lng"),
        }
        pois.append(poi)

    return pois
