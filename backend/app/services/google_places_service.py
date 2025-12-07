import requests
import os

API_KEY=os.getenv("GOOGLE_PLACES_API_KEY")
def map_google_types_to_category(types:list)-> str:
  if not types:
    return ""
  mapping={
    "museum":"museum",
    "park":"park",
    "tourist_attraction": "landmark",
    "restaurant": "food",
    "cafe": "food",
    "meal_takeaway": "food",
    "shopping_mall": "shopping",

  }
  for i in types:
     if i in mapping:
       return mapping[i]
  return ""

def search_places(query:str,city:str，country: str=""):
  #call the google places api
  if API_KEY is None:
    raise ValueError("Missing API key")
  url = (
        "https://maps.googleapis.com/maps/api/place/textsearch/json"
        f"?query={query}+in+{city}&key={API_KEY}"
    )
  response=requests.get(url).json()

  pois=[]
  for i in response.get("results",[]):
    location=i["geometry"]["location"]
    poi={"city_name": city,
            "place_name": i.get("name", ""),
            "country": country if country else "",
            "place_category": map_google_types_to_category(i.get("types", [])),
            "price": i.get("price_level", None),
            "open_time": None,
            "close_time": None,
            "popularity_score": i.get("rating", 0),
            "lat": location.get("lat"),
            "lon": location.get("lng"),}
    pois.append(poi)

    return pois
            
