# backend/tests/test_google_places.py
from backend.app.google_places import search_places

if __name__ == "__main__":
    pois = search_places("museum", "New York")
    print("Total POIs:", len(pois))
    for p in pois[:5]:
        print(p)
